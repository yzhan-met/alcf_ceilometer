"""Module stacks.alcf_ceilometer"""

from pkg_resources import resource_filename

from pathlib import Path
from aws_cdk import (
    core as cdk
)

from .utils import consolidate_config, resolve_tags


class Alcf_ceilometerStack(cdk.Stack):
    """Stack to deploy resources for alcf_ceilometer"""

    @classmethod
    def load_config(cls, target_env: str, use_git_info: bool) -> dict:
        """Loads the configuration for the given stack.

        Config file is located in configurations/<name of the class>.yaml.
        
        Args:
            target_env (str): The environment - Dev, PreProd, Prod - to work with.
            use_git_info (bool): Flag to indicate if git info must be used.
        
        Returns:
            dict: The load configuration for the given target_env.
        """
        return consolidate_config(
            resource_filename(__name__, f"configurations/{cls.__name__}.yaml"),
            target_env,
            use_git_info=use_git_info,
        )

    def __init__(
        self,
        app: cdk.App,
        id: str,  # pylint: disable=redefined-builtin
        target_env: str,
        stack_name_suffix: str = "",
        use_git_info: bool = False,
        **kwargs,
    ) -> None:

        # For the given target environment, load the configuration
        self.config = self.load_config(target_env, use_git_info)
        self.resolve_stack_names(suffix=stack_name_suffix)

        self.target_env = target_env
        self.suffix = stack_name_suffix

        # Override description, stack_name and tags if they have been provided
        kwargs.update(
            dict(
                description="Alerting resources (api)",
                stack_name=self.config["stack_name"],
                tags=resolve_tags(self.config, self.target_env),
            )
        )

        # Call the super constructor
        super().__init__(app, id, **kwargs)

        # Add code here


    def resolve_stack_names(self, suffix: str = ""):
        """Resolves the stack name and updates the config object.

        Note: do not call this method more than once else the suffix is re-added.
        
        Args:
            suffix (str, optional): The suffix to add to the stack name. Defaults to "".
        """
        # Resolve the stack name (add appropriate suffix if required)
        stack_name = self.config["stack_name"]

        if self.config.get("allow_multiple", False) and suffix != "":
            # When multiple stacks are allowed, use the suffix to make it unique
            stack_name += f"-{suffix}"
            self.config["stack_name"] = stack_name
    