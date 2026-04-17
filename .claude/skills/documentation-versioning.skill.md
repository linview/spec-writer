---
skill: "documentation-versioning"
description: "文档版本管理 - 版本号规范、归档规则、更新流程"
version: "2.0"
---

# 文档版本管理技能

## 核心原则

### 版本号规范

文档版本号采用 **vX.Y** 格式：
- **X** (主版本号): 重大架构变更、不兼容的修改
- **Y** (次版本号): 功能增强、bug 修复、基于新数据的修正

**示例**：
- v1.0 → v2.0: 重大架构重构
- v2.0 → v2.1: 功能增强或 bug 修复
- v2.1 → v2.2: 基于实际数据的修正

### 保留策略（✅ 强制要求）

**当前版本和往期版本保留在 `docs/design/` 目录**

```
docs/design/
├── cmdb_design_v2.0.md  ← 往期版本（保留）
├── cmdb_design_v2.1.md  ← 往期版本（保留）
└── cmdb_design_v2.2.md  ← 当前版本（活跃）
```

**归档版本存放于 `docs/archive/` 目录**

```
docs/archive/
├── cmdb_design_v2.1_20260131.md  ← 归档版本（带日期戳）
└── cmdb_design_v2.0_20260130.md  ← 归档版本（带日期戳）
```

### 归档规则

**何时归档**：
- ✅ 文档版本更新时（v2.1 → v2.2），旧版本归档到 `docs/archive/`
- ✅ 归档文件名格式：`原文件名_vX.Y_YYYYMMDD.md`
- ✅ **不要删除** `docs/design/` 下的往期版本文件

**示例操作**：
```bash
# 1. 更新文档版本（v2.1 → v2.2）
cp docs/design/cmdb_design_v2.1.md docs/design/cmdb_design_v2.2.md

# 2. 归档旧版本（带日期戳）
mv docs/design/cmdb_design_v2.1.md docs/archive/cmdb_design_v2.1_20260131.md
```

---

## 文档头部模板

所有设计文档必须包含版本信息头部：

```markdown
# 文档标题

**版本**: vX.Y (简短说明)
**创建日期**: YYYY-MM-DD
**状态**: ✅ 设计完成 | 🚧 实施中 | ⚠️ 已废弃
**替代版本**: vX.Y-1 (已归档至 `archive/文件名_vX.Y-1_YYYYMMDD.md`)

**版本说明**:
- vX.Y 新增功能/修正内容 1
- vX.Y 新增功能/修正内容 2

**关键修正**（如果有）:
1. ❌ vX.Y-1 错误假设
   ✅ vX.Y 修正内容
```

---

## 版本更新流程

### 步骤 1: 更新当前版本

```bash
# 复制当前版本作为新版本的基础
cp docs/design/文件名_vX.Y.md docs/design/文件名_vX.Y+1.md
```

### 步骤 2: 修改新版本内容

- 更新版本号：`vX.Y` → `vX.Y+1`
- 更新创建日期
- 更新版本说明和关键修正
- 修改具体章节内容

### 步骤 3: 归档旧版本

```bash
# 归档旧版本（带日期戳）
mv docs/design/文件名_vX.Y.md docs/archive/文件名_vX.Y_$(date +%Y%m%d).md
```

### 步骤 4: 更新引用

更新其他文档中对旧版本的引用：
```markdown
# 旧引用
- [cmdb_design_v2.1.md](./cmdb_design_v2.1.md)

# 新引用
- [cmdb_design_v2.2.md](./cmdb_design_v2.2.md)
```

### 步骤 5: 验证

```bash
# 检查文件是否存在
ls -lh docs/design/cmdb_design_v2.2.md
ls -lh docs/archive/cmdb_design_v2.1_20260131.md

# 检查版本号
grep "版本.*v2.2" docs/design/cmdb_design_v2.2.md
```

---

## 目录结构规范

### docs/design/ 目录

存放**当前版本和往期版本**的设计文档：
- 所有版本（v1.0, v2.0, v2.1...）都保留在此目录
- 便于查阅和对比不同版本
- 文档内部链接使用相对路径（如 `./文件名.md`）

### docs/archive/ 目录

存放**归档版本**的历史文档：
- 归档文件名格式：`文件名_vX.Y_YYYYMMDD.md`
- 带日期戳，便于追溯
- 保留完整的修改历史

### docs/analysis/ 目录

存放**分析文档**和**调研报告**：
- Informer 实际数据分析
- 数据库 schema 分析
- 技术方案调研
- 不受版本管理约束

---

## 常见错误

### 错误 1: 删除 `docs/design/` 下的旧版本

❌ **错误操作**：
```bash
rm docs/design/cmdb_design_v2.1.md
```

✅ **正确操作**：
```bash
# 保留旧版本在 docs/design/
# 同时归档一份到 docs/archive/
mv docs/design/cmdb_design_v2.1.md docs/archive/cmdb_design_v2.1_20260131.md
```

### 错误 2: 归档文件名不带日期戳

❌ **错误**: `cmdb_design_v2.1.md`
✅ **正确**: `cmdb_design_v2.1_20260131.md`

### 错误 3: 版本号不一致

文档头部版本号与文件名不一致：
- 文件名: `cmdb_design_v2.2.md`
- 头部: `**版本**: v2.2` ✅

---

## 检查清单

更新文档版本时，请按此清单检查：

- [ ] 已复制旧版本作为新版本基础
- [ ] 已更新文件名版本号（vX.Y → vX.Y+1）
- [ ] 已更新文档头部版本信息
- [ ] 已更新版本说明和关键修正
- [ ] 已归档旧版本到 `docs/archive/`（带日期戳）
- [ ] **docs/design/ 目录保留旧版本**
- [ ] 已更新其他文档中的引用链接
- [ ] 已验证文件存在性和版本号一致性

---

**版本**: v2.0
**更新日期**: 2026-02-03
**维护者**: Resource Meter Team
