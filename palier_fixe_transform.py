#!/usr/bin/env python3
"""Transform PalierFixe input → PalierFixeElement.json in same directory; remove SDG dups, Organization, i72-typed nodes; add types, definedBy, fix Characteristic."""
import json
import sys
from pathlib import Path

DEFINED_BY = "https://ontology.commonapproach.org/cids#ac"


def sdg_ids_from_file(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return {n["@id"] for n in doc["@graph"] if isinstance(n, dict) and "@id" in n}


def is_org_node(n):
    t = n.get("@type")
    if t == "cids:Organization":
        return True
    if isinstance(t, list) and "cids:Organization" in t:
        return True
    return False


def type_has_i72(t):
    if isinstance(t, str):
        return t.startswith("i72:")
    if isinstance(t, list):
        return any(isinstance(x, str) and x.startswith("i72:") for x in t)
    return False


def with_code_type(t):
    if t is None:
        return ["cids:Code"]
    if t == "cids:Code":
        return t
    if isinstance(t, str):
        if t == "cids:Code":
            return t
        return [t, "cids:Code"]
    if isinstance(t, list):
        return t if "cids:Code" in t else t + ["cids:Code"]
    return t


def fix_sff_characteristic(x):
    if x == "sff:Characteristic":
        return "cids:Characteristic"
    if isinstance(x, list):
        return [fix_sff_characteristic(i) for i in x]
    if isinstance(x, dict):
        return {k: fix_sff_characteristic(v) for k, v in x.items()}
    return x


def main():
    in_path = Path(sys.argv[1])
    dir_ = in_path.parent
    sdg_ids = sdg_ids_from_file(dir_ / "SDGImpacts.jsonld")

    with open(in_path, encoding="utf-8") as f:
        g = json.load(f)

    out = []
    for n in g:
        if not isinstance(n, dict):
            out.append(n)
            continue
        i = n.get("@id")
        if i in sdg_ids or is_org_node(n) or type_has_i72(n.get("@type")):
            continue
        n = fix_sff_characteristic(n)
        n["@type"] = with_code_type(n.get("@type"))
        n["definedBy"] = DEFINED_BY
        out.append(n)

    out_path = dir_ / "PalierFixeElement.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
