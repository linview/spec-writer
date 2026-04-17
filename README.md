# Doc Template - AI 驱动的工程规范文档生成系统

> ⚠️ **重要**：这不是让你手动填空的模板！
>
> 本系统由 **Claude spec-writer Skill** 驱动，通过**对话式交互**自动生成工程规范文档。
>
> **你只需要与 AI 对话，它会引导你完成文档编写。**

---

## 🎯 一分钟上手

```bash
# 启动 spec-writer Skill
/spec-writer

# AI 会引导你通过对话完成文档
# 大约 5-10 分钟，生成完整的方案论证文档
```

**核心特点**：
- ✅ **对话式创建**：AI 逐个问题引导你完成文档
- ✅ **智能推断**：基于你提供的前置知识（父文档、在线文档），AI 自动推荐 80% 的内容
- ✅ **自动评分**：文档生成后自动评分（10 分制），指出需要改进的地方
- ✅ **草稿管理**：随时保存草稿，支持断点续写

---

## 🤖 如何使用 spec-writer Skill

### 正确的使用方式

```bash
# Step 1: 启动 spec-writer Skill
/spec-writer

# Step 2: 通过对话告诉 AI 你想做什么
# 示例对话：
```

**对话示例 1：创建新文档**
```
You: 我想创建一个新功能的方案文档
AI: 好的，我来帮你创建。请选择文档粒度：
     - project（新项目立项）
     - feature（新功能开发）
     - enhance（功能优化）
     - fix（Bug 修复）

You: feature
AI: 好的，请填写项目信息：
     项目名称：[输入]
     特性名称：[输入]
     团队：[输入]

[AI 继续引导你填写其他信息...]
```

**对话示例 2：检查存量文档**
```
You: 请检查这个文档是否符合规范：depot/devops/old-project/xxx.md
AI: 好的，我来检查这个文档...
     使用模板: all_in_one.template.md v1.1.0
     发现 3 个问题：
       1. 缺失章节：技术实施要点
       2. 字段未填：ROI 分析
       3. 格式问题：YAML metadata 缺少 spec_type

     是否交互式补充？

You: 是
[AI 引导你补充缺失内容...]
```

**对话示例 3：评分现有文档**
```
You: 请给这个文档评分：depot/devops/my-project/xxx.md
AI: 好的，我来评估这个文档...

     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     📊 文档评分报告
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     总分: 8.5/10

     分项得分：
       形式完整性：4.0/4.0 ✓
       内容逻辑性：2.5/3.0 ⚠️
         建议：补充"投入成本详细构成"
       可操作性：1.5/2.0 ⚠️
         建议：补充"数据模型详细设计"
       文档规范：0.5/1.0 ⚠️
         建议：补充"相关文档"章节

     改进建议：
       1. [必须] 补充"投入成本详细构成"
       2. [建议] 补充"数据模型详细设计"
       3. [建议] 补充"相关文档"章节
```

### ❌ 错误的使用方式

**不要使用这些命令**（与 Claude Code 冲突）：
```bash
# ❌ 错误：/spec 会被 Claude 识别为 Skill 名称
/spec new
/spec create
/spec score

# ✅ 正确：直接与 spec-writer 对话
/spec-writer
You: 我想创建一个新文档
```

---

## 📚 使用教程

### 场景 1：创建新功能方案文档（最常见）

```bash
# Step 1: 启动 spec-writer
/spec-writer

# Step 2: 通过对话告诉 AI 你的需求
You: 我想为 CI Health Tracker 创建一个 Dashboard 功能的方案文档

# Step 3: AI 引导你完成文档创建
AI: 好的，我来帮你创建。请确认项目信息：
     项目名称：ci-health-tracker
     特性名称：dashboard
     团队：devops
     输出路径：depot/devops/ci-health-tracker/ci-health-tracker_feature-dashboard_v1.0.0.md

     是否正确？

You: 是

AI: 是否提供前置知识？可以提高推荐准确度
     支持的类型：
       - 本地文档（父文档、依赖文档）
       - 在线文档 URL
       - 网页 URL
       - 跳过

You: 读取父文档 depot/devops/ci-health-tracker/ci-health-tracker_project_v1.0.0.md

AI: ✓ 已读取父文档
     - 技术栈: Python 3.8+, FastAPI, React
     - 已有功能: CLI 工具、数据同步、报告生成
     - 业务领域: CICD

     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     Step 4/13: BRD - 需求背景
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     [智能推断推荐 📘 来源于父文档]
       - 业务痛点：现有 CLI 工具不够直观，需要可视化界面
       - 为什么要做：提升排障效率 30%

     选项：
       □ 全部接受
       □ 部分接受（手动修改）
       □ 拒绝推荐，手动填写

You: 全部接受

AI: ✓ 已记录

     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     Step 5/13: BRD - 客户是谁
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     [智能推断推荐 📘 来源于父文档]
       - 目标客户：DevOps 团队（继承父文档）
       - 投入成本：待定

You: 全部接受，但补充一下投入成本
     时间：2 周
     人力：1 人

AI: ✓ 已记录

     [继续填写其他章节...]

AI: ✅ 文档已生成
     路径: depot/devops/ci-health-tracker/ci-health-tracker_feature-dashboard_v1.0.0.md
     评分: 9.5/10

     分项得分：
       形式完整性：4.0/4.0 ✓
       内容逻辑性：3.0/3.0 ✓
       可操作性：2.0/2.0 ✓
       文档规范：0.5/1.0 ⚠️
         建议：补充"相关文档"章节链接
```

