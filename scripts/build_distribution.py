#!/usr/bin/env python3
"""Build and verify Codex, Claude Code, and TRAE distribution artifacts."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "distribution" / "catalog.json"
PLUGIN_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class DistributionError(RuntimeError):
    pass


def load_catalog() -> dict[str, Any]:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"Cannot read {CATALOG_PATH}: {exc}") from exc

    if catalog.get("schema_version") != 1:
        raise DistributionError("distribution/catalog.json must use schema_version 1")
    marketplace = catalog.get("marketplace")
    if not isinstance(marketplace, dict) or not marketplace.get("name"):
        raise DistributionError("catalog marketplace metadata is incomplete")
    plugins = catalog.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise DistributionError("catalog must declare at least one plugin")
    return catalog


def repo_path(raw_path: str) -> Path:
    candidate = (ROOT / raw_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise DistributionError(f"Path escapes repository: {raw_path}") from exc
    return candidate


def skill_name(skill_dir: Path) -> str:
    skill_file = skill_dir / "SKILL.md"
    try:
        text = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise DistributionError(f"Cannot read {skill_file}: {exc}") from exc

    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise DistributionError(f"Missing YAML frontmatter: {skill_file}")
    name_match = re.search(r"^name:\s*([^\s#]+)\s*$", match.group(1), re.MULTILINE)
    if not name_match:
        raise DistributionError(f"Missing name in {skill_file}")
    name = name_match.group(1)
    if not SKILL_NAME_PATTERN.fullmatch(name):
        raise DistributionError(f"Invalid skill name {name!r} in {skill_file}")
    if name != skill_dir.name:
        raise DistributionError(
            f"Skill name {name!r} does not match directory {skill_dir.name!r}"
        )
    return name


def json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def ensure_file(path: Path, expected: bytes, check: bool) -> None:
    if check:
        try:
            actual = path.read_bytes()
        except OSError as exc:
            raise DistributionError(f"Missing generated file {path}: {exc}") from exc
        if actual != expected:
            raise DistributionError(f"Generated file is stale: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(expected)


def file_map(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        raise DistributionError(f"Missing directory: {root}")
    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise DistributionError(f"Symlinks are not supported in packaged skills: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def sync_tree(source: Path, target: Path, check: bool) -> None:
    if check:
        if file_map(source) != file_map(target):
            raise DistributionError(f"Packaged skill is stale: {target}")
        return

    if target.exists():
        if target.is_symlink():
            raise DistributionError(f"Refusing to replace symlinked target: {target}")
        shutil.rmtree(target)
    shutil.copytree(source, target)


def codex_manifest(plugin: dict[str, Any], owner: str) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "name": plugin["id"],
        "version": plugin["version"],
        "description": plugin["description"],
        "author": {"name": owner},
        "skills": "./skills/",
        "keywords": plugin.get("tags", []),
        "interface": {
            "displayName": plugin["display_name"],
            "shortDescription": plugin["description"],
            "longDescription": plugin["long_description"],
            "developerName": owner,
            "category": plugin["category"],
            "capabilities": [],
            "defaultPrompt": plugin["default_prompt"],
        },
    }
    if plugin.get("license"):
        manifest["license"] = plugin["license"]
    return manifest


def claude_manifest(plugin: dict[str, Any], owner: str) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "name": plugin["id"],
        "version": plugin["version"],
        "description": plugin["description"],
        "author": {"name": owner},
        "skills": "./skills/",
    }
    if plugin.get("license"):
        manifest["license"] = plugin["license"]
    return manifest


def codex_marketplace(catalog: dict[str, Any]) -> dict[str, Any]:
    market = catalog["marketplace"]
    return {
        "name": market["name"],
        "interface": {"displayName": market["display_name"]},
        "plugins": [
            {
                "name": plugin["id"],
                "source": {
                    "source": "local",
                    "path": f"./plugins/{plugin['id']}",
                },
                "policy": {
                    "installation": (
                        "INSTALLED_BY_DEFAULT"
                        if plugin.get("default_install")
                        else "AVAILABLE"
                    ),
                    "authentication": "ON_INSTALL",
                },
                "category": plugin["category"],
            }
            for plugin in catalog["plugins"]
        ],
    }


def claude_marketplace(catalog: dict[str, Any]) -> dict[str, Any]:
    market = catalog["marketplace"]
    return {
        "name": market["name"],
        "owner": {"name": market["owner"]},
        "metadata": {
            "description": "面向工程开发与设计工作的 Agent Skills。"
        },
        "plugins": [
            {
                "name": plugin["id"],
                "source": f"./plugins/{plugin['id']}",
                "description": plugin["description"],
                "version": plugin["version"],
                "category": plugin["category"],
                "tags": plugin.get("tags", []),
            }
            for plugin in catalog["plugins"]
        ],
    }


def zip_entry(archive: zipfile.ZipFile, name: str, data: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, data)


def build_skill_zip(source: Path, extras: dict[str, Path]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise DistributionError(
                    f"Symlinks are not supported in TRAE archives: {path}"
                )
            if path.is_file():
                mode = stat.S_IMODE(path.stat().st_mode)
                zip_entry(
                    archive,
                    path.relative_to(source).as_posix(),
                    path.read_bytes(),
                    mode,
                )
        for archive_name, path in sorted(extras.items()):
            zip_entry(archive, archive_name, path.read_bytes(), 0o644)
    return output.getvalue()


def build_trae_release_package(
    plugin: dict[str, Any], skill_archives: dict[str, bytes]
) -> bytes:
    if not skill_archives:
        raise DistributionError(f"Plugin {plugin['id']} contains no TRAE skills")
    if len(skill_archives) == 1:
        return next(iter(skill_archives.values()))

    skill_names = sorted(skill_archives)
    manifest = {
        "name": plugin["id"],
        "version": plugin["version"],
        "type": "trae-skill-bundle",
        "upload": "extract-and-upload-each-zip",
        "skills": skill_names,
    }
    display_name = plugin.get("display_name", plugin["id"])
    readme = (
        f"# {display_name} TRAE 上传包\n\n"
        f"版本：{plugin['version']}\n\n"
        "此文件是多个独立 TRAE skills 的交付 bundle，不能直接作为单个 skill 上传。"
        "请先解压，再将其中的每个 ZIP 分别上传到 TRAE 企业技能。\n\n"
        "包含：\n\n"
        + "".join(f"- `{name}.zip`\n" for name in skill_names)
    ).encode("utf-8")

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        zip_entry(archive, "README.md", readme, 0o644)
        zip_entry(archive, "MANIFEST.json", json_bytes(manifest), 0o644)
        for name in skill_names:
            zip_entry(archive, f"{name}.zip", skill_archives[name], 0o644)
    return output.getvalue()


def build(check: bool) -> None:
    catalog = load_catalog()
    market = catalog["marketplace"]
    owner = market["owner"]
    seen_plugins: set[str] = set()
    seen_skills: set[str] = set()
    trae_packages: dict[str, bytes] = {}

    for plugin in catalog["plugins"]:
        plugin_id = plugin.get("id")
        if not isinstance(plugin_id, str) or not PLUGIN_ID_PATTERN.fullmatch(plugin_id):
            raise DistributionError(f"Invalid plugin id: {plugin_id!r}")
        if plugin_id in seen_plugins:
            raise DistributionError(f"Duplicate plugin id: {plugin_id}")
        seen_plugins.add(plugin_id)

        plugin_root = ROOT / "plugins" / plugin_id
        ensure_file(
            plugin_root / ".codex-plugin" / "plugin.json",
            json_bytes(codex_manifest(plugin, owner)),
            check,
        )
        ensure_file(
            plugin_root / ".claude-plugin" / "plugin.json",
            json_bytes(claude_manifest(plugin, owner)),
            check,
        )

        skill_root = plugin_root / "skills"
        if not check:
            if skill_root.exists():
                if skill_root.is_symlink():
                    raise DistributionError(
                        f"Refusing to replace symlinked directory: {skill_root}"
                    )
                shutil.rmtree(skill_root)
            skill_root.mkdir(parents=True)

        extras: dict[str, Path] = {}
        if plugin.get("license_file"):
            extras["LICENSE.txt"] = repo_path(plugin["license_file"])
        if plugin.get("provenance_file"):
            extras["UPSTREAM.json"] = repo_path(plugin["provenance_file"])

        for archive_name, source in extras.items():
            ensure_file(plugin_root / archive_name, source.read_bytes(), check)

        plugin_skill_archives: dict[str, bytes] = {}
        for raw_skill_path in plugin.get("skills", []):
            source = repo_path(raw_skill_path)
            name = skill_name(source)
            if name in seen_skills:
                raise DistributionError(f"Duplicate active skill name: {name}")
            seen_skills.add(name)
            sync_tree(source, skill_root / name, check)
            plugin_skill_archives[name] = build_skill_zip(source, extras)

        release_name = f"{plugin_id}-{plugin['version']}.zip"
        trae_packages[release_name] = build_trae_release_package(
            plugin, plugin_skill_archives
        )

    ensure_file(
        ROOT / ".agents" / "plugins" / "marketplace.json",
        json_bytes(codex_marketplace(catalog)),
        check,
    )
    ensure_file(
        ROOT / ".claude-plugin" / "marketplace.json",
        json_bytes(claude_marketplace(catalog)),
        check,
    )

    dist_root = ROOT / "dist" / "trae"
    expected_zip_names = set(trae_packages)
    if not check:
        dist_root.mkdir(parents=True, exist_ok=True)
        for stale_archive in dist_root.glob("*.zip"):
            stale_archive.unlink()

    checksums: list[str] = []
    for filename, payload in sorted(trae_packages.items()):
        archive_path = dist_root / filename
        ensure_file(archive_path, payload, check)
        checksums.append(f"{hashlib.sha256(payload).hexdigest()}  {filename}")
    ensure_file(
        dist_root / "SHA256SUMS",
        ("\n".join(checksums) + "\n").encode("utf-8"),
        check,
    )
    if check:
        actual_zip_names = {path.name for path in dist_root.glob("*.zip")}
        if actual_zip_names != expected_zip_names:
            raise DistributionError(
                "TRAE release artifacts are stale: "
                f"expected {sorted(expected_zip_names)}, got {sorted(actual_zip_names)}"
            )

    action = "Verified" if check else "Built"
    print(
        f"{action} {len(seen_plugins)} plugins, {len(seen_skills)} skills, "
        f"and {len(trae_packages)} TRAE release packages"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that generated files match the catalog and source skills",
    )
    args = parser.parse_args()
    try:
        build(check=args.check)
    except DistributionError as exc:
        print(f"distribution error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
