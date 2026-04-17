---
skill: "spec-writer"
description: "工程规范文档编写技能 - 通过对话式交互创建、检查、评分工程规范文档（方案论证专用）"
version: "1.2.0"
author: "Claude"
last_updated: "2026-03-30"
capabilities:
  - "对话式文档创建"
  - "存量文档检查与补充"
  - "文档质量评分（10分制）"
  - "草稿保存与恢复"
  - "智能推断推荐"
  - "多模板支持"
compatible_templates:
  - "all_in_one v1.1+"
  - "api_spec"
  - "architecture"
workflow:
  - "模板扫描与选择"
  - "对话式填写章节"
  - "智能推断推荐"
  - "完整性检查"
  - "文档评分"
  - "生成到 depot/"
document_boundary:
  focus: "方案论证（BRD + PRD + Design Spec）"
  not_include:
    - "项目管理内容（里程碑、任务排期、人力分配）"
    - "过程管理内容（交付验收标准、迭代规划）"
  delegated_to:
    - "scrum_master agent（项目管理）"
---

# Spec Writer 工作技能

## 📋 核心职责

Spec Writer 是一个**对话式文档编写助手**，帮助开发者通过自然语言交互完成工程规范文档的编写、检查和优化。

### 主要功能

1. **📝 对话式创建文档**：引导用户通过对话完成文档编写
2. **🔍 存量文档检查**：对比模板，识别缺失章节并交互式补充
3. **📊 文档质量评分**：评估文档完整性、逻辑性、可操作性、规范性（10分制）
4. **💾 草稿管理**：保存和恢复草稿（JSON格式）
5. **🤖 智能推断推荐**：推荐内容，需用户确认后写入
6. **📂 多模板支持**：自动扫描 `templates/` 目录，支持多种模板

---

## 🎯 工作流程

### 工作流程概览

```mermaid
graph TD
    A[启动 Skill] --> B{选择工作模式}
    B -->|创建新文档| C[扫描模板目录]
    B -->|检查存量文档| D[读取现有文档]
    B -->|评分文档| E[读取待评分文档]

    C --> F[用户选择模板]
    F --> G[解析模板 metadata]
    G --> H[根据模板设置的流程内容，\n对话式填写章节]

    D --> I[对比模板结构]
    I --> J[识别缺失章节]
    J --> K[交互式补充]

    H --> L[智能推断推荐]
    L --> M[用户确认]
    M --> N[生成文档]
    N --> O[文档评分]

    K --> N
    E --> O

    O --> P[保存到 depot/]
    H -.->|用户中断| Q[保存草稿]
    Q --> R[保存到 drafts/]
```

### 1️⃣ 对话式创建文档（Plan Mode 风格）

**工作流程**

```
阶段 1：准备工作（Plan Mode 风格）
├─ Step 0: 选择模板文件
├─ Step 1: 提供前置知识（背景文档）
├─ Step 2: 展示计划概要
└─ Step 3: 用户确认（能否实现？）

阶段 2：对话式创建（显示进度条）
├─ Step 4-N: 基于模板文件预设的问题流程，轮询式对话确认每个章节
│   ├─ 每个回合底部显示进度条
│   ├─ 智能推断推荐（需确认）
│   └─ 保存草稿（可选中断）
└─ Step N+1: 检查完整性（章节级别）

阶段 3：文档生成
├─ Step N+2: 生成文档到 depot/{team}/{project}/
└─ Step N+3: 评分并给出改进建议
```

---

#### Step 0: 模板扫描与选择

**动作**：
1. 扫描 `templates/` 目录，发现所有 `.template.md` 文件
2. 读取每个模板的 YAML metadata
3. 列出可用模板供用户选择

**输出示例**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 欢迎使用 Spec Writer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: 准备阶段

Step 1/4: 选择模板文件

可用模板（从 templates/ 扫描）：
  1. all_in_one.template.md        # All-in-One 三段论文档
  2. api_spec.template.md          # API 规范文档
  3. architecture.template.md      # 架构设计文档

选项：
  □ 从列表选择（输入序号 1-3）
  □ 使用默认模板（all_in_one.template.md）

User: [选择 1]

✓ 已加载模板：all_in_one.template.md (v1.1)
  包含章节：BRD、PRD、Design Spec、附录
```

**实现要点**：
- 使用 `Glob` 工具扫描 `templates/**/*.template.md`
- 使用 `Read` 工具读取每个模板的前 50 行，解析 YAML metadata
- 提取 `template_name`、`description`、`supported_sections` 字段

---

#### Step 1: 提供前置知识（⚠️ **重要**）

**触发时机**：在 BRD 需求背景之前（Step 2/4）

**为什么重要**：
- 无前置知识：AI 推荐准确度 60%
- 有前置知识（父文档）：AI 推荐准确度 **90%+**

**输出示例**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2/4: 提供前置知识（可选）⚠️ 强烈推荐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

为了提供更准确的智能推断，建议提供背景知识。

前置知识来源：
  □ 本地文档路径（如父文档、依赖文档）
  □ 在线文档 URL（如 https://docs.example.com/prd）
  □ 网页 URL（如 GitHub README）
  □ 跳过

检测到可能的父文档：
  depot/devops/ci-health-tracker/ci-health-tracker_feature-cli_v1.0.0.md

选项：
  □ 读取父文档
  □ 输入自定义路径
  □ 跳过

User: [选择] 读取父文档

✓ 已读取父文档：ci-health-tracker_feature-cli_v1.0.0.md
  - 技术栈：Python 3.8+, Click, SQLite, GitLab API
  - 业务领域：CICD
  - 已有功能：CLI 工具、数据同步、报告生成
  [已加载到上下文，用于智能推断]
```

**前置知识对智能推断的影响**：

| 推断目标 | 无前置知识 | 有前置知识（父文档） |
|---------|----------|-------------------|
| **技术栈推荐** | 通用技术栈（60% 准确） | 继承父文档（90% 准确） |
| **功能范围** | 手动输入 | 自动排除已有功能 |
| **命名规范** | 手动输入 | 继承父文档规范 |
| **实施计划** | 通用模板 | 参考父文档经验 |
| **风险评估** | 通用风险列表 | 结合父文档已知风险 |

---

#### Step 2: 选择文档粒度和基本信息

**动作**：询问用户文档粒度

