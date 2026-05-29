# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Spec Writer** — AI 驱动的工程规范文档生成系统（方案论证专用）。通过 `/spec-writer` skill 以对话式交互生成 BRD/PRD/Design Spec/HLD 等文档，支持智能推断、自动评分和草稿管理。

**文档边界**：只生成方案论证文档（为什么做 + 做什么 + 怎么做）。项目管理内容（Sprint Plan、工期估算、里程碑）由 scrum_master skill 负责，不属于本系统。

## 项目结构

```
spec-writer/
├── .claude/
│   ├── skills/spec-writer/        # 核心 skill 定义
│   │   ├── SKILL.md               # Skill 行为定义和工作流
│   │   ├── references/            # 按需加载的参考文档
│   │   │   ├── scoring_criteria.md    # 评分标准细则
│   │   │   ├── workflow_engine.md     # 对话流程示例
│   │   │   ├── engineering_research.md # 棕地工程调研流程
│   │   │   └── scenario_driven_design.md # 用户场景推演
│   │   └── scripts/               # 确定性操作脚本
│   │       ├── scan_templates.py
│   │       ├── score_document.py
│   │       ├── generate_filename.py
│   │       └── increment_version.py
│   └── agents/
│       └── backend-k8s-architect.md
├── templates/                     # 文档模板（spec-writer 自动扫描）
│   ├── all_in_one.template.md     # 单文件：BRD + PRD + Design Spec
│   ├── brd_prd.template.md        # 单文件：BRD + PRD（无技术方案）
│   ├── hld_backend.template.md    # 分片：后端架构设计（10 个分片文档）
│   └── examples/                  # 示例文档
├── depot/                         # 生成的文档仓库
│   └── {team}/{project}/          # 按团队/项目组织
│       └── drafts/                # 草稿（已 gitignore）
├── sandbox/                       # 临时文件
└── temp/                          # 临时文件
```

## 技术栈

- Markdown（文档）+ YAML（metadata）+ JSON（草稿）
- Python 脚本（确定性操作）
- Claude Code Skills + Agents

## 模板系统架构

### 两种输出模式

| 模式 | 模板 | 说明 |
|------|------|------|
| **单文件** | all_in_one, brd_prd | 一个 `.template.md` → 一个输出文档 |
| **分片** | hld_backend | 一个模板 → 多个分片文档，按 `depends_on` 拓扑排序生成 |

### 模板→执行引擎协议

spec-writer 从模板文件提取指令驱动对话流程：

| 模板标记 | 执行引擎行为 |
|---------|------------|
| `supported_sections: [...]` (YAML) | 确定对话轮次和章节名 |
| `[填写说明]` (Markdown 粗体) | 每轮对话的引导提示 |
| `（spec-writer 指令）` (章节标题) | 触发特殊行为（推荐、校验、跳过、图表等） |
| `output_mode: "sharded"` (YAML) | 启用分片输出模式 |
| `shards: [...]` (YAML) | 分片定义、依赖关系、条件跳过 |
| `condition: "..."` (shards[]) | 条件跳过判断 |
| `depends_on: [...]` (shards[]) | 确定生成顺序 |
| `output_artifacts` (YAML) | 附加产物（metadata.json, changelog.jsonl） |
| `version_policy` (YAML) | 版本管理策略 |

### 分片模板规则（hld_backend）

当 `output_mode: "sharded"` 时：
1. 按 `shards[].depends_on` 拓扑排序确定生成顺序
2. 每个分片前检查 `condition` → 满足则生成，不满足则标记 `skipped`
3. 每个分片生成后执行一致性校验（服务名、接口、数据实体、术语、PRD 覆盖）
4. 同步生成 `output_artifacts` 中的附加产物

### 模板扩展

新模板放到 `templates/` 下即可，必须包含 YAML frontmatter（`template_version`, `template_name`, `template_type`）。章节分隔符使用 `───────────────────`。

## 文档命名与输出

**命名**：`{scope}_{project-name}_{type}_v{X.Y.Z}.md`

| 粒度 | 适用场景 |
|------|---------|
| `project` | 新项目立项 |
| `feature` | 新功能开发 |
| `enhance` | 功能优化 |
| `fix` | Bug 修复 |

**路径**：`depot/{team}/{project}/{document-name}.md`

**YAML Metadata 必填字段**：`spec_version`, `spec_type`, `spec_name`, `project_name`, `team`, `description`, `compatible_with`, `last_updated`, `changelog`

**版本号**：语义化版本（major.minor.patch）

## Scripts

通过 `python3 scripts/<script>.py [args]` 调用（工作目录为项目根目录）：

| 脚本 | 用途 | 调用时机 |
|------|------|---------|
| `scan_templates.py [--dir templates/]` | 扫描模板目录，输出 JSON | 选择模板时（优先使用） |
| `score_document.py` | 文档评分（4维度10分制） | 文档生成完成后 |
| `generate_filename.py` | 生成标准化文件名 | 保存文档时 |
| `increment_version.py` | 语义化版本号递增 | 更新文档版本时 |

模板扫描优先使用脚本获取确定性结果。如脚本不可用，降级为手动 Glob + Read 解析。

## 草稿系统

- **格式**：JSON，存储在 `depot/{team}/{project}/drafts/draft-{timestamp}.json`
- **触发**：用户中断对话时自动保存，或用户显式请求
- **恢复**：读取 JSON → 展示进度概要 → 从断点章节继续
- `depot/*/*/drafts/` 已加入 `.gitignore`

## 文档评分（10 分制）

仅评估方案论证质量，不评估项目管理内容：

| 维度 | 权重 | 检查重点 |
|------|------|---------|
| 形式完整性 | 40% (4.0) | 章节齐全、metadata 完整、格式规范 |
| 内容逻辑性 | 30% (3.0) | BRD→PRD→Design 一致性、无矛盾 |
| 可操作性 | 20% (2.0) | 技术方案可落地、验收标准明确 |
| 文档规范 | 10% (1.0) | 命名规范、路径规范、相关文档链接 |

详细检查项见 `.claude/skills/spec-writer/references/scoring_criteria.md`。

## 相关文档

- **Skill 定义**：`.claude/skills/spec-writer/SKILL.md`
- **模板使用指南**：`templates/README.md`
- **用户教程**：`README.md`
- **示例文档**：`templates/examples/`
