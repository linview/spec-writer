---
skill: "architect"
description: "架构师工作技能 - 架构设计、文档管理、语义化版本控制、设计审查"
version: "1.0"
---

# Architect 工作技能

## 核心职责

1. **架构设计**：设计系统架构、数据模型、服务层架构、应用层架构
2. **文档管理**：维护设计文档，遵循语义化版本管理规范
3. **技术决策**：制定技术选型、设计模式、最佳实践
4. **跨层协调**：协调系统层、数据层、服务层、应用层的设计一致性
5. **设计审查**：Review 设计文档，确保架构合理性和可实施性

---

## 📋 设计文档管理规范（铁律）

### ⚠️ 核心原则：语义化版本 + 层次分类 + 归档管理

**设计文档必须遵循以下规则**：

1. **按架构层次分类命名**：使用 `{layer}_design_{sem_ver}.md` 格式
2. **语义化版本号**：变更粒度直接体现在文件名版本部分
3. **归档管理**：旧版本归档到 `docs/design/archive/`
4. **禁止描述性命名**：不使用 plan、update、design 等临时文件名

---

## 文档命名规范

### 架构层次分类

| 架构层次 | 文档命名模式 | 示例 |
|---------|-------------|------|
| **系统架构** | `system_architecture_{sem_ver}.md` | `system_architecture_v1.0.md` |
| **数据层/CMDB** | `cmdb_design_{sem_ver}.md` | `cmdb_design_v2.3.md` |
| **服务层架构** | `service_layer_architecture_{sem_ver}.md` | `service_layer_architecture_v2.0.md` |
| **API/应用层** | `api_design_{sem_ver}.md` | `api_design_v1.0.md` |
| **FAQ 文档** | `{name}_faq_{sem_ver}.md` 或 `{name}_faq.md` | `service_layer_faq_v2.1.md` |

### 语义化版本规则

**版本格式**：`v{MAJOR}.{MINOR}.{PATCH}`

| 版本类型 | 版本号示例 | 变更类型 | 判断标准 |
|---------|-----------|---------|---------|
| **MAJOR** | v2.0 → v3.0 | 重大功能新增、架构变更 | 新增完整章节、表结构变更、接口重定义 |
| **MINOR** | v2.0 → v2.1 | 功能新增、向后兼容 | 新增小功能、配置项、优化项 |
| **PATCH** | v2.0 → v2.0.1 | Bug 修复、小改动 | 修正错误、补充说明、格式调整 |

**版本判断示例**：

| 变更内容 | 版本类型 | 示例 |
|---------|---------|------|
| 新增第 8 章：历史记录存储优化 | **MAJOR** | v2.0 → v3.0 |
| 新增配置项：历史记录保留期 | **MINOR** | v3.0 → v3.1 |
| 修正文档错误：章节编号错乱 | **PATCH** | v3.0 → v3.0.1 |
| 优化描述：补充代码示例 | **PATCH** | v3.0 → v3.0.1 |

### ❌ 禁止的命名方式

**以下命名方式严格禁止**：

1. ❌ 描述性语言命名的临时文件：
   - `history_storage_optimization_design_updates.md`
   - `history_storage_optimization_design_updates_CORRECTED.md`
   - `plan_20260204.md`
   - `design_update_phase1.md`
   - 任何带有 `plan`、`update`、`design`、`proposal` 等前缀的文件名

2. ❌ 不带版本号的文档：
   - `service_layer_architecture.md`（缺少版本号）
   - `cmdb_design.md`（缺少版本号）
   - `faq.md`（缺少版本号）

3. ❌ 使用日期作为版本号：
   - `service_layer_architecture_20260204.md`

**✅ 正确的命名方式**：

- ✅ `service_layer_architecture_v3.0.md`
- ✅ `cmdb_design_v2.4.md`
- ✅ `api_design_v1.2.md`
- ✅ `service_layer_faq_v3.0.md`

---

## 文档归档规范

### 归档时机

**每次 MAJOR 或 MINOR 版本更新时**，必须归档旧版本：

```bash
# 归档旧版本
mv docs/design/service_layer_architecture_v2.0.md \
   docs/design/archive/service_layer_architecture_v2.0_20260204.md
```

### 归档文件命名

**格式**：`{filename}_v{version}_{date}.{ext}`

| 组成部分 | 说明 | 示例 |
|---------|------|------|
| `{filename}` | 原文件名（不含版本号） | `service_layer_architecture` |
| `{version}` | 语义化版本号 | `v2.0` |
| `{date}` | 归档日期（YYYYMMDD） | `20260204` |
| `{ext}` | 文件扩展名 | `.md` |