**输出示例**：
```
Step 1/5: 选择文档粒度

  □ project（新项目立项）- 独立文档
  □ domain（跨项目业务领域）- 独立文档 + 关联到项目
  ☑ feature（新功能开发）- 独立文档 + 更新父文档
  □ enhance（功能优化）- 更新父文档 + 变更说明
  □ fix（Bug 修复）- 更新父文档 + PATCH 版本

[用户确认]
```

**命名规范**：
- 格式：`{project-name}_{type}_{summary}_v{X.Y.Z}.md`
- 示例：
  - `ci-health-tracker_project_overview_v1.0.0.md`
  - `ci-health-tracker_feature_dashboard_v1.0.0.md`
  - `ci-health-tracker_fix_sync-loss_v1.0.1.md`

---

#### Step 3: 展示计划概要（⚠️ **Plan Mode 风格**）

**触发时机**：前置知识收集完成之后

**动作**：根据模板文件展示完整的引导流程

**输出示例**：
all_in_one.template.md 内包含了 16 个问题概要，输出完整步骤，让用户了解整个对话流程。

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4/4: 计划概要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

将通过以下步骤创建文档：

Phase 1: BRD (4 个问题)
  1. BRD.background (需求背景)
  2. BRD.customer (客户是谁)
  3. BRD.benefits (预期收益)
  4. BRD.roi (是否值得做)

Phase 2: PRD (4 个问题)
  5. PRD.scope (功能范围)
  6. PRD.scenario (用户场景) ⚠️ 新增
  7. PRD.features (功能需求)
  8. PRD.non_functional (非功能需求)

Phase 3: Design Spec (4 个问题)
  9. Design.frontend (前端设计)
  10. Design.backend (后端设计)
  11. Design.database (数据库设计)
  12. Design.engineering_info (工程类前置知识) ⚠️ 新增

Phase 4: 技术实施要点 (4 个问题)
  13. Implementation.dependencies (技术依赖)
  14. Implementation.integration (集成方式)
  15. Implementation.risks (技术风险)
  16. Implementation.acceptance (验收要点)

总计：16 个问题 | 预计耗时：15-20 分钟

能否开始？
  ☑ 是，开始创建

User: [确认]
```

**说明**：
- ⚠️ 用户必须明确确认后才能开始对话（Plan Mode 风格）
- 显示预计耗时，让用户有心理准备

---

#### Step 4: 对话式创建（带进度条显示）⚠️ **重点改进**

**进度条格式**：

```
┌──────────────────────────────────────────┐
│ BRD.background (1/16), next: BRD.customer│
└──────────────────────────────────────────┘
```

- **格式**：`{当前章节}.{当前小节} ({当前步骤}/{总步骤}), next: {下一章节}.{下一小节}`
- **显示位置**：每个对话回合的底部
- **作用**：让用户清楚知道当前所在的位置，整体的进度，以及下一步要回答的问题。

**完整对话示例**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 2: 对话式创建
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────┐
│ BRD.background (1/16), next: BRD.customer│
└──────────────────────────────────────────┘

当前问题：BRD.background (需求背景)

业务痛点是什么？为什么做这个功能？

[智能推断推荐 📘 来源于父文档]
  - 现有 CLI 工具不够直观，需要可视化界面
  - 缺乏实时监控，排障效率低

选项：
  □ 接受推荐
  □ 手动输入

User: [输入] 现有 CLI 工具需要查看大量日志，排障效率低，需要可视化界面

✓ BRD.background 已完成

┌──────────────────────────────────────────┐
│ BRD.benefits (2/16), next: BRD.roi       │
└──────────────────────────────────────────┘

当前问题：BRD.customer (客户是谁)

目标客户是谁？投入成本是多少？

[智能推断推荐 📘 来源于父文档]
  - 目标客户：DevOps 团队（继承父文档）
  - 开发人力：2 人（参考父文档）

选项：
  □ 接受推荐
  □ 手动输入

User: [接受]

✓ BRD.customer 已完成

[继续 Q3、Q4...]

┌──────────────────────────────────────────┐
│ PRD.scope (5/16), next: PRD.features     │
└──────────────────────────────────────────┘

当前问题：PRD.scope (功能范围/边界)

选项：
  □ 继续下一个 Tab（输入 next）
  □ 查看本 Tab 汇总（输入 summary）
  □ 修改已回答的问题（输入 edit Q1-Q4）

User: [输入] next

✓ 切换到 PRD 章节

┌──────────────────────────────────────────────┐
│ Design.frontend (9/16), next: Design.backend │
└──────────────────────────────────────────────┘

当前问题：Design.frontend (前端设计)

⚠️ 即将进入 Design Spec 阶段，是否需要提供工程类前置知识？

功能范围内应该包含什么？不包含什么？

[智能推断推荐 📘📗 来源于父文档 + 项目类型]
  In Scope:
    - Dashboard 可视化（新增功能）
    - 实时数据刷新（新增功能）

  Out Scope:
    - Pipeline 监控（父文档已有，自动排除）
    - 失败分析（父文档已有，自动排除）

选项：
  □ 接受推荐
  □ 调整范围
  □ 手动输入

User: [接受]

[继续 Q6-Q13...]
```

---

**Tab 式交互模拟**（CLI 适配版）：

| Tab | 章节 | 问题数 | 说明 |
|-----|------|--------|------|
| Tab 1 | BRD | 4 | 需求背景、客户、预期收益、ROI |
| Tab 2 | PRD | 4 | 功能范围、用户场景、功能需求、非功能需求 |
| Tab 3 | Design Spec | 4 | 前端、后端、数据库、工程信息 |
| Tab 4 | Implementation | 4 | 技术依赖、集成方式、技术风险、验收要点 |

**交互命令**：
- `next` - 切换到下一个章节
- `summary` - 查看截止目前的问答汇总
- `edit Q{n}` - 修改已回答的问题
- `back` - 返回上一个章节 

**进度计算逻辑**：

