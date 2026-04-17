---
skill: "directory-structure"
description: "目录结构标准 - main.go 命名、build/ 和 log/ 目录管理"
version: "2.0"
---

# 目录结构标准技能

## 强制标准

### 1. 主入口文件命名规范

**项目强制要求**：
- 默认一个项目对外输出一个服务
- 主入口文件**必须**命名为 `main.go`
- 主入口文件放在项目根目录

**理由**：
1. ✅ 符合 Go 语言标准惯例
2. ✅ 社区标准，所有 Go 项目都用 `main.go`
3. ✅ 便于识别：开发者看到 `main.go` 就知道是入口文件
4. ✅ 工具兼容：`go build` 默认处理 `main.go`

**正确示例**：✅ `main.go`
**错误示例**：❌ `resource_meter.go`, `app.go`, `server.go`

### 2. 构建产物和日志目录分离

**项目强制要求**：
1. 所有构建产物必须输出到 `build/` 目录
2. 所有日志文件必须输出到 `log/` 目录
3. `build/` 和 `log/` 目录必须添加到 `.gitignore`

---

## 标准目录结构

```
resource-meter/
├── build/              # 构建产物输出目录（不提交到 Git）
├── log/                # 日志文件输出目录（不提交到 Git）
├── cmd/                # 主程序入口
├── deploy/             # 部署相关
├── desc/               # API 定义文件
├── docs/               # 项目文档
├── etc/                # 配置文件
├── internal/           # 内部包
├── scripts/            # 脚本文件
└── main.go             # 主入口文件（强制命名）
```

---

## 构建产物管理

### Makefile 构建配置

**必须定义以下变量**：
```makefile
BUILD_DIR := build
LOG_DIR := log
```

**构建目标必须创建 build 目录**：
```makefile
build-linux:
	@echo "Building Linux binary..."
	@mkdir -p $(BUILD_DIR)
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME) .
```

**清理目标必须清理 build 目录**：
```makefile
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
```

### 构建产物输出路径

| 构建目标 | 输出路径 | 二进制文件名 |
|---------|---------|-------------|
| make build (Linux) | `build/` | `resource_meter_api` |
| make build-win | `build/` | `resource_meter_api.exe` |
| make build-mac | `build/` | `resource_meter_api_mac` |

### Dockerfile 引用

**Dockerfile 必须从 build/ 目录复制二进制**：
```dockerfile
FROM alpine:latest
WORKDIR /app
COPY build/resource_meter_api /app/resource_meter_api
```

---

## 日志管理

### 日志配置

**开发环境** (`etc/config_dev.yaml`)：
```yaml
Log:
  ServiceName: ResourceMeter
  Mode: file
  Path: log
  Level: info
  Compress: false
  KeepDays: 7
```

**生产环境** (`etc/config_prod.yaml`)：
```yaml
Log:
  ServiceName: ResourceMeter
  Mode: file
  Path: log
  Level: info
  Compress: true
  KeepDays: 30
```

### 日志文件命名

| 文件名 | 用途 | 格式 |
|--------|------|------|
| access.log | HTTP 访问日志 | 每日滚动 |
| error.log | 错误日志 | 每日滚动 |
| stat.log | 统计日志 | 每日滚动 |

---

## Git 忽略规则

### .gitignore 必须包含

```gitignore
# Build directory
build/
dist/

# Log directory
log/
*.log

# Binaries
*.exe
*.test
*.out

# IDE files
.idea/
.vscode/

# OS files
.DS_Store
```

---

## 代码检查清单

- [ ] 构建产物输出到 `build/` 目录
- [ ] 日志文件输出到 `log/` 目录
- [ ] Makefile 中定义 `BUILD_DIR` 和 `LOG_DIR` 变量
- [ ] 构建目标使用 `@mkdir -p $(BUILD_DIR)` 创建目录
- [ ] 清理目标使用 `rm -rf $(BUILD_DIR)` 清理构建产物
- [ ] 配置文件中设置 `Log.Path: log`
- [ ] `.gitignore` 包含 `build/` 和 `log/`
- [ ] Dockerfile 从 `build/` 目录复制二进制文件

---

## 运维指南

### 清理构建产物

```bash
# 使用 Makefile 清理
make clean

# 手动清理
rm -rf build/
```

### 清理日志文件

```bash
# 清理 7 天前的日志
find log/ -name "*.log" -mtime +7 -delete

# 清理所有日志
rm -rf log/
```

### 查看日志

```bash
# 实时查看访问日志
tail -f log/access.log

# 查看错误日志
tail -f log/error.log
```

---

## 常见问题

### Q1: 为什么要将构建产物放到 build/ 目录？

**A**：
1. 避免污染项目根目录
2. 便于批量清理构建产物
3. 防止错误提交到 Git
4. 符合 Go 项目标准结构

### Q2: 日志文件为什么要放到 log/ 目录？

**A**：
1. 集中管理所有日志文件
2. 便于日志轮转和清理
3. 防止日志文件污染项目结构
4. 符合 Linux 文件系统层次标准 (FHS)

---

**版本**: v2.0
**更新日期**: 2026-02-03
**维护者**: Resource Meter Team
