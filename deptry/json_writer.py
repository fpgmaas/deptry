import json
from typing import Dict


class JsonWriter:
    """
    Class to write issues to a json file
    """

    def __init__(self, json_output: str) -> None:
        self.json_output = json_output

    def write(self, issues: Dict):
        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(issues, f, ensure_ascii=False, indent=4)
