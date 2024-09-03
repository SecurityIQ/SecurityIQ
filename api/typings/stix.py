from typing import Literal

STIXCategory = Literal[
    "attack-pattern",
    "malware",
    "tool",
    "intrusion-set",
    "campaign",
    "course-of-action",
    "x-mitre-tactic",
    "x-mitre-matrix",
    "x-mitre-data-source",
    "x-mitre-data-component",
]
