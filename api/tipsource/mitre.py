from typing import Any, Literal, Required, TypedDict, Unpack

from api.typings.stix import STIXCategory
from api.tipsource.baseclass import TIPSource

from mitreattack.stix20 import MitreAttackData

class MITRE(TIPSource):
    def __init__(self) -> None:
        self.mitre = MitreAttackData('enterprise-attack.json')

    def fetch_data(self, queries: list[str], stixtype: STIXCategory) -> dict[str, Any]:
        stixtype = kwargs.get('stixtype', 'attack-pattern')

        full_info = {}
        for query in queries:
            info = self.mitre.get_object_by_attack_id(query, stixtype)
            full_info['query'] = info

        return full_info