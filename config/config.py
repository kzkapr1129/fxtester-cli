from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomlkit


def load_config(config_path: Path) -> dict:
    config = {}
    if config_path.is_file():
        with config_path.open() as f:
            if "tomlkit" in sys.modules:
                config = tomlkit.parse(f.read())
            elif "tomllib" in sys.modules:
                config = tomllib.loads(f.read())
    return config
