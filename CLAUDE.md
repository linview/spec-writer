# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Spec Writer** 是一个 AI 驱动的工程规范文档生成系统，通过对话式交互帮助开发者快速创建高质量的工程规范文档（方案论证专用）。

**核心特点**：
- 对话式文档创建（非手动填空）
- 智能推断推荐（基于前置知识推荐 80% 内容）
- 自动文档评分（10 分制评估）
- 草稿管理（支持断点续写）

## 快速开始

### 使用 spec-writer Skill 创建文档

```bash
# 启动 spec-writer Skill
/spec-writer

# 通过对话告诉 AI 你的需求
You: 我想创建一个新功能的方案文档
AI: 好的，我来帮你创建。请选择文档模板：
     - all_in_one（BRD + PRD + Design Spec 三段论）
     - brd_prd（BRD + PRD 两段论，不包含技术方案）

You: all_in_one
AI: 请选择文档粒度：
     - project（新项目立项）
     - feature（新功能开发）
     - enhance（功能优化）
     - fix（Bug 修复）

You: feature
[继续对话...]
```

**关键点**：
- ✅ 使用 `/spec-writer` 启动 skill
- ✅ 通过对话交互完成文档编写
- ❌ 不要手动复制模板填空
- ❌ 不要使用 `/spec new` 等命令（与 Claude Code 冲突）

### 提供前置知识（强烈推荐）

**为什么重要**：
- 无前置知识：AI 推荐准确度 60%
- 有前置知识（父文档）：AI 推荐准确度 90%+

**支持的前置知识类型**：
- ✅ 本地文档（父文档、依赖文档）
- ✅ 在线文档 URL
- ✅ 网页 URL
- ✅ 代码仓库

## 项目结构

```
spec-writer/
├── .claude/
│   ├── skills/                    # Skill 定义目录
│   │   ├── spec-writer/           # 核心技能：文档编写
│   │   ├── developer/             # 开发工作技能
│   │   ├── architect/             # 架构师工作技能
│   │   ├── qa/                    # QA 工作技能
│   │   ├── scrum_master/          # Scrum Master 技能
│   │   └── simple-admin-workflow/ # Simple Admin 工作流
│   ├── agents/                    # Agent 定义
│   └── settings.local.json        # 本地权限配置
├── templates/                     # 文档模板目录
│   ├── all_in_one.template.md     # All-in-One 三段论文档模板
│   └── examples/                  # 示例文档
├── depot/                         # 生成的文档仓库
│   ├── devops/                    # DevOps 团队文档
│   │   ├── ci-health-tracker/     # CI Health Tracker 项目
│   │   └── dev-closeup/           # Dev-Closeup 项目
│   └── team-a/                    # Team A 团队文档
├── sandbox/                       # 沙盒目录（临时文件）
├── temp/                          # 临时文件目录
└── test_reports/                  # 测试报告目录
```

## 文档模板系统

### 模板架构

**多模板支持**：spec-writer 会自动扫描 `templates/` 目录，支持多种文档模板。

**模板选择逻辑**：
1. 扫描 `templates/` 目录下所有 `.template.md` 文件
2. 解析每个模板的 YAML frontmatter（`template_version`, `template_type`, `supported_sections`）
3. 根据用户需求推荐最合适的模板
4. 用户也可以手动指定模板

**模板 Metadata 结构**：
```yaml
---
template_version: "1.1.0"        # 模板版本（语义化版本）
template_name: "brd_prd"         # 模板唯一标识
template_type: "requirement_spec" # 模板类型
description: "BRD + PRD 两段论文档"
supported_sections:              # 支持的章节列表
  - prerequisites
  - brd
  - prd
  - business_flow
  - ui_ux
  - next_steps
compatible_with: "spec-writer v1.1"
last_updated: "2026-03-30"
changelog:                       # 版本变更记录
  - version: "1.1.0"
    date: "2026-03-30"
    changes: "添加流程图/时序图建议提醒"
---
```

### 可用模板

#### 1. All-in-One 模板（all_in_one.template.md v1.1.0）

**定位**：方案论证专用文档（不包含项目管理内容）

**章节结构**：
```
1. BRD（业务需求描述） - 为什么做
   - 需求背景、客户是谁、预期收益、ROI 分析

2. PRD（产品需求描述） - 做什么
   - 功能范围、用户场景、功能需求、非功能需求

3. Design Spec（技术方案设计） - 怎么做
   - 前端设计、后端设计、数据库/中间件设计

4. 技术实施要点
   - 技术依赖、集成方式、技术风险、验收要点

5. 技术债务与已知问题
   - 技术债务、已知问题、未来优化

6. 相关文档
   - 父文档、子特性、依赖文档、参考资料
```