```python
def calculate_progress(draft):
    """计算当前进度百分比"""
    total_questions = 16  # 总长度根据*.template.md的问题数量动态计算

    completed_questions = sum(
        1 for section in draft["progress"].values()
        for status in section.values()
        if status == "completed"
    )

    percentage = (completed_questions / total_questions) * 100

    # 获取下一个问题
    next_question = get_next_question(draft["progress"])

    return {
        "current": completed_questions,
        "total": total_questions,
        "percentage": percentage,
        "next": next_question  # 格式：Section.subsection，如 "BRD.benefits"
    }

def get_next_question(progress):
    """获取下一个待回答的问题"""
    section_order = ["brd", "prd", "design_spec", "implementation"] # 根据*.template.md的章节顺序动态生成
    subsection_order = {
        "brd": ["background", "customer", "expected_benefits", "roi_analysis"],
        "prd": ["scope", "user_scenarios", "features", "non_functional"],
        "design_spec": ["frontend", "backend", "database", "engineering_info"],
        "implementation": ["dependencies", "integration", "risks", "acceptance"]
    }

    for section in section_order:
        if section not in progress:
            continue
        for subsection in subsection_order[section]:
            if progress[section].get(subsection) != "completed":
                return f"{section}.{subsection}"

    return "completed"
```

---

**草稿恢复时的进度显示**：

```
📂 恢复草稿

草稿 ID：draft-20260227-103000
创建时间：2026-02-27 10:30:00
最后修改：2026-02-27 11:15:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
进度概要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ BRD.background（已完成）
✓ BRD.customer（已完成）
⏳ BRD.benefits（进行中）
⏸️ BRD.roi（待处理）
⏸️ PRD.scope（待处理）
...

当前进度：4/16 (25%), next: BRD.benefits
  - 已完成：3 个问题
  - 进行中：0 个问题
  - 待处理：13 个问题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文档类前置知识
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 已加载父文档：ci-monitor_platform_v1.0.0.md
  - 技术栈：Go, PostgreSQL, Redis
  - 业务领域：ci-monitor

是否从此处继续？
  ☑ 是，继续填写
  □ 修改已完成内容
  □ 查看完整草稿内容

User: [确认] 是，继续填写

✓ 从 4/16 继续

┌──────────────────────────────────────────┐
│ BRD.roi (4/16), next: PRD.scope          │
└──────────────────────────────────────────┘

当前问题：BRD.roi (回报率)
...
```

**动作**：轮询式确认每个章节

**流程**：
1. **前置知识提供**（⚠️ **在 BRD 需求背景之前**）
   - 询问用户是否需要提供前置知识
   - 支持本地文档、在线 URL、网页 URL
   - 读取并提取关键信息，用于后续智能推断

2. **轮询式确认每个章节**
   - 读取模板中的所有章节
   - 按顺序询问用户
   - 对每个章节：
     - 检查是否可以跳过（如 CLI 工具项目跳过 UI/UX）
     - 尝试智能推断推荐（基于前置知识）
     - 用户确认或手动输入
   - 记录已完成的章节

**⚠️ 文档边界说明**：

在开始对话之前，必须明确 **all_in_one** 等 spec 文档模板的定位：

```
✅ spec 文档聚焦：方案论证
  - BRD（业务需求描述）：为什么做（Why）
  - PRD（产品需求描述）：做什么（What）
  - Design Spec（技术方案设计）：怎么做（How）
  - 技术实施要点：技术依赖、集成方式、技术风险、验收要点
  - 技术债务与已知问题：技术债务、已知问题、未来优化

❌ spec文档不包含：项目管理内容
  - 里程碑定义、任务排期、人力分配
  - 交付验收标准、迭代规划
  - 进度风险、资源风险

👉 项目管理内容请使用 scrum_master agent
```

**智能推断边界**：
- ✅ **推荐推断**：技术栈、数据模型、接口设计、技术风险
- ❌ **不推断**：工期估算、人力分配、里程碑规划（留给 scrum_master）

---

**前置知识提供示例**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 3/5: 提供前置知识（可选）⚠️ **新功能**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

为了提供更准确的智能推断，建议提供背景知识。

前置知识来源：
  □ 本地文档路径（如父文档、依赖文档）
  □ 在线文档 URL（如 https://docs.example.com/prd）
  □ 网页 URL（如 GitHub README）
  □ 跳过

检测到可能的父文档：
  depot/devops/ci-health-tracker/ci-health-tracker_feature-cli_v1.0.0.md

选项：
  □ 读取父文档
  □ 输入自定义路径
  □ 跳过

User: [选择] 读取父文档

✓ 已读取父文档：ci-health-tracker_feature-cli_v1.0.0.md
  - 技术栈：Python 3.8+, Click, SQLite, GitLab API
  - 业务领域：CICD
  - 已有功能：CLI 工具、数据同步、报告生成
  [已加载到上下文，用于智能推断]
```

**输出示例**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4/5: 填写 BRD - 需求背景
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[智能推断推荐]
根据项目类型（CLI 工具 + 后端 API），推断可能的需求背景：
  业务痛点：CI 失败难以定位，每周花费 10+ 小时排查
  为什么要做：提升故障定位效率

选项：
  □ 全部接受
  □ 部分接受（手动修改）
  □ 拒绝推荐，手动填写

User: [全部接受]

✓ 已记录"需求背景"

---

Step 5/5: 填写 PRD - 功能范围

是否需要 UI/UX 设计章节？
  □ 是（有 Web UI 界面）
  ☑ 否（CLI 工具项目）

✓ 已记录"不需要 UI/UX"到待办事项
```

**章节跳过规则**：
- CLI 工具项目 → 跳过 UI/UX 章节
- 纯后端 API 项目 → 跳过 UI/UX 章节
- 功能级文档（feature/enhance/fix）→ 可跳过 BRD 的某些章节

---

#### Step 4: 智能推断推荐

**推断场景**：

| 场景 | 推断内容 | 数据来源 |
|------|---------|---------|
| **技术栈** | 前端框架、后端框架、数据库 | 项目类型、团队技术栈 |
| **实施计划** | 阶段划分、里程碑 | 功能需求复杂度 |
| **风险点** | 技术风险、进度风险 | 技术栈、功能复杂度 |
| **数据模型** | 核心表结构、字段 | 功能需求、业务领域 |

**推断流程**：
```
1. 分析项目类型（Web/CLI/API）
2. 分析已有内容（BRD/PRD）
3. 查询参考文档（如有）
4. 生成推荐内容
5. 展示给用户
6. 用户确认（全部接受/部分接受/拒绝）
7. 写入文档
```

**输出示例**：
```
🤖 智能推断：技术栈推荐

根据以下信息：
  - 项目类型：CLI 工具 + 后端 API
  - 团队技术栈：Python
  - 性能要求：中等

推荐技术栈：
  - 前端：Python 3.10 + Click（CLI 工具）
  - 后端：Python 3.10 + FastAPI
  - 数据库：PostgreSQL（支持复杂查询）
  - 缓存：Redis（高性能 KV 存储）

选项：
  □ 全部接受
  □ 部分接受（手动修改）
  □ 拒绝推荐，手动填写

User: [全部接受]

✓ 已写入"技术栈"章节
```

