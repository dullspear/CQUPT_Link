import json
import os
from logger import log


class ConfigManager:
    def __init__(self, config_file_path, default_config=None):
        self.config_file_path = config_file_path
        self.default_config = default_config
        self.load_config()

    def load_config(self) -> dict:
        if not os.path.exists(self.config_file_path):
            if self.default_config is not None:
                with open(self.config_file_path, "w", encoding="utf-8") as f:
                    json.dump(self.default_config, f, indent=4)
                return self.default_config.copy()
            else:
                with open(self.config_file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                return {}
        else:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    if self.default_config is not None:
                        data = self.default_config.copy()
                    else:
                        data = {}
                    self.save_config(data)
            if self.default_config is not None:
                for k, v in self.default_config.items():
                    if k not in data:
                        data[k] = v
            return data

    def save_config(self, config: dict) -> None:
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def get_config_value(self, key, default=None):
        config = self.load_config()
        if key in config:
            return config[key]
        if default is not None:
            return default
        log.error(f"Config key '{key}' not found and no default provided.")
        raise KeyError(f"Config key '{key}' not found")

    def set_config_value(self, key, value):
        config = self.load_config()
        config[key] = value
        self.save_config(config)

    def delete_config_key(self, key):
        config = self.load_config()
        if key in config:
            del config[key]
            self.save_config(config)
            return True
        return False

    def list_config(self):
        return self.load_config()