**实际耗时**：
- 有前置知识：5-8 分钟（AI 推荐 80% 内容）
- 无前置知识：15-20 分钟（手动输入较多）

---

### 场景 2：保存和恢复草稿

```bash
# 启动 spec-writer
/spec-writer

# 保存草稿
You: 保存当前进度

AI: 💾 草稿已保存
     路径：depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json
     当前进度：
       ✓ 已完成：BRD
       ⏳ 进行中：PRD - 功能范围
       ⏳ 待完成：Design Spec、附录

# 恢复草稿（下次对话时）
/spec-writer

You: 恢复草稿 depot/devops/ci-health-tracker/drafts/draft-20260227-103000.json

AI: 📂 已恢复草稿
     上次进度：
       ✓ 已完成：BRD
       ⏳ 进行中：PRD - 功能范围

     从断点继续：PRD - 功能范围/边界
```

---

## 💡 高效使用技巧

### 1. 提供前置知识（⚠️ 强烈推荐）

**为什么重要**：
- 无前置知识：AI 推荐准确度 60%
- 有前置知识（父文档）：AI 推荐准确度 **90%+**

**支持的前置知识类型**：
- ✅ 本地文档（父文档、依赖文档）
- ✅ 在线文档 URL（如 https://docs.example.com/prd）
- ✅ 网页 URL（如 GitHub README）

**示例对话**：
```
AI: 是否提供前置知识？

You: 是，读取父文档 depot/devops/ci-health-tracker/ci-health-tracker_project_v1.0.0.md

AI: ✓ 已读取父文档
     - 技术栈: Python 3.8+, FastAPI, React
     - 已有功能: CLI 工具、数据同步、报告生成
     - 业务领域: CICD

     [AI 基于这些信息，后续推荐会非常准确]
```

### 2. 利用智能推断

**AI 可以自动推断**：
- ✅ 技术栈（继承父文档）
- ✅ 功能范围（自动排除已有功能）
- ✅ 数据模型（复用父文档表结构）
- ✅ 风险点（结合父文档已知风险）

**AI 不会推断**（需要你提供）：
- ❌ 工期估算、人力分配（留给 scrum_master）
- ❌ 具体的业务细节（你最清楚）

### 3. 对话式交互的优势

```
传统方式（手动填空）：
❌ 复制模板 → 填写 100+ 个字段 → 不知道写得好不好 → 格式容易不规范

spec-writer Skill（对话式）：
✅ AI 引导 → 智能推荐 80% 内容 → 自动评分 → 格式自动规范
```

---

## 🎯 文档边界说明

### ✅ spec-writer 负责写什么？

**方案论证文档**（BRD + PRD + Design Spec）：

```markdown
## 📋 BRD（业务需求描述）
- 为什么做（业务痛点、预期收益、ROI 分析）

## 📱 PRD（产品需求描述）
- 做什么（功能范围、用户场景、功能需求、非功能需求）

## 🔧 Design Spec（技术方案设计）
- 怎么做（前端设计、后端设计、数据库设计）

─────────────────── 技术实施要点 ───────────────────
### 4. 技术实施要点
- 技术依赖（外部依赖、内部依赖、环境依赖）
- 集成方式（与现有系统集成）
- 技术风险（技术风险、性能风险、安全风险）
- 验收要点（功能验收、性能验收、安全验收）

─────────────────── 技术债务与已知问题 ───────────────────
## ⚠️ 技术债务与已知问题
- 技术债务（代码重构、架构优化）
- 已知问题（技术问题和限制）
- 未来优化（技术优化方向）
```

### ❌ spec-writer 不写什么？

**项目管理内容**（交给 scrum_master Skill）：

