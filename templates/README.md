# 工程规范文档模板说明

> ⚠️ **重要提示**：这些模板由 **spec-writer skill** 使用，不是让你手动填空！
>
> 请使用 `/spec-writer` 通过对话让 AI 助手帮你生成文档。

---

## 📁 模板文件

| 文件 | 版本 | 输出模式 | 说明 |
|------|------|---------|------|
| `all_in_one.template.md` | v1.1.0 | 单文件 | All-in-One 三段论文档（BRD + PRD + Design Spec） |
| `brd_prd.template.md` | v1.1.0 | 单文件 | BRD + PRD 两段论文档（不含技术方案），适合产品经理/业务方 |
| `hld_backend.template.md` | v1.0.0 | **分片** | 后端架构设计文档（10 个分片），需配合 BRD/PRD 父文档使用 |
| `examples/all_in_one.example.md` | - | - | 示例文档（参考用） |

---

## 🎯 模板结构

### 1. All-in-One 模板（all_in_one.template.md v1.1.0）

**定位**：方案论证专用文档（不包含项目管理内容）

**章节结构**：

```
1. BRD（业务需求描述） - 为什么做
   - 需求背景、客户是谁、预期收益、ROI 分析

2. PRD（产品需求描述） - 做什么
   - 功能范围、用户场景、功能需求、非功能需求、UI/UX（可选）

3. Design Spec（技术方案设计） - 怎么做
   - 前端设计、后端设计、数据库/中间件设计

─────────────────── 技术实施要点 ───────────────────
4. 技术实施要点
   - 技术依赖、集成方式、技术风险、验收要点

─────────────────── 技术债务与已知问题 ───────────────────
5. 技术债务与已知问题
   - 技术债务、已知问题、未来优化

─────────────────── 相关文档 ───────────────────
6. 相关文档
   - 父文档、子特性、依赖文档、参考资料
```

### 2. BRD+PRD 模板（brd_prd.template.md v1.1.0）

**定位**：业务需求和产品需求两段论文档（不包含技术方案），适合产品经理/业务方使用。

**章节结构**：

```
1. 前置知识（可选）
2. BRD（业务需求描述）
3. PRD（产品需求描述）
4. 流程图建议（醒目提醒）
5. 业务流程可视化（可选）
6. UI/UX 需求（可选）
7. 后续建议
```

### 3. 后端架构设计模板（hld_backend.template.md v1.0.0）

**定位**：后端架构设计文档，从宏观到微观定义后端系统架构。**必须配合 BRD/PRD 父文档使用**。

**输出模式**：分片（`output_mode: "sharded"`）— 一个模板生成一组独立文件，每个分片可独立供 AI coding agent 消费。

**10 个分片**：

| 分片 | 文件名 | 条件 | 依赖 |
|------|--------|------|------|
| 全局字典 | `{project}_glossary_v{version}.md` | 必选 | 无 |
| 系统架构 | `{project}_system-architecture_v{version}.md` | 必选 | glossary |
| 数据模型 | `{project}_data-model_v{version}.md` | 有状态服务 | system_architecture |
| 服务功能 | `{project}_service-{service_name}_v{version}.md` | 必选（可多文件） | system_architecture, data_model |
| 接口协议 | `{project}_api-spec_v{version}.md` | 必选 | service_functions |
| 系统集成 | `{project}_integration_v{version}.md` | 必选 | interface_protocols |
| 部署方案 | `{project}_deployment_v{version}.md` | 必选 | system_architecture |
| 测试验收 | `{project}_test-plan_v{version}.md` | 必选 | service_functions, interface_protocols |
| 附加方案 | `{project}_{plan_name}_v{version}.md` | 有特化需求 | system_architecture |
| FAQ | `{project}_faq_v{version}.md` | 必选 | 无 |

**附加产物**：
- `metadata.json` — 分片组目录（状态跟踪）
- `changelog.jsonl` — 迭代历史（追加式）

**版本策略**：SemVer 2.0，初始版本 `0.1.0`。PRD 变更触发 minor bump，架构重构触发 major bump。

---

## 🔍 与传统文档的区别

| 传统项目文档 | all_in_one.template v1.1.0 |
|-------------|--------------------------|
| ❌ 包含项目管理内容（里程碑、任务排期） | ✅ **不包含**项目管理内容 |
| ❌ 混合方案论证和过程管理 | ✅ **聚焦**方案论证（BRD + PRD + Design） |
| ❌ 实施计划：阶段划分、工期估算 | ✅ 技术实施要点：技术依赖、集成方式、技术风险 |
| ❌ 风险评估：进度风险、资源风险 | ✅ **仅**技术风险、性能风险、安全风险 |
| ❌ 风险与待办：负责人、优先级 | ✅ 技术债务、已知问题、未来优化 |

---

## 💡 使用方式

### ⭐ 推荐：使用 spec-writer Skill（AI 驱动）

```bash
/spec-writer
```

通过对话告诉 AI 你想做什么，AI 会自动扫描模板、引导填写、智能推断、生成文档并评分。

### ❌ 错误的使用方式

```bash
# ❌ 错误：/spec 会被 Claude 识别为 Skill 名称
/spec new /spec create /spec score

# ✅ 正确：通过 /spec-writer 对话
/spec-writer
```

---

## 📝 版本变更

### v1.0.0 (2026-05-27) — templates/README.md

- 新增 `hld_backend.template.md` v1.0.0 声明（分片输出）
- 新增 `brd_prd.template.md` v1.1.0 声明
- 修正使用方式为 `/spec-writer`

### v1.1.0 (2026-02-27)

- 明确文档边界为"方案论证专用"
- 新增技术实施要点、技术债务与已知问题

---

## 🔗 相关文档

- **项目总 README**：[../README.md](../README.md)
- **spec-writer Skill**：[../.claude/skills/spec-writer/SKILL.md](../.claude/skills/spec-writer/SKILL.md)
- **示例文档**：[examples/all_in_one.example.md](examples/all_in_one.example.md)
