#!/usr/bin/env python

"""CDK app for deploying resources for alcf_ceilometer"""

import sys
from pathlib import Path

from aws_cdk import core as cdk

# Inject required path to gain access to the stacks package
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent),
)
from stacks.alcf_ceilometer import (  # pylint: disable=import-error,wrong-import-position
    Alcf_ceilometerStack,
)

_app = cdk.App()

target_env = _app.node.try_get_context("environment")

Alcf_ceilometerStack(
    _app,
    f"Alcf_ceilometer{target_env}",
    _app.node.try_get_context("environment"),
    stack_name_suffix=_app.node.try_get_context("suffix"),
    use_git_info=False,
    env=cdk.Environment(
        account=str(_app.node.try_get_context("account_id")),
        region=_app.node.try_get_context("region"),
    ),
)

_app.synth()
