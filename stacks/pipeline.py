"""Module stacks.pipeline"""

from pathlib import Path
from pkg_resources import resource_filename

from aws_cdk import (
    core,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
)
from aws_cdk.pipelines import (
    CodeBuildOptions,
    CodeBuildStep,
    CodePipeline,
    CodePipelineSource,
    ManualApprovalStep
)

from . import SUBDIRECTORY_APPS_PIPELINE
from .alcf_ceilometer import Alcf_ceilometerStack
from .utils import consolidate_config, resolve_tags


class Alcf_ceilometerApplicationStage(core.Stage):
    """alcf_ceilometer application stage"""

    def __init__(
        self, scope, id, target_env, **kwargs
    ):  # pylint: disable=redefined-builtin
        """ Initializer """
        super().__init__(scope, id, **kwargs)

        Alcf_ceilometerStack(
            self,
            f"Alcf_ceilometerStack{target_env}",
            target_env,
        )


class Alcf_ceilometerPipelineStack(core.Stack):
    """Stack to deploy workflow resources for alcf_ceilometer"""

    @classmethod
    def load_config(cls, target_env: str) -> dict:
        """Loads the configuration for the given stack.

        Config file is located in configurations/<name of the class>.yaml.

        Args:
            target_env: The FR environment - Dev, PreProd, Prod - to work with.

        Returns:
            The load configuration for the given target_env.
        """
        return consolidate_config(
            resource_filename(__name__, f"configurations/{cls.__name__}.yaml"),
            target_env,
        )

    def __init__(
        self, app, id, target_env, **kwargs
    ):  # pylint: disable=redefined-builtin

        # For the given target environment, load the configuration
        self.config = self.load_config(target_env)

        self.target_env = target_env

        # Override description, stack_name and tags if they have been provided
        kwargs.update(
            dict(
                description="Pipeline to deploy alcf_ceilometer",
                stack_name=self.config["stack_name"],
                tags=resolve_tags(self.config, self.target_env),
            )
        )

        # Call the super constructor
        super().__init__(app, id, **kwargs)

        # Execution buckets used by the pipeline
        cross_region_replication_buckets = {}
        for target_region in self.config["target_regions"]:
            bucket = s3.Bucket.from_bucket_arn(
                self,
                f"ExecBucket{target_region}",
                bucket_arn="arn:aws:s3:::{bucket_name}".format(
                    bucket_name=self.config["exec_buckets"][target_region]
                ),
            )
            cross_region_replication_buckets.update({target_region: bucket})

        # CDK Pipeline
        source = CodePipelineSource.connection(
            "MetServiceDev/alcf_ceilometer", "master",
            connection_arn=ssm.StringParameter.value_for_string_parameter(
                self, self.config['codestar_connection_parameter'])
        )

        pipeline = CodePipeline(
            self, "Alcf_ceilometerPipeline",
            code_pipeline=codepipeline.Pipeline(
                self, "CodePipeline",
                cross_region_replication_buckets=cross_region_replication_buckets,
            ),
            self_mutation_code_build_defaults=CodeBuildOptions(
                partial_build_spec=codebuild.BuildSpec.from_object(
                    dict(
                        phases=dict(
                            install=dict(
                                commands=[
                                    "npm install -g cdk-assume-role-credential-plugin"
                                ]
                            )
                        )
                    )
                )
            ),
            synth=CodeBuildStep(
                "Synth",
                input=source,
                install_commands=[
                    "npm install -g aws-cdk",
                    "npm install -g cdk-assume-role-credential-plugin",
                    "aws codeartifact --region us-west-2 login --domain artifacts-fr-metservice --domain-owner 557762406065 --tool pip --repository fr-dev-python",
                    "pip install --upgrade pip",
                    f"pip install -q -r {SUBDIRECTORY_APPS_PIPELINE}/requirements.txt"
                ],
                commands=[
                    f"cd {SUBDIRECTORY_APPS_PIPELINE}",
                    "cdk synth"
                ],
                role_policy_statements=[
                    # Grant permissions to perform lookups (if required) using the cdk-assume-role-credential-plugin plugin
                    iam.PolicyStatement(
                        actions=["sts:AssumeRole"],
                        resources=[
                            f"arn:aws:iam::{self.account}:role/CDKReadRole",
                        ],
                    ),
                    # Grant permissions to login to CodeArtifact
                    iam.PolicyStatement(
                        actions=[
                            "codeartifact:GetAuthorizationToken",
                            "codeartifact:GetRepositoryEndpoint",
                            "codeartifact:ReadFromRepository",
                        ],
                        resources=[
                            f"arn:aws:codeartifact:*:{self.account}:domain/artifacts-fr-metservice",
                            f"arn:aws:codeartifact:*:{self.account}:package/artifacts-fr-metservice/*/*/*/*",
                            f"arn:aws:codeartifact:*:{self.account}:repository/artifacts-fr-metservice/fr*",
                        ],
                    ),
                    iam.PolicyStatement(
                        actions=["sts:GetServiceBearerToken"],
                        conditions={
                            "StringEquals": {
                                "sts:AWSServiceName": "codeartifact.amazonaws.com"
                            }
                        },
                        resources=["*"],
                    ),
                ],
                primary_output_directory=str(Path(SUBDIRECTORY_APPS_PIPELINE) / "cdk.out")
            ),
            docker_enabled_for_synth=True
        )

        if self.target_env == "Prod":
            pipeline.add_stage(
                Alcf_ceilometerApplicationStage(
                    self,
                    "Alcf_ceilometerApplicationStagePreProd",
                    "PreProd",
                    env=core.Environment(account="557762406065", region="us-west-2"),
                )
            )

            pipeline.add_stage(
                Alcf_ceilometerApplicationStage(
                    self,
                    f"Alcf_ceilometerApplicationStage{self.target_env}",
                    self.target_env,
                    env=core.Environment(account="557762406065", region="us-west-2"),
                ),
                pre=[ManualApprovalStep("ApprovalBeforeDeployingProduction")],
                post=[
                    self.docs_build_step(
                        f"{self.target_env}-Alcf_ceilometer-Docs", source, prod=True)
                ]
            )
        else:
            pipeline.add_stage(
                Alcf_ceilometerApplicationStage(
                    self,
                    f"Alcf_ceilometerApplicationStage{self.target_env}",
                    self.target_env,
                    env=core.Environment(account="557762406065", region="us-west-2"),
                ),
                post=[
                    self.docs_build_step(
                        f"{self.target_env}-Alcf_ceilometer-Docs", source)
                ]
            )

    def docs_build_step(self, name: str, input: CodePipelineSource, prod: bool=False) -> CodeBuildStep:
        """Return a CDK Pipeline Step object to build documentation

        Args:
            name: name of the resource
            input: input source code
            prod: are these docs for production
        
        Returns:
            An object to build documentation
        """
        return CodeBuildStep(
            name,
            input=input,
            install_commands=[
                "aws codeartifact --region us-west-2 login --domain artifacts-fr-metservice --domain-owner 557762406065 --tool pip --repository fr-dev-python",
                "pip install --upgrade pip",
                "pip install -q -r docs/requirements-docs.txt",
                "for file in apps/**/requirements.txt; do pip install -q -r $file; done",
                "for file in lambdas/**/**/requirements.txt; do pip install -q -r $file; done"
            ],
            commands=[
                "make -C docs/ gen_all",
                f"make -C docs/ publish IS_COMMIT_TAGGED={prod}"
            ],
            role_policy_statements=[
                # Grant permissions to login to CodeArtifact
                iam.PolicyStatement(
                    actions=[
                        "codeartifact:GetAuthorizationToken",
                        "codeartifact:GetRepositoryEndpoint",
                        "codeartifact:ReadFromRepository",
                    ],
                    resources=[
                        f"arn:aws:codeartifact:*:{self.account}:domain/artifacts-fr-metservice",
                        f"arn:aws:codeartifact:*:{self.account}:package/artifacts-fr-metservice/*/*/*/*",
                        f"arn:aws:codeartifact:*:{self.account}:repository/artifacts-fr-metservice/fr*",
                    ],
                ),
                iam.PolicyStatement(
                    actions=["sts:GetServiceBearerToken"],
                    conditions={
                        "StringEquals": {
                            "sts:AWSServiceName": "codeartifact.amazonaws.com"
                        }
                    },
                    resources=["*"],
                ),
                # Grant permission to access SSM Parameter Store
                iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    resources=["*"],
                ),
                # Grant permission to access S3
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket"
                    ],
                    resources=[
                        "arn:aws:s3:::*docs.fr.metcloudservices.com",
                        "arn:aws:s3:::*docs.fr.metcloudservices.com/*"
                    ]
                )
            ]
        )