**完整示例**：
- `service_layer_architecture_v2.0_20260204.md`
- `cmdb_design_v2.3_20260204.md`
- `api_design_v1.0_20260204.md`

### 默认保留位置

**`docs/design/` 目录只保留最新版本**：

```bash
# 正确的目录结构
docs/design/
├── system_architecture_v1.0.md          # 最新版本
├── cmdb_design_v2.3.md                    # 最新版本
├── service_layer_architecture_v3.0.md     # 最新版本
└── service_layer_faq_v3.0.md              # 最新版本

docs/design/archive/
├── system_architecture_v1.0_20260131.md   # 历史版本
├── cmdb_design_v2.2_20260201.md           # 历史版本
├── service_layer_architecture_v2.0_20260204.md  # 历史版本
└── service_layer_faq_v2.1_20260204.md      # 历史版本
```

---

## 文档更新流程

### Step 1: 确定变更类型

**判断版本号增量**：

| 变更内容 | 版本类型 | 文件名变化 |
|---------|---------|-----------|
| 新增完整章节（如第 8 章） | MAJOR | v2.0 → v3.0 |
| 表结构变更（DDL 脚本） | MAJOR | v2.3 → v3.0 |
| 接口重定义 | MAJOR | v1.0 → v2.0 |
| 新增配置项 | MINOR | v2.0 → v2.1 |
| 新增小功能 | MINOR | v2.0 → v2.1 |
| 修正错误 | PATCH | v2.0 → v2.0.1 |
| 补充说明 | PATCH | v2.0 → v2.0.1 |

### Step 2: 归档旧版本（如需要）

**MAJOR 或 MINOR 版本更新时**：

```bash
# 进入项目目录
cd /home/mini/Proj/llv/resource-meter

# 归档旧版本
mv docs/design/service_layer_architecture_v2.0.md \
   docs/design/archive/service_layer_architecture_v2.0_$(date +%Y%m%d).md
```

**PATCH 版本更新时**：
- 不归档（直接覆盖文件）

### Step 3: 创建新版本

**方式 1：复制旧版本（推荐）**

```bash
# 复制旧版本作为基础
cp docs/design/archive/service_layer_architecture_v2.0_20260204.md \
   docs/design/service_layer_architecture_v3.0.md

# 编辑新版本，更新内容
vim docs/design/service_layer_architecture_v3.0.md
```

**方式 2：直接创建新版本**

```bash
# 直接创建新版本
vim docs/design/service_layer_architecture_v3.0.md
```

### Step 4: 更新版本历史表

**在每个文档的开头更新版本历史表**：

```markdown
## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-02-02 | 初始版本 | Development Team |
| v2.0 | 2026-02-03 | 明确活跃 Pod GPU 实时计算实现规范 | QA + Development Team |
| v3.0 | 2026-02-04 | 新增历史记录存储优化（第 8 章） | Development Team |

**v3.0 主要变更**：
- ✅ 新增第 8 章：历史记录存储优化
- ✅ 表结构优化：pod_resource_history 字段精简
- ✅ 代码实现：EventProcessor 延迟 CREATE 记录
- ⚠️ 向后兼容：优化向后兼容，不影响现有功能
```

### Step 5: 更新相关文档

**如果更新涉及多个文档，保持版本号一致**：

| 主文档版本 | FAQ 文档版本 | 示例场景 |
|-----------|------------|---------|
| v3.0 | v3.0 | 主文档 MAJOR 更新，FAQ 同步更新 |
| v2.1 | v2.1 | 主文档 MINOR 更新，FAQ 同步更新 |
| v2.0.1 | 不变 | 主文档 PATCH 更新，FAQ 不变 |

---

## 文档结构规范

### 必需章节

**每个设计文档必须包含以下章节**：

1. **文档元数据**
   ```markdown
   # {文档标题} v{version}

   **文档版本**: v{version}
   **创建日期**: YYYY-MM-DD
   **作者**: {作者}
   **状态**: {状态}
   ```

2. **版本历史表**
   ```markdown
   ## 📋 版本历史

   | 版本 | 日期 | 变更说明 | 作者 |
   |------|------|---------|------|
   | v1.0 | YYYY-MM-DD | 初始版本 | {作者} |
   ```

3. **文档概述**
   ```markdown
   ## 📋 文档概述

   本文档描述了...
   ```

4. **核心内容章节**
   - 根据文档类型组织（架构设计、数据模型、API 设计等）

5. **变更日志（可选）**
   - 对于 PATCH 更新，可以添加变更日志

### 推荐章节结构

**system_architecture_{sem_ver}.md**：
```markdown
1. 架构概述
2. 技术栈
3. 部署架构
4. 网络拓扑
5. 安全设计
6. 监控告警
```