```markdown
## Sprint Plan（由 scrum_master 负责）
- 任务分解（Story-001, Story-002...）
- 工期估算（Story-001: 3天, @张三）
- 里程碑（M1: Day 3, M2: Day 7）
- 交付验收（UAT 测试、发布）
```

**为什么分离？**
- 方案论证 = **解决问题**（业务价值 + 产品设计 + 技术方案）
- 项目管理 = **交付过程**（任务排期 + 人力分配 + 进度控制）

---

## 🔗 角色协作：spec-writer vs scrum_master

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: 方案论证（spec-writer Skill）                   │
│  ├─ 通过对话创建方案论证文档                              │
│  ├─ 包含：BRD + PRD + Design Spec                        │
│  ├─ 耗时：5-15 分钟                                      │
│  └─ 输出：depot/{team}/{project}/xxx_spec_v1.0.0.md      │
└─────────────────────────────────────────────────────────┘
                           ↓
                    [方案评审通过]
                           ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 2: 项目管理（scrum_master Skill）                  │
│  ├─ 基于方案文档创建 Sprint Plan                         │
│  ├─ 包含：任务分解、工期估算、里程碑                      │
│  └─ 输出：sprint-plan-sprint23.md                        │
└─────────────────────────────────────────────────────────┘
```

### 实际案例

**阶段 1：使用 spec-writer 创建方案文档**
```bash
/spec-writer
You: 创建 CI Health Tracker Dashboard 功能方案文档

→ 生成: ci-health-tracker_feature-dashboard_v1.0.0.md
→ 包含: BRD、PRD、Design Spec、技术实施要点
→ 评分: 9.5/10
→ 耗时: 8 分钟
```

**阶段 2：使用 scrum_master 创建 Sprint Plan**
```bash
/scrum_master
You: 基于方案文档 ci-health-tracker_feature-dashboard_v1.0.0.md 创建 Sprint Plan

→ 生成: sprint-plan-sprint23.md
→ 包含: Story 分解、任务分配（Story-001: 3天, @张三）
→ 里程碑: M1 (Day 3), M2 (Day 7)
```

---

## 📂 文档存储结构

```
doc-template/
├── depot/                                    # AI 生成的文档仓库
│   ├── devops/                               # 团队
│   │   └── ci-health-tracker/                # 项目
│   │       ├── ci-health-tracker_project_v1.0.0.md
│   │       ├── ci-health-tracker_feature-dashboard_v1.0.0.md
│   │       └── drafts/                       # 草稿目录（gitignore）
│   │           └── draft-20260227-103000.json
├── templates/                                # 模板目录（AI 读取）
│   ├── all_in_one.template.md                # AI 使用的模板
│   └── examples/                             # 示例文档
│       └── all_in_one.example.md
├── .claude/
│   └── skills/
│       └── spec-writer/
│           └── SKILL.md                      # AI 的行为定义
└── README.md                                 # 本文件
```

### 文档命名规范

**格式**：`{scope}_{project-name}_{type}_v{X.Y.Z}.md`

| 粒度 | 适用场景 | 对话示例 |
|------|---------|---------|
| **project** | 新项目立项 | "创建一个新项目方案文档" |
| **feature** | 新功能开发 | "为 CI Health Tracker 创建 Dashboard 功能方案" |
| **enhance** | 功能优化 | "创建性能优化方案文档" |
| **fix** | Bug 修复 | "创建数据同步 bug 的修复方案" |

---

## 💡 最佳实践

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

---

## 📚 参考文档

- **模板使用指南**：[templates/README.md](templates/README.md)
- **spec-writer Skill 文档**：[.claude/skills/spec-writer/SKILL.md](.claude/skills/spec-writer/SKILL.md)
- **示例文档**：[templates/examples/all_in_one.example.md](templates/examples/all_in_one.example.md)

---

## 📝 更新日志

### v1.1.0 (2026-02-27)

**重大变更**：明确文档边界为"方案论证专用"

- ✅ **新增**：技术实施要点（替代实施计划）
- ✅ **新增**：技术债务与已知问题（替代风险与待办）
- ✅ **移除**：项目管理内容（里程碑、任务排期、人力分配）
- ✅ **改进**：spec-writer 智能推断边界说明
- ✅ **改进**：文档评分标准（不评估项目管理内容）
- ✅ **修正**：使用方式改为通过 `/spec-writer` 对话（而非错误的 `/spec` 命令）

**迁移指南**：
- v1.0.0 文档仍可使用，但建议升级到 v1.1.0 模板
- 项目管理内容请迁移到 scrum_master Skill

---

**🎉 开始使用 spec-writer，让 AI 帮你写文档！**

```bash
/spec-writer
```
