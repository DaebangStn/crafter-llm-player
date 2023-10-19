from typing import Any, Dict
from ruamel.yaml import YAML


def load_yaml_to_dict(path: str) -> Dict[str, Any]:
    yaml = YAML()
    with open(path, "r") as f:
        loaded = yaml.load(f)

    assert loaded is not None, f"failed to load yaml file: {path}"

    return loaded
