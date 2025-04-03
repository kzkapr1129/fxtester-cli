"""設定ファイルモジュール"""

from pathlib import Path
import sys
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomlkit


def load_config(config_path: Path) -> dict[str, Any]:
    """設定情報の読み込み

    toml形式の設定ファイルを読み込む

    Args:
        config_path (Path): 設定ファイルのパス

    Returns:
        dict[str,Any]: 設定情報が格納された辞書データ
    """
    config = {}
    if config_path.is_file():
        with config_path.open() as f:
            if "tomlkit" in sys.modules:
                config = tomlkit.parse(f.read())
            elif "tomllib" in sys.modules:
                config = tomllib.loads(f.read())
    return config
