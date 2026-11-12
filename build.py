#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a SillyTavern theme json from a per-theme source directory.

Usage:
    python build.py <slug>
    python build.py <slug> --check
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "theme.schema.json"
THEMES_DIR = ROOT / "themes"

# The repository is a backup target, not a runtime resource host.
SELF_REPO_MARKERS = ("st-css",)


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SystemExit("File not found: " + str(path))
    except json.JSONDecodeError as exc:
        raise SystemExit("Invalid JSON: %s (%s)" % (path, exc))


def type_ok(value, expected):
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    return True


def validate(obj, schema):
    errors = []
    props = schema.get("properties", {})

    for key in schema.get("required", []):
        if key not in obj:
            errors.append("missing field: " + key)

    if schema.get("additionalProperties") is False:
        for key in obj:
            if key not in props:
                errors.append("unknown field: " + key)

    for key, value in obj.items():
        spec = props.get(key)
        if not spec:
            continue
        expected = spec.get("type")
        if expected and not type_ok(value, expected):
            errors.append("%s: expected %s, got %s" % (key, expected, type(value).__name__))
            continue
        pattern = spec.get("pattern")
        if pattern and isinstance(value, str) and not re.match(pattern, value):
            errors.append("%s: invalid format: %s" % (key, value[:60]))
        if "enum" in spec and value not in spec["enum"]:
            errors.append("%s: value %r not in %r" % (key, value, spec["enum"]))
        if "minimum" in spec and isinstance(value, (int, float)) and value < spec["minimum"]:
            errors.append("%s: below minimum %s" % (key, spec["minimum"]))
        if "maximum" in spec and isinstance(value, (int, float)) and value > spec["maximum"]:
            errors.append("%s: above maximum %s" % (key, spec["maximum"]))

    return errors


def strip_private_keys(obj):
    return {k: v for k, v in obj.items() if not k.startswith("_")}


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def scan_self_repo(css):
    body = strip_comments(css)
    urls = re.findall(r"https?://[^\s\"');]+", body)
    return sorted({u for u in urls if any(m in u.lower() for m in SELF_REPO_MARKERS)})


def build(slug, check_only=False):
    theme_dir = THEMES_DIR / slug
    if not theme_dir.is_dir():
        raise SystemExit("Theme directory not found: " + str(theme_dir))

    css_path = theme_dir / "style.css"
    meta_path = theme_dir / "meta.json"
    if not css_path.is_file():
        raise SystemExit("File not found: " + str(css_path))
    if not meta_path.is_file():
        raise SystemExit("File not found: " + str(meta_path))

    css = css_path.read_text(encoding="utf-8")
    meta = strip_private_keys(load_json(meta_path))
    schema = load_json(SCHEMA_PATH)

    blocked = scan_self_repo(css)
    if blocked:
        print("[blocked] CSS references this repository as a resource URL:")
        for url in blocked:
            print("          " + url)
        raise SystemExit(1)

    result = dict(meta)
    result["custom_css"] = css
    errors = validate(result, schema)
    if errors:
        print("[validation failed] %d issue(s):" % len(errors))
        for err in errors:
            print("          - " + err)
        raise SystemExit(1)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    json.loads(text)

    print("[ok] fields=%d  css=%d chars  slug=%s" % (len(result), len(css), slug))
    if check_only:
        print("     dry run, nothing written")
        return result

    out = theme_dir / (slug + ".json")
    out.write_text(text + "\n", encoding="utf-8")
    print("[built] " + str(out))
    return result


def main():
    parser = argparse.ArgumentParser(description="Build a SillyTavern theme json")
    parser.add_argument("slug", help="theme directory name under themes/")
    parser.add_argument("--check", action="store_true", help="validate only, do not write")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.slug):
        raise SystemExit("slug must start with a letter or digit and contain only A-Z a-z 0-9 _ -")

    build(args.slug, args.check)


if __name__ == "__main__":
    main()
