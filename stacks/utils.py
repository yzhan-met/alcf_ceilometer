"""Module stacks.utils"""

import subprocess
from pathlib import Path

from ruamel.yaml import YAML
from fr_helpers.common.utils import merge_dicts_v2

yaml = YAML()


# TODO: this method should probably be put in a FR CDK library as it will be used quite often
def consolidate_config(
    config_filepath: str, environment: str, use_git_info: bool = False
) -> dict:
    """Consolidate the main's context based on environment as a single dict.

    Note: this is not the full context but just common + environment.
    The environment must exist as a key of context.
    
    Args:
        config_filepath (str): The full path of the config file to load config from.
        environment (str): The specific environment to load configuration from.
    
    Returns:
        dict: The consolidated common+environment as a single dict.
    """
    with open(config_filepath) as handler:
        loaded_config = yaml.load(handler)

    # In the same folder as the config file, load the tags.yaml file
    with open(str(Path(config_filepath).parent / "tags.yaml")) as handler:
        loaded_tags = yaml.load(handler)

    config = loaded_config["Common"]
    config["tags"] = loaded_tags

    config = dict(merge_dicts_v2(config, loaded_config.get(environment, {})))

    if use_git_info:
        # Automatically inject the current git branch name and closest tag
        config["git"] = dict(
            tag=subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
            .decode("ascii")
            .strip(),
            branch=subprocess.check_output(["git", "branch", "--show-current"])
            .decode("ascii")
            .strip(),
            commit=subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip(),
        )

    return config


def resolve_tags(config: dict, environment: str) -> dict:
    """Resolves the tags of the stack.

    Returns:
        dict: The resolved tags of the stack.
    """
    tags = config.get("tags", {})
    tags["Environment"] = environment

    return tags
