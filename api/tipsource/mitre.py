from typing import Any

from mitreattack.stix20 import MitreAttackData

from api.tipsource.baseclass import TIPSource


class MITRE(TIPSource):
    def __init__(self) -> None:
        self.mitre = MitreAttackData("enterprise-attack.json")

    # have no clue how to type kwargs in subclass like this
    def fetch_data(self, queries: list[str], **kwargs: Any) -> dict[str, Any]:
        stixtype = kwargs.get("stixtype", "attack-pattern")

        full_info = {}
        for query in queries:
            info = self.mitre.get_object_by_attack_id(query, stixtype)
            full_info["query"] = info

        return full_info
