---
skill: "naming-conventions"
description: "命名规范 - 蛇形命名方式 (snake_case)、文件命名规则"
version: "2.0"
---

# 命名规范技能

## 强制标准：蛇形命名方式 (snake_case)

**项目强制要求**：所有代码文件、配置文件、脚本文件和目录必须使用蛇形命名方式（snake_case），即使用下划线 `_` 连接单词，禁止使用连字符 `-`。

---

## 命名规则

### 1. Go 源代码文件
- ✅ **正确**: `resource_meter.go`, `config_dev.go`, `health_handler.go`
- ❌ **错误**: `resource-meter.go`, `config-dev.go`, `health-handler.go`

### 2. 配置文件 (YAML/TOML/JSON)
- ✅ **正确**: `config_dev.yaml`, `config_prod.yaml`, `database_config.yaml`
- ❌ **错误**: `config-dev.yaml`, `config-prod.yaml`, `database-config.yaml`

### 3. Shell 脚本文件
- ✅ **正确**: `start_dev.sh`, `stop_dev.sh`, `init_db.sh`
- ❌ **错误**: `start-dev.sh`, `stop-dev.sh`, `init-db.sh`

### 4. 目录命名
- ✅ **正确**: `dev_pod_informer`, `scripts_database`, `internal_handler`
- ❌ **错误**: `dev-pod-informer`, `scripts-database`, `internal-handler`

### 5. API 定义文件
- ✅ **正确**: `resource_meter.api`, `user_service.api`
- ❌ **错误**: `resource-meter.api`, `user-service.api`

### 6. 二进制文件
- ✅ **正确**: `resource_meter_api`, `resource_meter_cli`
- ❌ **错误**: `resource-meter-api`, `resource-meter-cli`

---

## 例外情况（允许使用连字符或标准命名）

### 1. Go Modules (Go 社区标准)
- ✅ **允许**: `resource-meter` (go.mod 中的 module 名称)
- **原因**: Go 社区惯例，所有 Go 官方和第三方模块都使用连字符

### 2. Go 包名 (Go 语言规范)
- ✅ **允许**: 使用单个单词，如 `main`, `config`, `handler`
- **原因**: Go 语言规范要求包名使用简短的单个小写单词

### 3. 通用配置文件（工具标准命名）
- ✅ **允许**:
  - `Makefile` (Make 工具标准)
  - `Dockerfile` (Docker 工具标准)
  - `.gitlab-ci.yml` (GitLab CI 标准命名)
  - `docker-compose.yml` (Docker Compose 标准命名)
  - `go.mod`, `go.sum` (Go 工具标准)
- **原因**: 这些是开发工具的标准命名，修改会导致工具无法识别

### 4. 文档文件（建议使用连字符增强可读性）
- ✅ **允许**: `epic-1-scaffolding.md`, `story-1-01-design.md`
- **原因**: 文档文件使用连字符更便于阅读，不影响代码编译和运行

### 5. 技能文件（可选项）
- ✅ **允许**: `event-db-cmdb-design.skill.md`
- **原因**: 技能文件使用连字符便于区分不同的技能概念

---

## 代码检查清单

在创建或重命名文件时，请按照以下清单检查：

- [ ] 文件名使用小写字母
- [ ] 多个单词使用下划线 `_` 连接
- [ ] 不使用连字符 `-`（除非属于例外情况）
- [ ] 不使用驼峰命名 `CamelCase` 或 `PascalCase`
- [ ] 不使用空格或特殊字符

---

## 重命名操作指南

当发现不符合规范的文件时，按以下步骤重命名：

### 1. 使用 git mv 重命名（保留历史）

```bash
# 示例：重命名配置文件
git mv etc/config-dev.yaml etc/config_dev.yaml

# 示例：重命名 Go 源文件
git mv resource-meter.go resource_meter.go

# 示例：重命名目录
git mv sandbox/dev-pod-informer sandbox/dev_pod_informer
```

### 2. 更新所有引用

重命名文件后，必须更新所有引用该文件的地方：
- **Makefile**: 更新文件路径引用
- **配置文件**: 更新 include 引用
- **Go 代码**: 更新 import 路径
- **Shell 脚本**: 更新文件路径
- **文档**: 更新文件路径说明

### 3. 验证编译和测试

```bash
# 重新编译
make build

# 运行测试
make test
```

---

## 命名规范的理论依据

### 为什么选择蛇形命名 (snake_case)？

1. **一致性**: 项目统一使用蛇形命名，避免混用不同风格
2. **跨语言兼容**: 蛇形命名在多种编程语言中都是标准命名方式
3. **可读性**: 下划线分隔的单词清晰易读，特别是在文件系统中
4. **避免歧义**: 连字符在某些命令行工具中可能被误解析为选项参数
5. **数据库友好**: 蛇形命名与数据库表名、字段命名规范一致

### 为什么 Go Modules 使用连字符？

Go 官方推荐在 module 路径中使用连字符（如 `resource-meter`），这是 Go 社区的特殊惯例，不影响其他文件使用蛇形命名。

---

## 强制执行

此规范是 Resource Meter 项目的**强制标准**，所有开发人员必须遵守：

- 代码审查 (Code Review) 时必须检查命名规范
- 不符合规范的文件不得合并到主分支
- CI/CD 流水线应包含命名规范检查（可选）

---

**版本**: v2.0
**更新日期**: 2026-02-03
**维护者**: Resource Meter Team