---

#### Step 5: 工程类前置知识收集（⚠️ **新增功能**）

**触发时机**：进入 Design Spec 章节之前（Q9/16 之前）

**目的**：
- 绿地项目：跳过工程信息收集，基于通用最佳实践推断
- 棕地项目：收集现有工程信息，提供更准确的技术方案推荐

**项目类型判断流程**：

```
┌──────────────────────────────────────────────┐
│ Design.frontend (9/16), next: Design.backend │
└──────────────────────────────────────────────┘

⚠️ 即将进入 Design Spec 阶段

项目类型判断：
  □ 绿地项目（Greenfield）- 全新项目，无需提供工程信息
  ☑ 棕地项目（Brownfield）- 存量项目迭代，需要提供工程背景

User: [选择] 棕地项目
```

**模式选择**（标准模式 vs 快速模式）：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
工程类前置知识收集（棕地项目）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **安全声明**：spec-writer 严禁更改任何外部代码库/数据库/中间件/配置的内容。
spec-writer 是只读角色，仅限于调研评估工程背景使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
模式选择
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

选择调研模式：
  □ 标准模式（Standard Mode）- 深度调研，适合中小型项目
  ☑ 快速模式（Quick Mode）- 轻量级调研，保证响应速度 ⚠️ 推荐

【模式对比】

| 维度 | 标准模式 | 快速模式 ⚠️ |
|------|---------|-----------|
| **代码库调研** | 扫描全部代码文件 | 仅读 CLAUDE.md, README.md |
| **数据库调研** | 完整 Schema + 索引 + 约束 | DB/Table List + 粗略 ER 关系 |
| **中间件调研** | 配置文件 + 服务拓扑 | 上下游服务分析 |
| **调研时间** | 5-10 分钟（大型项目更长） | 1-2 分钟 |
| **适用场景** | 中小型项目（<10K 行代码） | 大型项目或快速场景 |

⚠️ **为什么推荐快速模式？**
- 避免加载过大代码工程，保证输出速度
- 大部分工程信息可以从 CLAUDE.md/README.md 获取
- 如需详细信息，可在后续对话中按需展开

User: [选择] 快速模式
```

**结构化表单收集**（快速模式示例）：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
快速模式 - 工程信息收集
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请填写以下工程信息（所有字段均为可选）：

【前端工程】（快速模式：仅读 CLAUDE.md, README.md）
  1. 前端代码库路径：__________________
     示例：/home/user/repos/my-project/frontend/
     访问方式：[本地文件系统] [Git仓库 URL]
     ⚠️ 快速模式：仅读取 CLAUDE.md, README.md

  2. 前端技术栈：__________________
     示例：React 18 + TypeScript + Ant Design
     ⚠️ 通常可从 README.md 获取

【后端工程】（快速模式：仅读 CLAUDE.md, README.md）
  3. 后端代码库路径：__________________
     示例：/home/user/repos/my-project/backend/
     访问方式：[本地文件系统] [Git仓库 URL]
     ⚠️ 快速模式：仅读取 CLAUDE.md, README.md

  4. 后端技术栈：__________________
     示例：Go 1.21 + Gin + GORM
     ⚠️ 通常可从 README.md 获取

【数据层】（快速模式：DB/Table List + 粗略 ER）
  5. 数据库类型：__________________
     选项：[PostgreSQL] [MySQL] [MongoDB] [Redis] [其他]

  6. 数据库连接方式（⚠️ 只读访问）：__________________
     示例：postgresql://user:pass@localhost:5432/dbname
     ⚠️ 注意：仅用于查询 schema 和数据模型，不会修改任何数据
     ⚠️ 快速模式：获取 DB List + Table List + 粗略 ER 关系

  7. 数据库 Schema 文档（可选）：__________________
     示例：/home/user/docs/database-schema.md
     或者：https://docs.example.com/database

【中间件】（快速模式：上下游服务分析）
  8. 消息队列：__________________
     示例：Kafka (localhost:9092)
     访问方式：[配置文件路径] [连接字符串]
     ⚠️ 快速模式：分析上下游服务（Topic 列表）

  9. 缓存系统：__________________
     示例：Redis (localhost:6379)
     访问方式：[配置文件路径] [连接字符串]
     ⚠️ 快速模式：分析 Key 命名规范和用途

【其他】
  10. 配置文件路径：__________________
      示例：/etc/my-project/config.yaml

  11. API 文档：__________________
      示例：https://api.example.com/docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
选项：
  ☑ 提交表单
  □ 跳过（绿地项目或稍后提供）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: [提交表单]

✓ 已记录工程类前置知识

  前端代码库：/home/user/repos/my-project/frontend/
  后端代码库：/home/user/repos/my-project/backend/
  数据库：PostgreSQL (只读访问)
  中间件：Kafka, Redis

  [工程信息已加载到上下文，用于智能推断]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 9/16: Design Spec - 前端设计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**只读安全约束**：

```yaml
security_constraints:
  read_only_operations:
    - 读取代码文件（Read tool）
    - 读取数据库 Schema（SELECT query，仅 metadata）
    - 读取配置文件（Read tool）
    - 读取 API 文档（WebFetch tool）

  forbidden_operations:
    - 修改代码文件（Edit/Write tool）
    - 修改数据库数据（INSERT/UPDATE/DELETE）
    - 修改配置文件
    - 修改中间件状态
```

**快速模式实现策略**：

```python
# 伪代码：快速模式读取策略

