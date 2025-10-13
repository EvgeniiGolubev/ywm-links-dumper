import configparser
from pathlib import Path

APP_NAME = "YWM_ExternalLinks"
SETTINGS_FILENAME = "settings.ini"

class Settings:
    def __init__(self):
        self.setting_path = self.__get_settings_path()
        self.config = configparser.ConfigParser()

        if self.setting_path.exists():
            self.config.read(self.setting_path, encoding="utf-8")
        else:
            self._create_default()

        default = self.config["DEFAULT"]
        self.oauth_token = default.get("YWM_OAUTH_TOKEN", "")
        self.out_dir = default.get("YWM_OUTPUT_DIR", str(Path.home() / "Desktop"))
        self.host_domain = default.get("YWM_HOST_DOMAIN", "")
        self.limit = int(default.get("YWM_LIMIT", "100"))
        self.offset = int(default.get("YWM_OFFSET", "0"))

    def save(self, key: str, value: str) -> None:
        self.config["DEFAULT"][key] = value
        self._save()

        attr_name = self._key_to_attr(key)
        if attr_name in ("limit", "offset"):
            setattr(self, attr_name, int(value))
        else:
            setattr(self, attr_name, value)

    def __get_settings_path(self) -> Path:
        documents = Path.home() / "Documents"
        config_dir = documents / APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / SETTINGS_FILENAME

    def _create_default(self):
        self.config["DEFAULT"] = {
            "YWM_OAUTH_TOKEN": "",
            "YWM_OUTPUT_DIR": str(Path.home() / "Desktop"),
            "YWM_HOST_DOMAIN": "",
            "YWM_LIMIT": "100",
            "YWM_OFFSET": "0"
        }
        self._save()

    def _save(self):
        with open(self.setting_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    def _key_to_attr(self, key: str) -> str:
        return key.lower().replace("ywm_", "")