#### 2. BRD+PRD 模板（brd_prd.template.md v1.1.0）

**定位**：业务需求和产品需求两段论文档（不包含技术方案）

**章节结构**：
```
1. 前置知识（可选）
   - 父文档、代码仓库、技术栈文档、参考资料

2. BRD（业务需求描述）
   - 需求背景、客户是谁、预期收益、ROI 分析

3. PRD（产品需求描述）
   - 功能范围/边界、用户画像、用户故事、功能需求、非功能需求

4. 📐 流程图建议（醒目提醒）
   - 强烈建议生成业务流程图和时序图

5. 业务流程可视化（可选）
   - 业务流程图、业务时序图

6. UI/UX 需求（可选）

7. 后续建议
   - 技术方案设计、项目管理
```

**适用场景**：
- 需要先明确业务和产品需求，技术方案后续再独立设计
- 产品经理与业务方沟通，不涉及技术细节
- 需要生成业务流程图和时序图，但不涉及技术架构

**与 All-in-One 的区别**：
- ✅ 更强调流程图/时序图的重要性（有醒目提醒）
- ✅ 不包含技术方案设计（前端/后端/数据库）
- ✅ 适合产品经理、业务分析师使用

### 文档命名规范

**格式**：`{scope}_{project-name}_{type}_v{X.Y.Z}.md`

| 粒度 | 适用场景 | 示例 |
|------|---------|------|
| **project** | 新项目立项 | `ci-health-tracker_project_v1.0.0.md` |
| **feature** | 新功能开发 | `ci-health-tracker_feature-dashboard_v1.0.0.md` |
| **enhance** | 功能优化 | `dev-closeup_enhancements_domain_v1.0.0.md` |
| **fix** | Bug 修复 | `ci-health-tracker_fix_sync-bug_v1.0.0.md` |

**文档路径**：`depot/{team}/{project}/{document-name}.md`

### 文档 Metadata

每个文档必须包含 YAML metadata：

```yaml
---
spec_version: "1.0.0"
spec_type: "feature"  # project | feature | enhance | fix
spec_name: "artifact-label-model"
project_name: "研发闭环（DevOps）"
team: "devops"
description: "制品标签体系设计方案"
compatible_with: "spec-writer v1.1"
last_updated: "2026-03-11"
changelog:
  - version: "1.0.0"
    date: "2026-03-11"
    changes: 初始版本
---
```

## 文档边界说明

### ✅ spec-writer 负责写什么？

**方案论证文档**（BRD + PRD + Design Spec）：
- 为什么做（业务痛点、预期收益、ROI 分析）
- 做什么（功能范围、用户场景、功能需求、非功能需求）
- 怎么做（前端设计、后端设计、数据库设计）
- 技术实施要点（技术依赖、集成方式、技术风险、验收要点）
- 技术债务与已知问题

### ❌ spec-writer 不写什么？

**项目管理内容**（交给 scrum_master Skill）：
- Sprint Plan（任务分解、Story-001/002...）
- 工期估算（Story-001: 3天, @张三）
- 里程碑（M1: Day 3, M2: Day 7）
- 交付验收（UAT 测试、发布）

**为什么分离？**
- 方案论证 = 解决问题（业务价值 + 产品设计 + 技术方案）
- 项目管理 = 交付过程（任务排期 + 人力分配 + 进度控制）

## Skill 协作流程

### Phase 1: 方案论证（spec-writer Skill）

```bash
/spec-writer
You: 创建 CI Health Tracker Dashboard 功能方案文档

→ 生成: ci-health-tracker_feature-dashboard_v1.0.0.md
→ 包含: BRD、PRD、Design Spec、技术实施要点
→ 评分: 9.5/10
→ 耗时: 8 分钟
```

### Phase 2: 项目管理（scrum_master Skill）

```bash
/scrum_master
You: 基于方案文档 ci-health-tracker_feature-dashboard_v1.0.0.md 创建 Sprint Plan

→ 生成: sprint-plan-sprint23.md
→ 包含: Story 分解、任务分配（Story-001: 3天, @张三）
→ 里程碑: M1 (Day 3), M2 (Day 7)
```

## 草稿系统架构

**草稿格式**：JSON，存储在 `depot/{team}/{project}/drafts/`