def quick_mode_engineering_research(form_data):
    """快速模式：轻量级工程调研（1-2 分钟）"""
    results = {}

    # 1. 前端代码库（仅读 CLAUDE.md, README.md）
    if form_data.get("frontend_repo"):
        frontend_path = form_data["frontend_repo"]
        claude_md = read_file(f"{frontend_path}/CLAUDE.md")
        readme_md = read_file(f"{frontend_path}/README.md")

        results["frontend"] = {
            "tech_stack": extract_tech_stack(readme_md),
            "project_structure": extract_structure(claude_md),
            "key_components": extract_components(claude_md),
            "status": "quick_scan_complete"
        }

    # 2. 后端代码库（仅读 CLAUDE.md, README.md）
    if form_data.get("backend_repo"):
        backend_path = form_data["backend_repo"]
        claude_md = read_file(f"{backend_path}/CLAUDE.md")
        readme_md = read_file(f"{backend_path}/README.md")

        results["backend"] = {
            "tech_stack": extract_tech_stack(readme_md),
            "api_structure": extract_api_structure(claude_md),
            "services": extract_services(claude_md),
            "status": "quick_scan_complete"
        }

    # 3. 数据库（DB/Table List + 粗略 ER）
    if form_data.get("database_dsn"):
        dsn = form_data["database_dsn"]
        db_list = query_databases(dsn)
        table_list = {}
        er_relationships = []

        for db in db_list:
            tables = query_tables(dsn, db)
            table_list[db] = tables

            for table in tables:
                foreign_keys = query_foreign_keys(dsn, db, table)
                er_relationships.extend(foreign_keys)

        results["database"] = {
            "db_list": db_list,
            "table_list": table_list,
            "er_relationships": er_relationships,
            "status": "quick_scan_complete"
        }

    # 4. 中间件（上下游服务分析）
    if form_data.get("kafka_config"):
        kafka_config = load_config(form_data["kafka_config"])
        topics = extract_kafka_topics(kafka_config)

        results["kafka"] = {
            "topics": topics,
            "upstream_services": identify_upstream(topics),
            "downstream_services": identify_downstream(topics),
            "status": "quick_scan_complete"
        }

    return results
```

**按需展开示例**：

```
[文档生成过程中...]

📊 基于快速扫描结果，我推荐以下前端技术方案：

**组件复用建议** 🔧
  - 复用现有组件：Layout, DataTable
  - 新增组件：DashboardChart（ECharts 集成）

User: 能否详细分析一下 DataTable 组件的接口？

✓ 按需展开：深度扫描 DataTable 组件

⏳ 正在扫描 /home/user/repos/my-project/frontend/src/components/DataTable/

  ✓ DataTable.tsx (205 行)
  ✓ DataTable.types.ts (45 行)
  ✓ 扫描完成，耗时 3 秒

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DataTable 组件详细分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

组件接口：
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  pagination?: PaginationConfig;
  onRowClick?: (row: T) => void;
  loading?: boolean;
}
```

支持的特性：
- ✅ 分页（前端分页 + 后端分页）
- ✅ 排序（单列排序）
- ✅ 筛选（列筛选）
- ✅ 行选择（单选/多选）
- ❌ 虚拟滚动（不支持大数据量）

复用建议：
✅ DataTable 组件完全满足 Dashboard 需求，可以直接复用。

[继续文档生成...]
```

---

#### Step 5.5: PRD 用户场景推演（⚠️ **新增功能**）

**触发时机**：PRD.scope（功能范围）完成之后，PRD.features（功能需求）之前

**为什么重要**：
- ❌ 没有用户场景，方案设计缺少依据
- ❌ 验收标准定义模糊
- ❌ 开发过程容易偏离用户需求

**推演流程示例**：

```
┌──────────────────────────────────────────┐
│ PRD.features (6/16), next: PRD.scenario  │
└──────────────────────────────────────────┘

当前问题：PRD.scenario (用户场景/用例)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户场景推演（⚠️ 重要环节）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基于功能范围（In Scope）：
  - 功能 1：DevPod Debug Scheduler 调度策略
  - 功能 2：Debug Slot 资源池管理
  - 功能 3：调度优先级算法

我将引导你推演 3-5 个典型用户场景。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
场景 1/3：开发人员请求调试 Pod
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【用户画像】
  - 角色：开发人员
  - 技能水平：熟悉 Kubernetes，会使用 kubectl
  - 典型工作流：本地开发 → 提交 PR → CI/CD → 部署到测试环境

【场景描述】
  用户在开发过程中遇到 Bug，需要一个调试 Pod 来复现和定位问题。

【推演问题】
  Q1: 用户如何触发调试 Pod 请求？
    选项：
      □ CLI 命令（如 kubectl debug）
      □ Web UI 提交调试工单
      □ API 调用（集成到 CI/CD 流程）

    User: [选择] CLI 命令

    Q2: 用户需要提供哪些参数？
      推断：至少包含
        - namespace（部署环境）
        - target_pod（目标 Pod）
        - debug_image（调试镜像，如 ubuntu:latest）
        - duration（预计调试时长）

    Q3: 系统如何响应请求？
      推断：可能的响应
        ✓ 立即分配 Debug Slot（资源充足时）
        ⏳ 进入等待队列（资源不足时）
        ✗ 拒绝请求（超过优先级限制）

    Q4: 用户如何知道调试 Pod 就绪？
      推断：可能的反馈方式
        - CLI 输出 Pod 名称和状态
        - Web UI 显示进度条
        - 通知（如 Slack/Email）

[记录场景 1 详情...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
场景 2/3：Debug Slot 资源不足时的排队机制
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[继续推演...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
场景 3/3：调试超时自动清理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[继续推演...]

✓ 所有场景推演完成！
```

**场景推演模板**：

```markdown
### 场景 {编号}：{场景名称}

**用户画像**：
- 角色：{开发人员/测试人员/SRE/...}
- 技能水平：{熟悉 Kubernetes / 初学者 / ...}
- 典型工作流：{简述日常工作流程}

**场景描述**：
{用户在什么情况下，遇到什么问题，需要使用这个功能}

**操作步骤**：
1. 步骤 1：{用户操作}
   - 输入：{参数、命令}
   - 系统响应：{反馈信息}

2. 步骤 2：{用户操作}
   - 输入：{参数、命令}
   - 系统响应：{反馈信息}

3. 步骤 3：{用户操作}
   - 输入：{参数、命令}
   - 系统响应：{反馈信息}

**预期结果**：
- 成功情况：{期望的输出、状态变化}
- 失败情况：{可能的错误提示、降级方案}

**验收标准**（从场景提取）：
- [ ] {验收条件 1}
- [ ] {验收条件 2}
- [ ] {验收条件 3}
```

**智能推断场景**（基于功能范围）：

