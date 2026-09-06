#!/usr/bin/env python3
"""sam-update.py — sync SAM system files from a source template into the
current project, leaving instance files untouched.

Usage:
    python plans/sam-update.py [SOURCE_PATH] [--apply]

If SOURCE_PATH is omitted, the script falls back to the SAM_TEMPLATE_PATH
environment variable. The script is run from the target project root; the
target is the current working directory.

Behavior:
- Dry-run by default. Shows per-file classification: created / updated
  (with diff) / unchanged / skipped.
- --apply actually writes the files.
- Instance files (plans/config.json, state.json, BUILD.md, etc.) are NEVER
  modified.
- Stamps plans/.sam-version on --apply with the manifest version, the source
  path, and a timestamp.
- After syncing the system files, audits the user's plans/config.json
  against the new plans/config.schema.json and reports REQUIRED / ERROR /
  WARN entries.

Exit codes:
- 0  clean sync, nothing to apply, or successful apply
- 1  script failure (bad source path, missing manifest, etc.)
- 2  config audit found warnings or errors (sync still succeeded)
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

MANIFEST_REL = "plans/sync-manifest.json"
CONFIG_REL = "plans/config.json"
SCHEMA_REL = "plans/config.schema.json"
VERSION_FILE_REL = "plans/.sam-version"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_source(arg_source: str | None) -> Path:
    src = arg_source or os.environ.get("SAM_TEMPLATE_PATH")
    if not src:
        sys.exit(
            "ERROR: no source path provided. Pass it as an argument or set "
            "SAM_TEMPLATE_PATH."
        )
    src_path = Path(src).expanduser().resolve()
    if not src_path.is_dir():
        sys.exit(f"ERROR: source path is not a directory: {src_path}")
    if not (src_path / MANIFEST_REL).is_file():
        sys.exit(f"ERROR: source path missing {MANIFEST_REL}: {src_path}")
    return src_path


def classify(src_file: Path, dst_file: Path) -> str:
    if not dst_file.exists():
        return "created"
    if src_file.read_bytes() == dst_file.read_bytes():
        return "unchanged"
    return "updated"


def show_diff(src_file: Path, dst_file: Path, label_src: str, label_dst: str) -> None:
    src_lines = src_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    dst_lines = dst_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    diff = difflib.unified_diff(dst_lines, src_lines, fromfile=label_dst, tofile=label_src, n=2)
    out = "".join(diff)
    if out:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")


def sync_file(
    src_root: Path,
    dst_root: Path,
    src_rel: str,
    dst_rel: str,
    apply: bool,
) -> tuple[str, str]:
    src_file = src_root / src_rel
    dst_file = dst_root / dst_rel
    if not src_file.is_file():
        return ("missing-in-source", dst_rel)

    status = classify(src_file, dst_file)

    if status == "updated":
        print(f"  [updated]   {dst_rel}")
        show_diff(src_file, dst_file, f"source/{src_rel}", f"target/{dst_rel}")
    elif status == "created":
        print(f"  [created]   {dst_rel}")
    else:
        print(f"  [unchanged] {dst_rel}")

    if apply and status in ("created", "updated"):
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    return (status, dst_rel)


def sync_files(
    src_root: Path,
    dst_root: Path,
    manifest: dict,
    apply: bool,
) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {
        "created": [],
        "updated": [],
        "unchanged": [],
        "scaffolded": [],
        "skipped": [],
        "missing-in-source": [],
    }

    print("System files (plans/):")
    for rel in manifest.get("system_files", []):
        status, name = sync_file(src_root, dst_root, rel, rel, apply)
        summary.setdefault(status, []).append(name)

    print("\nDeploy mappings (system files placed outside plans/):")
    for entry in manifest.get("deploy_mappings", []):
        status, name = sync_file(src_root, dst_root, entry["source"], entry["target"], apply)
        summary.setdefault(status, []).append(name)

    print("\nInstance files (scaffolded if absent, never overwritten):")
    manifest_version = manifest.get("version", "unknown")
    for rel in manifest.get("instance_files", []):
        if rel == VERSION_FILE_REL:
            verb = "stamped" if apply else "will stamp"
            print(f"  [{verb}]  {rel}  (manifest version: {manifest_version})")
            continue
        dst_file = dst_root / rel
        if dst_file.exists():
            # Present instance file — never touched.
            print(f"  [skipped]    {rel}  (instance)")
            summary["skipped"].append(rel)
            continue
        # Absent in the target: scaffold it from the template (copy-if-missing).
        src_file = src_root / rel
        if src_file.is_file():
            verb = "scaffolded" if apply else "will scaffold"
            print(f"  [{verb}] {rel}  (absent - copying from template)")
            if apply:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
            summary["scaffolded"].append(rel)
        else:
            print(f"  [skipped]    {rel}  (absent; not in template)")
            summary["skipped"].append(rel)

    return summary


def stamp_version(dst_root: Path, manifest: dict, src_root: Path) -> None:
    payload = {
        "synced_at": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "manifest_version": manifest.get("version", "unknown"),
        "source_path": str(src_root),
    }
    (dst_root / VERSION_FILE_REL).write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def audit_config(config_path: Path, schema_path: Path) -> list[tuple[str, str]]:
    """Validate a config.json against a config.schema.json. Returns a list of
    (severity, message) tuples.

    On --apply, both paths come from the target (sync is done). On dry-run,
    the schema path comes from the source so the audit reflects what the
    user's config will look like against the *incoming* schema, not the old
    one.

    Severity levels:
    - REQUIRED — schema marks key as required and it is missing
    - ERROR    — value violates enum/type
    - WARN     — new optional key (using default) or unknown key
    """
    issues: list[tuple[str, str]] = []

    if not schema_path.is_file():
        return [("ERROR", f"{SCHEMA_REL} not found in target after sync")]
    if not config_path.is_file():
        return [
            (
                "WARN",
                f"{CONFIG_REL} not found in target - SAM will use schema defaults; "
                f"create it from the source template if you want explicit values.",
            )
        ]

    schema = load_json(schema_path)
    try:
        config = load_json(config_path)
    except json.JSONDecodeError as exc:
        return [("ERROR", f"{CONFIG_REL} is not valid JSON: {exc}")]

    schema_props = schema.get("properties", {})
    required = set(schema.get("required", []))
    config_keys = set(k for k in config.keys() if k != "$schema")

    for key in required:
        if key not in config_keys:
            issues.append(("REQUIRED", f"missing required key '{key}'"))

    for key in sorted(schema_props.keys()):
        if key in ("$schema",):
            continue
        prop = schema_props[key]
        if key not in config_keys:
            default = prop.get("default")
            if default is None and prop.get("type") == "object":
                continue
            issues.append(
                (
                    "WARN",
                    f"'{key}' missing - schema added this key (default: {default!r})",
                )
            )
            continue

        value = config[key]
        enum = prop.get("enum")
        if enum is not None and value not in enum:
            issues.append(
                (
                    "ERROR",
                    f"'{key}' = {value!r} - must be one of {enum}",
                )
            )

    for key in sorted(config_keys - set(schema_props.keys())):
        issues.append(
            ("WARN", f"unknown key '{key}' - schema no longer defines this")
        )

    return issues


def print_summary(summary: dict[str, list[str]], apply: bool) -> None:
    """Render a scannable end-of-run recap. The per-file diffs above dominate the
    output; this block is the at-a-glance picture of what happened. Changed buckets
    (created / updated / scaffolded) list their filenames; unchanged / skipped show
    counts only to stay tight. Printed in both dry-run and --apply."""
    label = {
        "unchanged": "unchanged",
        "created": "created" if apply else "will create",
        "updated": "updated" if apply else "will update",
        "scaffolded": "scaffolded" if apply else "will scaffold",
        "skipped": "skipped",
        "missing-in-source": "missing in source",
    }
    order = ["unchanged", "created", "updated", "scaffolded", "skipped", "missing-in-source"]
    detailed = {"created", "updated", "scaffolded"}  # list filenames for these
    width = max(len(v) for v in label.values())

    print("\nSummary")
    for key in order:
        items = summary.get(key, [])
        n = len(items)
        if key == "missing-in-source" and n == 0:
            continue  # only surface this when it actually happens
        line = f"  {(label[key] + ':').ljust(width + 1)} {n:>3}"
        if n and key in detailed:
            line += f"   ({', '.join(items)})"
        elif n and key == "skipped":
            line += "   (instance files, unchanged)"
        print(line)


def print_audit(issues: list[tuple[str, str]]) -> int:
    print("\nConfig audit (plans/config.json vs new plans/config.schema.json):")
    if not issues:
        print("  clean - no schema drift detected")
        return 0
    width = max(len(s) for s, _ in issues)
    for severity, message in issues:
        print(f"  {severity.ljust(width)}  {message}")
    has_problem = any(s in ("REQUIRED", "ERROR", "WARN") for s, _ in issues)
    return 2 if has_problem else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync SAM system files into the current project.")
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Path to a SAM template repo. Falls back to SAM_TEMPLATE_PATH env var.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write files. Without this flag, the script only previews changes.",
    )
    args = parser.parse_args()

    src_root = resolve_source(args.source)
    dst_root = Path.cwd().resolve()

    if src_root == dst_root:
        sys.exit("ERROR: source and target are the same directory.")

    manifest = load_json(src_root / MANIFEST_REL)

    print(f"Source: {src_root}")
    print(f"Target: {dst_root}")
    print(f"Manifest version: {manifest.get('version', 'unknown')}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}\n")

    summary = sync_files(src_root, dst_root, manifest, args.apply)

    if args.apply:
        stamp_version(dst_root, manifest, src_root)

    config_path = dst_root / CONFIG_REL
    schema_path = (dst_root if args.apply else src_root) / SCHEMA_REL
    issues = audit_config(config_path, schema_path)
    audit_exit = print_audit(issues)

    # Bottom-most: the scannable recap after all the per-file diffs and the audit.
    print_summary(summary, args.apply)

    if not args.apply:
        print("\n(dry run - re-run with --apply to write changes)")

    return audit_exit


if __name__ == "__main__":
    sys.exit(main())