**草稿结构**：
```json
{
  "draft_id": "draft-20260227-103000",
  "template": "all_in_one v1.1.0",
  "metadata": {
    "project_name": "ci-health-tracker",
    "spec_type": "feature",
    "spec_name": "dashboard"
  },
  "progress": {
    "completed_sections": ["brd"],
    "current_section": "prd_scope",
    "pending_sections": ["prd_user_stories", "design_spec", "appendix"]
  },
  "content": {
    "brd": { ... },
    "prd": { ... }
  },
  "context": {
    "parent_doc": "ci-health-tracker_project_v1.0.0.md",
    "tech_stack": ["Python 3.8+", "FastAPI", "React"]
  }
}
```

**草稿使用流程**：

**保存草稿**：
```
/spec-writer
You: 保存当前进度
AI: 💾 草稿已保存
     路径：depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json
     当前进度：
       ✓ 已完成：BRD
       ⏳ 进行中：PRD - 功能范围
       ⏳ 待完成：Design Spec、附录
```

**恢复草稿**：
```
/spec-writer
You: 恢复草稿 depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json
AI: 📂 已恢复草稿
     上次进度：
       ✓ 已完成：BRD
       ⏳ 进行中：PRD - 功能范围
     从断点继续：PRD - 功能范围/边界
```

**草稿位置**：`depot/{team}/{project}/drafts/`（已加入 .gitignore）

## 文档评分标准

spec-writer 会自动对生成的文档进行评分（10 分制）：

| 评分维度 | 权重 | 评估标准 |
|---------|------|---------|
| **形式完整性** | 4.0/4.0 | 章节完整、metadata 完整、格式规范 |
| **内容逻辑性** | 3.0/3.0 | BRD/PRD/Design 逻辑一致、需求可追溯 |
| **可操作性** | 2.0/2.0 | 技术方案清晰、验收标准明确 |
| **文档规范** | 1.0/1.0 | 命名规范、路径规范、相关文档链接 |

**示例评分报告**：
```
总分: 8.5/10
分项得分：
  形式完整性：4.0/4.0 ✓
  内容逻辑性：2.5/3.0 ⚠️
    建议：补充"投入成本详细构成"
  可操作性：1.5/2.0 ⚠️
    建议：补充"数据模型详细设计"
  文档规范：0.5/1.0 ⚠️
    建议：补充"相关文档"章节
```

## 最佳实践

### ✅ DO（推荐做法）

1. **使用 spec-writer Skill**
   - ✅ 通过 `/spec-writer` 启动
   - ✅ 通过对话告诉 AI 你的需求
   - ✅ 接受智能推断推荐（80% 内容）

2. **提供前置知识**
   - ✅ 读取父文档，AI 推荐准确度提升 30%+
   - ✅ 支持本地文档、在线 URL、网页 URL

3. **及时保存草稿**
   - ✅ 对话过程中随时中断
   - ✅ 下次通过对话恢复草稿

### ❌ DON'T（避免做法）

1. **不要手动填空**
   - ❌ 不要复制模板手动填写
   - ✅ 使用 `/spec-writer` 让 AI 引导你

2. **不要使用错误的命令**
   - ❌ `/spec new`、`/spec create` 等（与 Claude Code 冲突）
   - ✅ 直接 `/spec-writer` 然后对话

3. **不要混淆职责**
   - ❌ 不要在方案文档中写"工期 2 周，2 人"
   - ✅ 项目管理内容交给 scrum_master Skill

## 常见问题

### Q: 如何检查存量文档是否符合规范？

```bash
/spec-writer
You: 请检查这个文档是否符合规范：depot/devops/old-project/xxx.md
AI: 好的，我来检查这个文档...
     使用模板: all_in_one.template.md v1.1.0
     发现 3 个问题：
       1. 缺失章节：技术实施要点
       2. 字段未填：ROI 分析
       3. 格式问题：YAML metadata 缺少 spec_type

     是否交互式补充？
```

### Q: 如何给现有文档评分？

```bash
/spec-writer
You: 请给这个文档评分：depot/devops/my-project/xxx.md
AI: 好的，我来评估这个文档...
     总分: 8.5/10
     [评分详情...]
```

### Q: 文档版本如何管理？

使用语义化版本（Semantic Versioning）：`v{major}.{minor}.{patch}`

- **major**：不兼容的架构变更
- **minor**：向后兼容的功能新增
- **patch**：向后兼容的问题修正

**示例**：
- `v1.0.0` → `v1.1.0`：新增技术实施要点章节
- `v1.0.0` → `v2.0.0`：重构文档结构（不兼容变更）