```
[智能推断推荐 📘📗 来源于功能范围 + 父文档]

基于功能范围（In Scope）：
  - 功能 1：DevPod Debug Scheduler 调度策略
  - 功能 2：Debug Slot 资源池管理
  - 功能 3：调度优先级算法

推断可能包含的用户场景：

🎯 场景 1：开发人员请求调试 Pod（高优先级）
  - 用户角色：开发人员
  - 触发条件：开发环境中遇到 Bug
  - 操作：CLI 命令提交调试请求
  - 预期：系统立即分配 Debug Slot（如果资源充足）

🎯 场景 2：测试人员调试失败 Test（中优先级）
  - 用户角色：测试人员
  - 触发条件：自动化测试失败，需要手动复现
  - 操作：Web UI 提交调试工单
  - 预期：进入等待队列，按优先级调度

🎯 场景 3：SRE 紧急调试生产问题（高优先级）
  - 用户角色：SRE
  - 触发条件：生产环境故障
  - 操作：CLI 命令 + `--priority=high`
  - 预期：抢占低优先级 Debug Slot

🎯 场景 4：Debug Slot 资源不足时的排队
  - 用户角色：任意
  - 触发条件：所有 Debug Slot 占用中
  - 操作：提交调试请求
  - 预期：进入等待队列，显示排队位置

🎯 场景 5：调试超时自动清理
  - 用户角色：系统自动触发
  - 触发条件：调试时长超过阈值（如 2 小时）
  - 操作：自动终止 Debug Pod
  - 预期：释放 Debug Slot，通知用户

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

选项：
  ☑ 全部接受（并基于场景生成验收标准）
  □ 部分接受（选择需要的场景）
  □ 拒绝推荐，手动输入

User: [选择] 全部接受

✓ 已接受场景推荐，正在生成验收标准...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
验收标准生成（基于场景）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基于场景 1（开发人员请求调试 Pod）：
  ✓ F-001.1：支持 CLI 命令 `kubectl debug` 提交调试请求
  ✓ F-001.2：参数包含 namespace, target_pod, debug_image, duration
  ✓ F-001.3：资源充足时，30 秒内分配 Debug Slot
  ✓ F-001.4：CLI 输出 Pod 名称和就绪状态

基于场景 2（测试人员调试失败 Test）：
  ✓ F-002.1：支持 Web UI 提交调试工单
  ✓ F-002.2：显示排队位置和预计等待时间
  ✓ F-002.3：按优先级算法排序调度

基于场景 3（SRE 紧急调试生产问题）：
  ✓ F-003.1：支持 `--priority=high` 参数
  ✓ F-003.2：高优先级请求抢占低优先级 Debug Slot
  ✓ F-003.3：被抢占用户收到通知和延长时长选项

[继续生成其他场景的验收标准...]

✓ 验收标准生成完成！
  共生成 15 个验收标准（5 个场景 × 平均 3 个标准/场景）

是否需要补充或调整？
  □ 是，需要修改
  ☑ 否，继续

User: [确认] 继续

✓ PRD.scenario 已完成

  - 用户场景：5 个
  - 验收标准：15 个
  - [已记录到文档]
```

**场景推演的关键问题**（确保覆盖完整）：

| 维度 | 推演问题 | 目的 |
|------|---------|------|
| **触发条件** | 用户在什么情况下使用这个功能？ | 明确使用场景边界 |
| **操作流程** | 用户需要执行哪些步骤？ | 设计交互流程 |
| **输入参数** | 用户需要提供哪些信息？ | 定义接口参数 |
| **系统响应** | 系统如何反馈？ | 定义响应格式 |
| **成功情况** | 期望的输出是什么？ | 定义成功标准 |
| **失败情况** | 可能的错误有哪些？ | 定义错误处理 |
| **边界条件** | 资源不足/超时/并发时如何处理？ | 定义降级方案 |

**场景推演检查清单**：

- [ ] **完整性**：是否覆盖了所有主要用户角色？
- [ ] **真实性**：场景是否符合用户日常工作流程？
- [ ] **可验证性**：每个场景是否可以转换为验收标准？
- [ ] **边界条件**：是否考虑了异常情况（资源不足、超时、并发）？
- [ ] **可操作性**：验收标准是否明确可测试？

---

#### Step 6: 生成文档并评分

**动作**：
1. 生成完整文档（包含 YAML metadata）
2. 保存到 `depot/{team}/{project}/`
3. 对文档进行评分

**输出示例**：
```
✅ 文档已生成

路径：depot/devops/ci-health-tracker/ci-health-tracker_project_overview_v1.0.0.md
版本：1.0.0

---

📊 文档评分报告

总分：8.5/10

分项得分：
  形式完整性：4.0/4.0 ✓
    - 所有章节齐全
    - 必填字段完整
    - YAML metadata 规范

  内容逻辑性：2.5/3.0 ⚠️
    - BRD 与 PRD 逻辑一致 ✓
    - 技术方案与需求对应 ✓
    - 建议：补充"投入成本详细构成"到 ROI 分析

  可操作性：1.5/2.0 ⚠️
    - 技术方案可落地 ✓
    - 建议：补充"实施计划负责人"

  文档规范：0.5/1.0 ⚠️
    - 文件命名符合规范 ✓
    - 建议：补充"相关文档"章节链接

改进建议：
  1. [必须] 补充"投入成本详细构成"到 ROI 分析
  2. [建议] 补充"实施计划负责人"
  3. [建议] 补充"相关文档"章节链接

是否根据建议更新文档？
  □ 是
  ☑ 否（稍后手动更新）
```

---

### 2️⃣ 存量文档检查

#### 启动流程

**输入**：`--existing docs/old-spec.md`

**输出示例**：
```
🔍 检查存量文档

现有文档：docs/old-spec.md

请选择用于对比的模板：
  1. all_in_one.template.md
  2. 输入自定义模板路径

User: [选择 1]

✓ 使用模板：all_in_one.template.md
  正在对比文档结构...

发现 3 个缺失章节：
  ❌ PRD → UI/UX 需求
  ⚠️ 字段未填：BRD → ROI 分析
  ⚠️ 格式问题：YAML metadata 缺少 spec_type

是否补充缺失内容？
  ☑ 是
```

#### 对比逻辑

**Step 1**: 读取现有文档，解析 YAML metadata
**Step 2**: 读取模板，获取完整章节结构
**Step 3**: 对比章节，识别缺失
**Step 4**: 交互式补充
**Step 5**: 更新版本号

**版本号规则**：
- **MAJOR**（1.0 → 2.0）：重大架构变更、新增 BRD/PRD 章节
- **MINOR**（1.0 → 1.1）：新增 Design Spec 子章节、补充字段
- **PATCH**（1.0 → 1.0.1）：修正错误、优化描述

