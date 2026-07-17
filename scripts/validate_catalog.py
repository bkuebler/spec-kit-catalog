#!/usr/bin/env python3
"""Validate the extension and workflow catalogs: structure, id/key consistency, reachable URLs.

Usage:
    python scripts/validate_catalog.py            # full (structure + URL HEAD checks)
    python scripts/validate_catalog.py --skip-urls # structure only
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_URLS = "--skip-urls" in sys.argv

EXT_REQUIRED = ["name", "id", "description", "author", "version",
                "download_url", "repository", "license"]
WF_REQUIRED = ["id", "name", "description", "author", "version", "url"]


def check_url(url):
    """Return HTTP status (redirects followed). Falls back to GET if HEAD is refused."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(
                url, method=method, headers={"User-Agent": "catalog-validator"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405):
                continue
            return e.code
        except Exception as e:  # noqa: BLE001
            return f"ERR {e}"
    return "ERR HEAD and GET both failed"


def validate_dict_catalog(path, top_collection, required, url_field):
    errs = []
    data = json.loads(path.read_text())
    for key in ("schema_version", top_collection):
        if key not in data:
            errs.append(f"[{path.name}] missing top-level key: {key}")
    items = data.get(top_collection, {})
    if not isinstance(items, dict):
        errs.append(f"[{path.name}] '{top_collection}' must be an object keyed by id")
        return errs
    for iid, item in items.items():
        for f in required:
            if f not in item:
                errs.append(f"[{path.name}:{iid}] missing field: {f}")
        if item.get("id") != iid:
            errs.append(f"[{path.name}:{iid}] id field '{item.get('id')}' != map key")
        if top_collection == "extensions":
            if "speckit_version" not in (item.get("requires") or {}):
                errs.append(f"[{path.name}:{iid}] missing requires.speckit_version")
        if not SKIP_URLS and item.get(url_field):
            st = check_url(item[url_field])
            ok = st in (200, 302)
            print(f"  {'OK ' if ok else 'BAD'} {iid:20} {st}  {item[url_field]}")
            if not ok:
                errs.append(f"[{path.name}:{iid}] {url_field} unreachable ({st}): {item[url_field]}")
    return errs


def main():
    errs = []
    ext = ROOT / "catalog.json"
    wf = ROOT / "workflow-catalog.json"

    if ext.exists():
        print(f"Validating {ext.name} ...")
        errs += validate_dict_catalog(ext, "extensions", EXT_REQUIRED, "download_url")
    else:
        errs.append("catalog.json not found")

    if wf.exists():
        print(f"Validating {wf.name} ...")
        errs += validate_dict_catalog(wf, "workflows", WF_REQUIRED, "url")

    if errs:
        print("\nFAILED:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
