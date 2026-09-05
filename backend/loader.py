from pathlib import Path
from typing import Dict

import yaml

from backend.models import SOP


SOPS_DIR = Path(__file__).parent / "sops"


def load_sops() -> Dict[str, SOP]:
    protocols = {}

    for yaml_file in SOPS_DIR.glob("*.yaml"):

        with open(yaml_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not data:
            continue

        for item in data:
            sop = SOP(**item)

            if sop.id in protocols:
                raise ValueError(
                    f"Duplicate SOP ID found: {sop.id}"
                )

            protocols[sop.id] = sop

    return protocols