**输出示例**：
```
Step 1/3: 补充 UI/UX 需求章节

[对话式填写...]

✓ 已补充"UI/UX 需求"章节

---

Step 2/3: 补充 ROI 分析

[智能推断推荐]
投入成本：
  - 时间：4 周
  - 人力：2 人
  - 金钱：$0

选项：
  □ 全部接受
  □ 部分接受
  □ 手动填写

User: [全部接受]

✓ 已补充"ROI 分析"

---

Step 3/3: 更新版本号

当前版本：1.0.0
变更类型：
  □ MAJOR（重大架构变更）
  ☑ MINOR（新增章节）
  □ PATCH（修正错误）

新版本：1.1.0

[确认] → [输出文档]

✅ 文档已规范化

输出：depot/devops/ci-health-tracker/ci-health-tracker_project_v1.1.0.md
版本：1.0.0 → 1.1.0
```

---

### 3️⃣ 文档评分

#### 评分体系（10分制）

**⚠️ 评分边界**：仅评估方案论证质量，不评估项目管理内容

| 维度 | 权重 | 检查项 | 满分 |
|------|------|--------|------|
| **形式完整性** | 40% | 章节齐全、必填字段完整、YAML metadata 规范 | 4.0 |
| **内容逻辑性** | 30% | 无矛盾、定义清晰、叙事准确 | 3.0 |
| **可操作性** | 20% | 技术方案可落地、技术实施要点明确 | 2.0 |
| **文档规范** | 10% | YAML、命名、格式正确 | 1.0 |

**说明**：
- **可操作性**评估：技术选型合理、数据模型清晰、接口定义完整、技术风险可控
- **不评估**：工期估算、人力分配、里程碑规划（留给 scrum_master）

#### 评分算法

```python
def evaluate_document(doc_path):
    doc = read_document(doc_path)

    scores = {
        "completeness": check_completeness(doc),       # 4.0 分
        "logic": check_logic_consistency(doc),         # 3.0 分
        "actionability": check_actionability(doc),     # 2.0 分
        "format": check_format_compliance(doc)         # 1.0 分
    }

    total_score = sum(scores.values())

    # 生成问题清单
    issues = identify_issues(doc, scores)

    # 生成改进建议
    recommendations = generate_recommendations(issues)

    return {
        "total_score": total_score,
        "scores": scores,
        "issues": issues,
        "recommendations": recommendations
    }
```

#### 问题分类

| 类型 | 说明 | 处理方式 |
|------|------|---------|
| **必须修复** | 影响文档使用，如缺失核心章节、关键逻辑错误 | 自动添加到"风险与待办"章节 |
| **建议改进** | 优化文档质量，如补充细节、优化表述 | 展示给用户，可选接受 |

---

### 4️⃣ 草稿管理

#### 草稿格式（JSON）

```json
{
  "draft_id": "draft-20260227-103000",
  "project_name": "CI Health Tracker",
  "template_used": "all_in_one",
  "template_version": "1.0.0",
  "created_at": "2026-02-27T10:30:00Z",
  "last_modified": "2026-02-27T11:15:00Z",
  "progress": {
    "current_section": "prd",
    "completed_sections": ["brd"],
    "pending_sections": ["prd", "design", "appendix"]
  },
  "metadata": {
    "team": "devops",
    "spec_type": "project",
    "spec_scope": "ci-monitor"
  },
  "content": {
    "brd": {
      "background": "CI 失败难以定位...",
      "customer": "DevOps 团队...",
      "expected_benefits": "效率提升 70%...",
      "roi_analysis": "ROI = 21.75..."
    },
    "prd": {
      "scope": "在范围内：..."
    }
  }
}
```

#### 保存草稿

**触发条件**：
- 用户输入 `/spec save`
- 对话过程中用户中断

**保存路径**：`depot/{team}/{project}/drafts/{draft_id}.json`

**输出示例**：
```
💾 保存草稿

草稿路径：depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json

当前进度：
  ✓ 已完成：BRD
  ⏳ 进行中：PRD
  ⏳ 待完成：Design Spec、附录

下次可使用以下命令恢复：
/spec resume --draft depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json
```

#### 恢复草稿

**输入**：`/spec resume --draft depot/.../draft-xxx.json`

**输出示例**：
```
📂 恢复草稿

草稿路径：depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json
创建时间：2026-02-27 10:30
上次修改：2026-02-27 11:15

当前进度：
  ✓ 已完成：BRD
  ⏳ 进行中：PRD
  ⏳ 待完成：Design Spec、附录

从断点继续：PRD - 功能范围/边界

[恢复对话...]
```

---

## 🤖 智能推断规则

### 推断数据来源

| 数据类型 | 来源 | 优先级 |
|---------|------|--------|
| **项目类型** | 用户输入、文档名称 | 高 |
| **团队技术栈** | 参考文档、用户输入 | 中 |
| **功能需求** | PRD 章节内容 | 高 |
| **业务领域** | project_name、用户输入 | 中 |

### 推断场景示例

#### 场景 1：推断技术栈

**条件**：
- 项目类型 = CLI 工具 + 后端 API
- 团队技术栈 = Python

**推断**：
```yaml
frontend:
  framework: "Python 3.10 + Click"
  reason: "CLI 工具标准技术栈"

backend:
  framework: "Python 3.10 + FastAPI"
  reason: "高性能异步框架，团队熟悉"

database:
  primary: "PostgreSQL"
  reason: "支持复杂查询，JSON 字段"
  cache: "Redis"
  reason: "高性能 KV 存储"
```

#### 场景 2：推断实施计划

**条件**：
- 功能需求 = 5 个（F-001 ~ F-005）
- 团队规模 = 2 人

**推断**：
```yaml
phases:
  - name: "阶段 1：基础框架"
    duration: "1 周"
    tasks: ["搭建 FastAPI 项目", "数据库 schema 设计", "GitLab API 集成"]

  - name: "阶段 2：核心功能"
    duration: "1.5 周"
    tasks: ["实现数据同步", "查询 API", "CLI 工具"]

  - name: "阶段 3：报告生成"
    duration: "0.5 周"
    tasks: ["报告统计逻辑", "Markdown 模板", "Redis 缓存"]
```

#### 场景 3：推断风险点

**条件**：
- 技术栈包含 GitLab API
- 团队规模 = 1 人