**cmdb_design_{sem_ver}.md**：
```markdown
1. 设计概述
2. 数据模型
3. 表结构设计
4. 索引设计
5. 数据字典
6. 迁移脚本
```

**service_layer_architecture_{sem_ver}.md**：
```markdown
1. 架构概述
2. K8s Informer 监听机制
3. Pod 生命周期处理流程
4. 状态机设计
5. GPU 用量计算
6. 活跃 Pod GPU 实时计算
7. K8s Event 日志输出
8. {新增章节}
```

**{name}_faq_{sem_ver}.md**：
```markdown
FAQ-1: {问题 1}
FAQ-2: {问题 2}
...
FAQ-N: {问题 N}
```

---

## 设计文档与 Story 的关系

### 双向追踪

**设计文档 → Story**：
- 每个设计文档可以对应多个 Story
- Story 引用设计文档的章节号

**Story → 设计文档**：
- Story 的实现会更新设计文档
- 设计文档的版本号要体现 Story 的变更

### 示例

```yaml
# Story 文档 (story-6-08-history-storage-optimization.md)
dependencies:
  - "STORY-6-04"
design_docs:
  - "docs/design/service_layer_architecture_v2.0.md#7-历史记录存储优化"
  - "docs/design/cmdb_design_v2.3.md#pod_resource_history"

# 实施完成后
design_updates:
  - "docs/design/service_layer_architecture_v3.0.md"  # v2.0 → v3.0
  - "docs/design/service_layer_faq_v3.0.md"          # v2.1 → v3.0
```

---

## 常见错误

### ❌ 错误 1：使用描述性文件名

```bash
# ❌ 错误：创建临时规划文件
vim docs/design/plan_20260204.md
vim docs/design/history_storage_optimization_design_updates.md
vim docs/design/proposal.md

# ✅ 正确：直接更新正式文档
vim docs/design/service_layer_architecture_v3.0.md
```

### ❌ 错误 2：不归档旧版本

```bash
# ❌ 错误：保留多个版本在 design/ 目录
docs/design/
├── service_layer_architecture_v1.0.md
├── service_layer_architecture_v2.0.md
└── service_layer_architecture_v3.0.md

# ✅ 正确：只保留最新版本
docs/design/
└── service_layer_architecture_v3.0.md

docs/design/archive/
├── service_layer_architecture_v1.0_20260131.md
└── service_layer_architecture_v2.0_20260204.md
```

### ❌ 错误 3：版本号判断错误

```bash
# ❌ 错误：小改动使用 MAJOR 版本
修正错别字 → v2.0 → v3.0  # 过度升级

# ✅ 正确：小改动使用 PATCH 版本
修正错别字 → v2.0 → v2.0.1

# ❌ 错误：重大改动使用 PATCH 版本
新增完整章节 → v2.0 → v2.0.1  # 版本号不足

# ✅ 正确：重大改动使用 MAJOR 版本
新增完整章节 → v2.0 → v3.0
```

---

## 最佳实践

1. **文档即代码**：设计文档与代码同等重要，必须版本化管理
2. **语义化版本**：严格遵循语义化版本规则，变更粒度体现在版本号
3. **及时归档**：每次 MAJOR/MINOR 更新时，及时归档旧版本
4. **版本同步**：主文档和 FAQ 文档的版本号保持一致
5. **单一真实来源**：设计文档是架构的唯一真实来源，禁止分散信息

---

## 关键资源

**设计文档**：
- `docs/design/system_architecture_v1.0.md`
- `docs/design/cmdb_design_v2.3.md`
- `docs/design/service_layer_architecture_v2.0.md`
- `docs/design/service_layer_faq_v2.1.md`

**SKILL 文档**：
- `.claude/skills/developer/SKILL.md` - 开发工作技能
- `.claude/skills/qa/SKILL.md` - QA 工作技能
- `.claude/skills/scrum_master/SKILL.md` - Scrum 工作流程

**Story 文档**：
- `docs/scrum/story/story-*.md` - Story 执行指南

---

## 文档审查清单

**设计文档更新前检查**：

- [ ] 确定版本号增量（MAJOR/MINOR/PATCH）
- [ ] 归档旧版本（如需要）
- [ ] 创建新版本文件
- [ ] 更新版本历史表
- [ ] 更新文档概述（如有必要）
- [ ] 更新相关文档（FAQ、其他层次文档）
- [ ] 验证文档结构完整（必需章节齐全）
- [ ] 验证内部链接有效
- [ ] 提交版本控制

---

**版本**: v1.0
**创建日期**: 2026-02-04
**作者**: Development Team
**状态**: 正式发布
