#!/usr/bin/env python3
"""根据文档 metadata 生成标准化文件名。

格式：{project}_{type}_{summary}_v{X.Y.Z}.md
"""

import argparse
import json
import sys


def generate_filename(
    project: str,
    doc_type: str,
    summary: str,
    version: str,
) -> str:
    project_slug = project.lower().replace(" ", "-")
    summary_slug = summary.lower().replace(" ", "_")
    return f"{project_slug}_{doc_type}_{summary_slug}_v{version}.md"


def main():
    parser = argparse.ArgumentParser(description="生成标准化文档文件名")
    parser.add_argument("--project", help="项目名称")
    parser.add_argument("--type", help="文档类型 (project/feature/enhance/fix)")
    parser.add_argument("--summary", help="文档摘要/简称")
    parser.add_argument("--version", default="1.0.0", help="版本号 (默认: 1.0.0)")
    parser.add_argument("--metadata", help="JSON 格式的 metadata (优先级高于单独参数)")
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(args.metadata)
        project = meta.get("project_name", meta.get("spec_name", "unknown"))
        doc_type = meta.get("spec_type", "project")
        summary = meta.get("summary", meta.get("spec_name", doc_type))
        version = meta.get("spec_version", "1.0.0")
    else:
        project = args.project or "unknown"
        doc_type = args.type or "project"
        summary = args.summary or doc_type
        version = args.version

    filename = generate_filename(project, doc_type, summary, version)
    print(filename)


if __name__ == "__main__":
    main()
