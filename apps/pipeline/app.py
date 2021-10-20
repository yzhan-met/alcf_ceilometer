#!/usr/bin/env python

"""CDK app for deploying pipeline resources for alcf_ceilometer"""

import sys
from pathlib import Path

from aws_cdk import core

# Inject required path to gain access to the stacks package
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent),
)
from stacks.pipeline import (  # pylint: disable=import-error,wrong-import-position
    Alcf_ceilometerPipelineStack,
)

_app = core.App()

# Iterate supported_environments and create one stack for each
for target_env in _app.node.try_get_context("supported_environments"):
    Alcf_ceilometerPipelineStack(
        _app,
        # Use the real stack name else there is a mismatch between the id of the stack and
        # the real CFn stack meaning the pipeline cannot self mutate !
        Alcf_ceilometerPipelineStack.load_config(target_env)["stack_name"],
        target_env,
        env=core.Environment(
            account=str(_app.node.try_get_context("account_id")),
            region=_app.node.try_get_context("region"),
        ),
    )

_app.synth()
