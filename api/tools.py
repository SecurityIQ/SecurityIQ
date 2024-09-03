import json

from langchain_core.tools import tool

from api.tipsource.mitre import MITRE
from api.typings.stix import STIXCategory


@tool
def get_info_mitre(technique_ids: list[str], stix_type: STIXCategory) -> str:
    """Get information about a specific MITRE ATT&CK technique

    Args:
    ----
        technique_id_list: A list of MITRE ATT&CK technique IDs to get information about
        stix_type: The STIX type to get information about, must be one of attack-pattern, malware, tool, intrusion-set, campaign, course-of-action, x-mitre-matrix, x-mitre-tactic, x-mitre-data-source, x-mitre-data-component

    """
    mitre = MITRE()

    info = mitre.fetch_data(technique_ids, stixtype=stix_type)
    return json.dumps(info)
