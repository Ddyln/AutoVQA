from pathlib import Path

import tomli as tomllib

# Load configuration from config.toml
_config_path = Path(__file__).parent / "config.toml"
with open(_config_path, "rb") as f:
    _config = tomllib.load(f)

# Load field configurations from TOML
ETP_FIELD_CONFIG = _config["etp_fields"]["fields"]
EIP_FIELD_CONFIG = _config["eip_fields"]["fields"]
IDP_FIELD_CONFIG = _config["idp_fields"]["fields"]
VQAC_FIELD_CONFIG = _config["vqac_fields"]["fields"]
NUMERIC_FIELD_CONFIG = _config["numeric_fields"]["fields"]
STR_FIELD_CONFIG = _config["str_fields"]["fields"]
LIST_FIELD_CONFIG = _config["list_fields"]["fields"]
KEY_MAPPER = _config["key_mapper"]
