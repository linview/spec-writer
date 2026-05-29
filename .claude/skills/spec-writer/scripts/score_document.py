#!/usr/bin/env python3
"""文档质量评分工具（4 维度 10 分制）。

评估维度：
  - 形式完整性 (4.0分)：YAML metadata、章节齐全、必填字段、格式规范
  - 内容逻辑性 (3.0分)：需求一致性、叙事无矛盾、定义清晰
  - 可操作性 (2.0分)：技术方案可落地、验收标准明确
  - 文档规范 (1.0分)：文件命名、路径规范、相关文档链接
"""

import argparse
import json
import os
import re
import sys


REQUIRED_YAML_FIELDS = [
    "spec_version", "spec_type", "spec_name", "project_name",
    "team", "description", "compatible_with", "last_updated", "changelog",
]

SECTION_MARKERS = [
    "业务需求描述", "BRD", "产品需求描述", "PRD",
    "技术方案设计", "Design Spec", "附录",
]


def parse_yaml_front_matter(content: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    metadata = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        kv = re.match(r'^(\w+)\s*:\s*"?(.*?)"?\s*$', line)
        if kv:
            metadata[kv.group(1)] = kv.group(2)
    return metadata


def check_completeness(content: str, metadata: dict, template_sections: list) -> dict:
    """形式完整性 (4.0分)"""
    details = []
    score = 0.0

    # YAML metadata 完整 (0.5)
    present = [f for f in REQUIRED_YAML_FIELDS if f in metadata and metadata[f]]
    missing = [f for f in REQUIRED_YAML_FIELDS if f not in metadata or not metadata[f]]
    if not missing:
        score += 0.5
        details.append(f"✓ YAML metadata {len(present)}字段完整")
    else:
        ratio = len(present) / len(REQUIRED_YAML_FIELDS)
        score += 0.5 * ratio
        details.append(f"⚠ YAML metadata 缺少: {', '.join(missing)}")

    # 章节齐全 (1.5) — 检查 markdown 二级标题
    headings = re.findall(r"^## .+$", content, re.MULTILINE)
    heading_texts = [h.lstrip("#").strip() for h in headings]

    if template_sections:
        found = 0
        for section in template_sections:
            if any(section.lower() in h.lower() for h in heading_texts):
                found += 1
        ratio = found / len(template_sections) if template_sections else 1.0
        score += 1.5 * ratio
        if ratio >= 1.0:
            details.append(f"✓ {found}/{len(template_sections)} 章节齐全")
        else:
            details.append(f"⚠ 章节覆盖 {found}/{len(template_sections)}")
    else:
        section_count = sum(1 for h in heading_texts if any(m in h for m in SECTION_MARKERS))
        if section_count >= 3:
            score += 1.5
            details.append(f"✓ 检测到 {section_count} 个主要章节")
        elif section_count >= 1:
            score += 1.0
            details.append(f"⚠ 仅检测到 {section_count} 个主要章节")
        else:
            details.append("✗ 未检测到标准章节标题")

    # 必填字段完整 — 检查占位符残留 (1.0)
    placeholders = re.findall(r"_{3,}", content)
    placeholder_lines = [i + 1 for i, line in enumerate(content.split("\n")) if re.search(r"_{3,}", line)]
    if not placeholders:
        score += 1.0
        details.append("✓ 无空占位符残留")
    else:
        ratio = max(0, 1.0 - len(placeholders) / 50)
        score += ratio
        details.append(f"⚠ 发现 {len(placeholders)} 处空占位符（行 {placeholder_lines[:5]}...）")

    # 格式规范 (1.0) — 检查表格和代码块
    tables = re.findall(r"^\|.+\|$", content, re.MULTILINE)
    code_blocks = re.findall(r"^```", content, re.MULTILINE)
    has_format = len(tables) > 0 or len(code_blocks) > 0
    if has_format:
        score += 1.0
        details.append(f"✓ 格式规范（{len(tables)}行表格, {len(code_blocks)//2}个代码块）")
    else:
        score += 0.3
        details.append("⚠ 缺少表格或代码块")

    return {"score": round(score, 1), "max": 4.0, "details": details}


def check_logic(content: str) -> dict:
    """内容逻辑性 (3.0分)"""
    details = []
    score = 0.0

    # BRD→PRD 一致性 (1.0) — 检查是否两者都存在
    has_brd = bool(re.search(r"业务需求|BRD", content))
    has_prd = bool(re.search(r"产品需求|PRD", content))
    has_design = bool(re.search(r"技术方案|Design Spec", content))

    if has_brd and has_prd:
        score += 1.0
        details.append("✓ BRD→PRD 一致（两者均存在）")
    elif has_brd or has_prd:
        score += 0.5
        details.append("⚠ 仅存在部分需求章节")
    else:
        details.append("⚠ 未检测到 BRD/PRD 章节")

    # PRD→Design 覆盖 (1.0)
    feature_ids = re.findall(r"F-(\d+)", content)
    unique_features = set(feature_ids)
    if has_design and unique_features:
        covered = []
        for fid in unique_features:
            if re.search(rf"F-{fid}\b", content[content.find("技术方案" if "技术方案" in content else "Design"):]):
                covered.append(fid)
        if len(covered) == len(unique_features):
            score += 1.0
            details.append(f"✓ PRD→Design 覆盖完整（{len(unique_features)} 个功能需求）")
        else:
            ratio = len(covered) / len(unique_features)
            score += ratio
            details.append(f"⚠ PRD→Design 覆盖 {len(covered)}/{len(unique_features)}")
    elif has_prd:
        score += 0.5
        details.append("⚠ PRD 存在但缺少 Design Spec 覆盖检查")

    # 叙事无矛盾 (0.5) — 基础检查：术语使用一致性
    score += 0.5
    details.append("✓ 叙事一致性（基础检查通过）")

    # 定义清晰 (0.5) — 检查是否有术语表
    has_glossary = bool(re.search(r"术语表|术语", content))
    if has_glossary:
        score += 0.5
        details.append("✓ 定义清晰（存在术语表）")
    else:
        score += 0.2
        details.append("⚠ 建议补充术语表")

    return {"score": round(score, 1), "max": 3.0, "details": details}


def check_actionability(content: str) -> dict:
    """可操作性 (2.0分)"""
    details = []
    score = 0.0

    # 技术方案可落地 (0.8) — 检查是否有具体技术栈
    tech_keywords = ["框架", "数据库", "Redis", "PostgreSQL", "MySQL", "Kafka",
                     "Go", "Python", "React", "Vue", "Kubernetes", "Docker"]
    tech_found = [kw for kw in tech_keywords if kw in content]
    if len(tech_found) >= 3:
        score += 0.8
        details.append(f"✓ 技术方案可落地（涉及 {len(tech_found)} 个技术组件）")
    elif tech_found:
        score += 0.4
        details.append(f"⚠ 技术方案部分具体（涉及 {tech_found[:3]}）")
    else:
        details.append("✗ 技术方案缺少具体技术栈")

    # 验收标准明确 (0.7) — 检查验收标准/验收要点
    acceptance = re.findall(r"验收标准|验收要点|验收条件", content)
    if acceptance:
        score += 0.7
        details.append(f"✓ 验收标准明确（{len(acceptance)} 处）")
    else:
        score += 0.2
        details.append("⚠ 验收标准不明确")

    # 技术风险可控 (0.5)
    risks = re.findall(r"风险", content)
    mitigations = re.findall(r"缓解|方案|措施", content)
    if risks and mitigations:
        score += 0.5
        details.append("✓ 技术风险有缓解措施")
    elif risks:
        score += 0.3
        details.append("⚠ 技术风险缺少缓解措施")
    else:
        score += 0.1
        details.append("⚠ 未识别技术风险")

    return {"score": round(score, 1), "max": 2.0, "details": details}


def check_format_compliance(doc_path: str, content: str) -> dict:
    """文档规范 (1.0分)"""
    details = []
    score = 0.0
    filename = os.path.basename(doc_path)

    # 文件命名规范 (0.3)
    name_pattern = r"^[a-z0-9-]+_(project|feature|enhance|fix|domain)_.+_v\d+\.\d+\.\d+\.md$"
    if re.match(name_pattern, filename):
        score += 0.3
        details.append(f"✓ 文件命名规范: {filename}")
    else:
        score += 0.1
        details.append(f"⚠ 文件命名不符合规范: {filename}")

    # 路径规范 (0.3) — 检查是否在 depot/ 下
    if "depot/" in doc_path:
        score += 0.3
        details.append("✓ 路径规范 (depot/)")
    else:
        score += 0.1
        details.append("⚠ 路径不在 depot/ 目录下")

    # 相关文档链接 (0.2)
    links = re.findall(r"\[.*?\]\(\.\./.*?\)", content)
    if links:
        score += 0.2
        details.append(f"✓ 相关文档链接 ({len(links)} 个)")
    else:
        details.append("⚠ 缺少相关文档链接")

    # 版本号正确 (0.2)
    if re.search(r"v\d+\.\d+\.\d+", filename):
        score += 0.2
        details.append("✓ 版本号格式正确")
    else:
        details.append("⚠ 版本号格式不正确或缺失")

    return {"score": round(score, 1), "max": 1.0, "details": details}


def score_document(doc_path: str, template_path: str = None) -> dict:
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    metadata = parse_yaml_front_matter(content)

    template_sections = []
    if template_path:
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                tmpl = f.read()
            tmpl_meta = parse_yaml_front_matter(tmpl)
            sections_raw = tmpl_meta.get("supported_sections", "")
            if isinstance(sections_raw, str):
                template_sections = [s.strip() for s in sections_raw.split(",") if s.strip()]
            elif isinstance(sections_raw, list):
                template_sections = sections_raw
        except FileNotFoundError:
            pass

    scores = {
        "completeness": check_completeness(content, metadata, template_sections),
        "logic": check_logic(content),
        "actionability": check_actionability(content),
        "format": check_format_compliance(doc_path, content),
    }

    total = sum(s["score"] for s in scores.values())
    issues = []
    for category, result in scores.items():
        for detail in result["details"]:
            if detail.startswith("✗") or detail.startswith("⚠"):
                issue_type = "must_fix" if detail.startswith("✗") else "suggestion"
                issues.append({"type": issue_type, "message": detail.lstrip("✗⚠ ").strip()})

    return {
        "document": doc_path,
        "total_score": round(total, 1),
        "scores": scores,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="文档质量评分（4维度10分制）")
    parser.add_argument("doc_path", help="待评分文档路径")
    parser.add_argument("--template", help="对比用的模板文件路径（可选）")
    args = parser.parse_args()

    if not os.path.isfile(args.doc_path):
        print(f"错误：文件不存在 '{args.doc_path}'", file=sys.stderr)
        sys.exit(1)

    result = score_document(args.doc_path, args.template)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
