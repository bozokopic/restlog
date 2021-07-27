from pathlib import Path

import appdirs

from hat import json


package_path: Path = Path(__file__).parent

user_conf_dir: Path = Path(appdirs.user_config_dir('restlog'))

json_schema_repo: json.SchemaRepository = json.SchemaRepository(
    json.json_schema_repo,
    json.SchemaRepository.from_json(package_path / 'json_schema_repo.json'))