## 相关文档

- **模板使用指南**：[templates/README.md](templates/README.md)
- **spec-writer Skill 文档**：[.claude/skills/spec-writer/SKILL.md](.claude/skills/spec-writer/SKILL.md)
- **示例文档**：[templates/examples/all_in_one.example.md](templates/examples/all_in_one.example.md)
- **项目主文档**：[README.md](README.md)

## 技术栈

- **Language**: Markdown (文档), YAML (metadata), JSON (草稿)
- **Tools**: Claude Code, Claude Skills
- **Version Control**: Git
- **Documentation Format**: Markdown + YAML Frontmatter

## 系统架构

### spec-writer Skill 工作原理

**核心能力**：
1. **模板扫描引擎**：自动扫描 `templates/` 目录，解析 YAML metadata
2. **智能推断引擎**：基于前置知识（父文档、在线文档）推荐 80% 内容
3. **对话式引导**：逐个章节引导用户填写，支持"全部接受/部分接受/拒绝"
4. **完整性检查**：对比模板结构，识别缺失章节
5. **评分引擎**：4 维度评分（形式完整性、内容逻辑性、可操作性、文档规范）

**工作流程**：
```
用户启动 /spec-writer
    ↓
扫描 templates/ 目录
    ↓
展示可用模板列表
    ↓
用户选择模板（或 AI 推荐）
    ↓
解析模板 YAML metadata
    ↓
询问：是否提供前置知识？
    ↓
[如果提供] 读取父文档/在线文档
    ↓
提取上下文（技术栈、已有功能、业务领域）
    ↓
展示计划概要（章节列表）
    ↓
用户确认能否实现？
    ↓
逐章对话式填写（带进度条）
    ├─ 智能推断推荐（需确认）
    ├─ 用户可以随时中断
    └─ 保存草稿
    ↓
完整性检查（对比模板）
    ↓
文档评分（10 分制）
    ↓
生成文档到 depot/
```

### 模板扩展机制

**添加新模板**：
1. 在 `templates/` 目录创建 `xxx.template.md`
2. 添加 YAML frontmatter（必须包含 `template_version`, `template_name`, `template_type`）
3. 定义章节结构（使用 `─────────────────── 分隔符`）
4. 重新启动 spec-writer，自动识别新模板

**模板兼容性检查**：
- spec-writer 检查 `compatible_with` 字段
- 如果模板版本不兼容，提示用户升级 spec-writer 或降级模板

## 开发注意事项

1. **模板更新**：
   - 修改模板时，务必更新 `template_version`（语义化版本）
   - 在 `changelog` 中记录变更
   - 如果是 breaking change，更新 major 版本号

2. **模板维护**：
   - 所有模板必须包含 YAML frontmatter
   - 章节分隔符使用 `───────────────────`
   - 填写说明使用 `**[填写说明]**：` 格式

3. **草稿管理**：
   - `depot/*/*/drafts/` 已加入 `.gitignore`
   - 草稿文件自动命名为 `draft-{timestamp}.json`
   - 恢复草稿时保留完整的上下文信息

4. **文档迁移**：
   - v1.0.0 文档仍可使用，但建议升级到 v1.1.0 模板
   - 迁移时需要更新 YAML metadata 字段（`spec_version`, `spec_type` 等）

5. **权限管理**：
   - `.claude/settings.local.json` 配置了允许的 Bash 命令和 WebSearch 权限
   - 添加新的 Bash 命令权限时，确保符合最小权限原则

## 版本历史

### v1.1.1 (2026-03-30)

**模板优化**：
- ✅ 新增：`brd_prd.template.md v1.1.0`（BRD + PRD 两段论文档）
- ✅ 改进：在 PRD 结束后添加醒目提醒，强调生成流程图/时序图
- ✅ 改进：完善 CLAUDE.md 架构说明（模板系统、草稿系统、工作流程）

### v1.1.0 (2026-02-27)

**重大变更**：明确文档边界为"方案论证专用"
- ✅ 新增：技术实施要点（替代实施计划）
- ✅ 新增：技术债务与已知问题（替代风险与待办）
- ✅ 移除：项目管理内容（里程碑、任务排期、人力分配）
- ✅ 改进：spec-writer 智能推断边界说明
- ✅ 改进：文档评分标准（不评估项目管理内容）
- ✅ 修正：使用方式改为通过 `/spec-writer` 对话（而非错误的 `/spec` 命令）