**推断**：
```yaml
risks:
  - type: "技术风险"
    description: "GitLab API 限流（429 错误）"
    impact: "中"
    mitigation: "实现指数退避重试，增加请求间隔"

  - type: "进度风险"
    description: "开发人力不足（只有 1 人）"
    impact: "低"
    mitigation: "与其他项目协调人力，或延长 1 周工期"
```

---

## 📁 文档结构

### depot/ 目录结构

```
depot/
├── {team}/                      # 团队/组织
│   ├── {project}/               # 项目
│   │   ├── {project}_{type}_v{X.Y.Z}.md    # 文档
│   │   └── drafts/              # 草稿目录（gitignore）
│   │       ├── draft-20260227-103000.json
│   │       └── draft-20260227-110000.json
│   └── {project2}/
│       └── ...
└── {team2}/
    └── ...
```

### 文档关联关系

**相关文档章节**：
```markdown
## 🔗 相关文档

- **父文档**：[文档路径](../)（如果存在）
- **子特性**：
  - [特性 1 文档路径](./)
  - [特性 2 文档路径](./)
- **依赖文档**：
  - [依赖文档路径](../../)
- **参考资料**：
  - [参考资料 1](____)
  - [参考资料 2](____)
```

---

## ✅ 验收标准

### 基础功能

- [ ] **TC-001**：模板扫描功能正确
  - 扫描 `templates/` 目录
  - 正确解析 YAML metadata
  - 列出可用模板

- [ ] **TC-002**：对话流程完整
  - 项目级文档：5 个步骤
  - 特性级文档：6 个步骤（需关联父文档）

- [ ] **TC-003**：章节跳过功能正常
  - CLI 工具项目自动跳过 UI/UX 章节

- [ ] **TC-004**：智能推断推荐
  - 根据项目类型推荐技术栈
  - 拒绝推荐后保留空白字段

- [ ] **TC-005**：草稿保存与恢复
  - 正确保存到 `depot/{team}/{project}/drafts/`
  - 从断点继续对话

- [ ] **TC-006**：文档评分功能正常
  - 10 分制评分
  - 生成问题清单和改进建议

- [ ] **TC-007**：存量文档检查
  - 对比模板结构
  - 识别缺失章节
  - 交互式补充

### 集成测试

- [ ] **测试场景 1**：新建项目文档
  - 模板：all_in_one.template.md
  - 粒度：project
  - 输出：depot/devops/ci-health-tracker/ci-health-tracker_project_v1.0.0.md
  - 评分：≥ 8/10

- [ ] **测试场景 2**：存量文档检查
  - 输入：docs/old-spec.md
  - 输出：depot/xxx/xxx_project_v1.1.0.md
  - 版本：1.0.0 → 1.1.0

- [ ] **测试场景 3**：草稿保存与恢复
  - 保存：depot/.../drafts/draft-xxx.json
  - 恢复：从断点继续

### 真实场景测试

- [ ] **CI Health Tracker 特性文档创建**
  - 项目：ci-health-tracker_feature-dashboard_v1.0.0.md
  - 粒度：feature
  - 评分：≥ 8.5/10

---

## 📐 文档格式规范

### 章节分隔符格式

**要求**：使用长分隔符分隔主要章节，便于 AI 按需加载

**格式**：
```
---
```

**示例**：
```markdown
## 📋 第一部分：业务需求描述（BRD）
...
---

## 📱 第二部分：产品需求描述（PRD）
...
---

## 🔧 第三部分：技术方案设计（Design Spec）
...
---

### 1. 前端设计（应用层/接入层）
...
---

### 2. 后端设计（服务层/调度层）
...
---

### 3. 数据库/中间件设计（服务层/中间层）
...
---

### 4. 实施计划
...
---

### 5. 风险评估
...
---

## 🔗 相关文档
...
---

## ⚠️ 风险与待办
...
---

## 📝 附录
```

**实现要点**：
- 模板文件（`.template.md`）必须使用长分隔符
- 生成的文档自动继承分隔符格式
- AI 可以根据分隔符按需加载指定章节

---

## 🔧 技术实现要点

### 模板扫描

```python
def scan_templates(template_dir="templates/"):
    """扫描模板目录，返回可用模板列表"""
    template_files = glob(f"{template_dir}/**/*.template.md", recursive=True)

    templates = []
    for file_path in template_files:
        metadata = parse_template_metadata(file_path)
        templates.append({
            "path": file_path,
            "name": metadata.get("template_name"),
            "description": metadata.get("description"),
            "sections": metadata.get("supported_sections", [])
        })

    return templates
```

### YAML Metadata 解析

```python
def parse_yaml_front_matter(file_path):
    """解析文件头部的 YAML metadata"""
    with open(file_path, 'r') as f:
        content = f.read()

    # 提取 YAML front matter（--- 之间）
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        return yaml.safe_load(yaml_content)

    return {}
```

### 文档命名

```python
def generate_filename(metadata):
    """根据 metadata 生成文档文件名"""
    scope = metadata.get("spec_type", "project")  # project/domain/feature/enhance/fix
    project_name = metadata.get("project_name", "unknown").lower().replace(" ", "-")
    doc_type = "feature" if scope in ["feature", "enhance", "fix"] else scope
    version = metadata.get("spec_version", "1.0.0")

    return f"{project_name}_{doc_type}_v{version}.md"
```

### 文档正文标题
**重要** 根据文档命名的type和summary内容 自动生成文档标题，替换模板文件首行的占位符 `{文档标题}`

例如: 
- 文件名: `ci-health-tracker_project_overview_v1.0.0.md`
- 文档标题: `# CI Health Tracker 项目概览` 


### 版本号更新

```python
def increment_version(current_version, change_type):
    """根据变更类型更新版本号"""
    major, minor, patch = map(int, current_version.split("."))

    if change_type == "MAJOR":
        major += 1
        minor = 0
        patch = 0
    elif change_type == "MINOR":
        minor += 1
        patch = 0
    elif change_type == "PATCH":
        patch += 1

    return f"{major}.{minor}.{patch}"
```

---

## 📚 参考资料

### 现有 Skill 格式参考

- `.claude/skills/developer/SKILL.md`
- `.claude/skills/architect/SKILL.md`

### 模板文件结构

- `templates/all_in_one.template.md`
- `templates/examples/all_in_one.example.md`

### 相关文档

- [Spec Writer Agent 实施计划](../../spec-writer_agent_plan.md)
- [工程规范文档模板使用指南](../templates/README.md)

---

**🎉 开始使用 Spec Writer，让文档编写更高效！**
