#!/usr/bin/env python3
"""扫描 templates/ 目录，解析模板 YAML frontmatter，输出 JSON 列表。"""

import argparse
import glob
import json
import re
import sys


def parse_yaml_front_matter(file_path: str) -> dict:
    """解析 YAML frontmatter，仅提取顶层标量字段和顶层简单列表。

    跳过嵌套块（缩进的子项），避免嵌套字段覆盖顶层 key。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_text = match.group(1)
    metadata = {}
    current_list_key = None

    for raw_line in yaml_text.split("\n"):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 跳过非顶层行（有缩进的行属于嵌套块）
        if raw_line.startswith("  ") or raw_line.startswith("\t"):
            # 顶层简单列表项：2空格缩进 + "- " 开头
            if current_list_key and re.match(r"^  - (\S.*)$", raw_line):
                item_text = re.match(r"^  - (\S.*)$", raw_line).group(1).strip().strip('"')
                if isinstance(metadata.get(current_list_key), list):
                    metadata[current_list_key].append(item_text)
            continue

        # 顶层 key: (空值，后面跟列表) — 必须在 match_kv 之前检查
        match_list = re.match(r"^(\w+)\s*:\s*$", stripped)
        if match_list:
            key = match_list.group(1)
            metadata[key] = []
            current_list_key = key
            continue

        # 顶层 key: value
        match_kv = re.match(r'^(\w+)\s*:\s*"?(.*?)"?\s*$', stripped)
        if match_kv:
            key, value = match_kv.group(1), match_kv.group(2)
            metadata[key] = value
            current_list_key = None
            continue

    return metadata


def scan_templates(template_dir: str = "templates/") -> list:
    pattern = f"{template_dir}/**/*.template.md"
    files = sorted(glob.glob(pattern, recursive=True))

    templates = []
    for file_path in files:
        metadata = parse_yaml_front_matter(file_path)
        if not metadata:
            continue

        entry = {
            "path": file_path,
            "name": metadata.get("template_name", ""),
            "description": metadata.get("description", ""),
            "version": metadata.get("template_version", ""),
            "type": metadata.get("template_type", ""),
            "output_mode": metadata.get("output_mode", "single"),
            "supported_sections": metadata.get("supported_sections", []),
            "compatible_with": metadata.get("compatible_with", ""),
        }

        if metadata.get("shards"):
            entry["shard_count"] = len(metadata["shards"])

        templates.append(entry)

    return templates


def main():
    parser = argparse.ArgumentParser(description="扫描模板目录，输出模板列表 JSON")
    parser.add_argument("--dir", default="templates/", help="模板目录路径 (默认: templates/)")
    args = parser.parse_args()

    templates = scan_templates(args.dir)
    json.dump(templates, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
