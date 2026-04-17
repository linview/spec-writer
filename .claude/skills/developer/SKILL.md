---
skill: "developer"
description: "开发工作技能 - 功能开发、代码风格、单元测试、SIT验证、代码规范、MR创建与CI调试"
version: "3.0"
---

# Developer 工作技能

## 核心职责

0. **代码风格**: 默认代码风格遵循KISS, DRY, SOLID原则；尽量符合”接口与实现分离，逻辑与配置分离“的标准
1. **功能开发**：实现新功能、修复Bug、优化性能； 
2. **单元测试**：编写和维护单元测试，确保测试覆盖率 ≥ 70%
3. **代码质量**：遵循代码规则，进行代码审查，
4. **集成测试验证**：使用官方SIT测试框架验证功能
5. **文档维护**：反馈设计文档、开发API文档、开发运维文档

---

## **代码风格**（重要）:  
   - 默认代码风格遵循 KISS（Keep It Simple, Stupid）、DRY（Don't Repeat Yourself）、SOLID 原则，追求简单、可维护、可扩展的实现。  
   - 强调“接口与实现分离，逻辑与配置分离”，保持各模块职责单一、接口清晰，实现与调用解耦。  
   - 命名规范清晰、统一（如函数名、变量名需表达实际含义，遵循 camelCase 或 snake_case，不使用拼音或无意义缩写）。  
   - 代码尽量模块化、函数职责单一，避免冗长或重复的代码。  
   - 注释放在核心业务、复杂逻辑处，保持必要但不过度，注重代码自解释性。  
   - 大块业务流程和外部依赖分层处理（如控制器、服务、存储分离）。  
   - 代码提交需格式规范、缩进统一，推荐统一采用 lint/formatter 工具。  

---

## Docker 开发规范（⚠️ 关键）

**黄金规则**：每次更新代码后，启动服务前必须重新编译 Docker 镜像

```bash
# ❌ 错误做法：只重启服务，不会应用新代码
docker compose restart api

# ✅ 正确做法：重新构建并启动服务
docker compose up -d --build api

# 或者分两步执行
make build
docker compose up -d --build api
```

**原因**：Docker 容器使用的是编译好的二进制文件，如果不重新构建镜像，新的代码更改不会生效。

**验证方法**：
```bash
# 检查容器内的二进制文件时间戳
docker exec resource-meter-api stat /app/resource-meter
# 应该显示最近的时间戳（几分钟内）
```

---

## SIT 测试规范（⚠️ 重要）

**黄金规则**：使用官方SIT测试框架，禁止自己编写测试脚本

```bash
# 开发完成后，使用官方SIT测试验证
./tests/sit/run_sit_tests.sh --auto     # 全自动模式（推荐）
./tests/sit/run_sit_tests.sh --quick    # 快速模式
./tests/sit/run_sit_tests.sh --interactive  # 交互式模式（调试）
```

**测试报告**：`test_reports/sit_report-*.md`
**官方框架**：`tests/sit/run_sit_tests.sh`, `tests/sit/sit_helpers.sh`

**快速验证**：
```bash
# 创建测试 Pod
./tests/sit/sit_helpers.sh create-devpod test-debug-001 4 dev-pod 600
sleep 8
./tests/sit/sit_helpers.sh query-status test-debug-001
./tests/sit/sit_helpers.sh delete test-debug-001 dev-pod
```

---

## UT 单元测试

```bash
# 运行所有单元测试
make test

# 运行特定包的测试
go test -v ./internal/pkgs/calculator/...

# 生成覆盖率报告
go test -v --cover ./internal/pkgs/... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total
```

**覆盖率要求**：
- 核心组件（calculator, informer）：≥ 80%
- 整体代码覆盖率：≥ 70%

---

## Mock Data 策略（⚠️ 重要）

### 核心原则：Spec → Scenario → Mock Data 三层对齐

基于设计规范（Spec）定义测试场景（Scenario），构建对齐的 Mock 数据，确保单元测试准确体现设计意图。

```
┌─────────────────────────────────────────────────────────────┐
│                    设计规范层 (Spec)                          │
│  - 来自 cmdb_design_v2.3.md                                  │
│  - 来自 service_layer_architecture_v2.0.md                   │
│  - 定义：状态机、业务规则、数据模型                            │
└────────────────────┬────────────────────────────────────────┘
                     │ 映射
┌────────────────────▼────────────────────────────────────────┐
│                    测试场景层 (Scenario)                      │
│  - 基于规范提取的典型用例                                     │
│  - 包含：正常路径、边界条件、异常处理                          │
└────────────────────┬────────────────────────────────────────┘
                     │ 对齐
┌────────────────────▼────────────────────────────────────────┐
│                    Mock 数据层 (Mock Data)                    │
│  - Go 结构体初始化                                            │
│  - Mock 对象期望设置                                          │
│  - 断言验证条件                                              │
└─────────────────────────────────────────────────────────────┘
```

### 关键要求

- ✅ **Spec → Scenario 对齐**: 每个 scenario 必须回溯到具体的 spec 条款
- ✅ **Scenario → Mock Data 对齐**: mock data 必须完全满足 scenario 的前置条件
- ✅ **可追溯性**: 测试代码中的注释必须标注来源 spec 的章节号

### Spec 场景文档

**参考文档**: `tests/ut/spec_scenarios.md` - 完整的 Spec → Scenario → Mock Data 映射规范

**场景覆盖**:
- Pod 来源识别（DevPod, ArgoWorkflow, RayJob）
- Pod 元数据提取（完整提取、默认值策略）
- 状态机转换（PENDING → RUNNING → STOPPED → RUNNING）
- GPU 用量计算（多次启停）
- 活跃 Pod GPU 实时计算（v2.0）

### 测试代码注释规范

```go
// Spec: <文档名> §<章节号>
// Scenario: <场景描述>
func TestXXX(t *testing.T) {
    // Arrange: 基于 spec 构建场景
    // ...

    // Act: 执行被测试的逻辑
    // ...

    // Assert: 验证 spec 要求
    // ...
}
```

### Mock 工具和最佳实践

**推荐工具**:
- **testify/mock**: Mock 接口对象（`github.com/stretchr/testify/mock`）
- **mockery**: 自动生成 mock 代码（`go install github.com/vektra/mockery/v2@latest`）
- **testcontainers**: 集成测试数据库（`github.com/testcontainers/testcontainers-go`）

**接口抽象原则**:
- 将具体类型（如 `*dao.PodResourceStatusDAO`）改为接口（`dao.PodResourceStatusDAOInterface`）
- 使用依赖注入将 mock 对象传入被测试的代码
- 避免在业务逻辑中硬依赖具体实现

**示例：接口抽象**
```go
// ❌ 错误：硬依赖具体类型
type EventProcessor struct {
    podStatusDAO *dao.PodResourceStatusDAO  // 无法 mock
}

// ✅ 正确：使用接口
type EventProcessor struct {
    podStatusDAO dao.PodResourceStatusDAOInterface  // 可 mock
}
```

**示例：Mock 对象设置**
```go
// Mock: 数据库操作期望
mockDAO.On("GetByK8sUID", mock.Anything, "pod-uid-001").
    Return(existingStatus, nil)

// Mock: 带条件验证的期望
mockDAO.On("Create", mock.Anything, mock.MatchedBy(func(status *model.PodResourceStatus) bool {
    // 验证 spec 要求：status = PENDING
    return status.Status == model.StatusPending
})).Return(nil)
```

### 生成 Mock 代码

```bash
# 安装 mockery
go install github.com/vektra/mockery/v2@latest

# 生成所有接口的 mocks
mockery --all --output=./internal/dao/mocks

# 生成特定接口的 mock
mockery --name=PodResourceStatusDAOInterface --output=./internal/dao/mocks
```

### 基于 Spec 编写 UT 的步骤

1. **确定 Spec 来源**
   - 在设计文档中找到相关章节（如 `service_layer_architecture_v2.0.md §4.2`）
   - 记录文档名、章节号、规范要求

2. **定义 Scenario**
   - 描述场景的前置条件、执行步骤、预期结果
   - 标注场景类型（Happy Path / 边界条件 / 异常处理）

3. **构建 Mock Data**
   - 使用 Go 结构体初始化创建测试数据
   - 确保 mock data 完全满足 scenario 的前置条件
   - 在注释中标注来源 spec 的章节号

4. **编写测试代码**
   - 使用 `testify/mock` 设置 mock 对象期望
   - 调用被测试的逻辑
   - 使用 `testify/assert` 验证 spec 要求

### 覆盖率提升策略

| 当前状态 | 目标状态 | 策略 |
|---------|---------|------|
| Calculator: 43.2% | ≥ 80% | 基于 spec §4 状态机转换编写场景测试 |
| Informer: 49.6% | ≥ 80% | 基于 spec §2.2 Pod 识别编写场景测试 |
| Extractor: 93.1% | ≥ 80% | ✅ 已达标 |
| 整体: 24.9% | ≥ 70% | DAO 层添加接口 + Mock 测试 |

**优先级**:
1. **P0**: 定义 DAO 接口层，解耦具体实现
2. **P1**: 使用 mockery 生成 mocks
3. **P1**: 基于 `tests/ut/spec_scenarios.md` 实现 Calculator/Informer UT
4. **P2**: 补充 DAO 层的基础测试

---

## 代码质量

**格式化**：`make fmt` 或 `go fmt ./...`

**静态分析**：`make lint` 或 `golangci-lint run`

**编译检查**：`go build ./...` 或 `make build`

---

## 代码提交规范

**提交前检查清单**：
- [ ] 代码已格式化 (`make fmt`)
- [ ] 通过静态分析 (`make lint`)
- [ ] 单元测试通过 (`make test`)
- [ ] 测试覆盖率达标 (≥ 70%)
- [ ] 使用官方SIT测试验证 (`./tests/sit/run_sit_tests.sh --quick`)
- [ ] 代码已审查（如果有PR）
- [ ] 文档已更新（如果需要）

**Commit Message 规范**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**：`feat`, `fix`, `refactor`, `docs`, `test`, `chore`

**示例**：
```
fix(informer): 修复 Pod DELETE 事件处理逻辑

- DELETE 事件检测只依赖 DeletionTimestamp
- 移除对 K8sPodPhase 的依赖
- 添加 nil pointer 保护

Fixes #123
```

---

## Git 推送规则（⚠️ 重要）

**默认行为**：
- ✅ **只做**：`git add` + `git commit`（提交到本地分支）
- ❌ **不做**：`git push`（不推送远程）

**Master 分支保护规则**：
- **方式 1**：Review 授权流程（修改代码 → commit → 等待 review → 用户手动 push）
- **方式 2**：GitLab MR 流程（创建 feature 分支 → push → 创建 MR → 合并）

**绝对禁止**：未经明确授权直接 `git push origin master`

**YOLO 模式例外条件**（必须同时满足）：
1. 用户**明确授权**（明确说"YOLO模式"或"可以推送"）
2. 只能推送 **master 之外的分支**（feature/*, dev, bugfix/* 等）
3. 推送前必须显示 commit 信息供审查
4. **永远不要自动推送 master 分支**（即使 YOLO 模式也不行）

---

## Git Worktree 工作流

**核心概念**：主干开发模式，支持并行开发多个任务

**分支命名规范**：
- 功能分支：`feat/<story_id>-<summary>`
- Bug 修复：`fix/<bug-id>-<description>`
- 紧急修复：`hotfix/<short-description>`
- 重构：`refactor/<short-description>`

**标准流程**：
```bash
# 1. 创建 worktree（从主仓库）
cd /home/mini/Proj/resource-meter
git worktree add ../resource-meter-worktrees/story-06-01-pod-handler \
  -b feat/story-06-01-pod-handler

# 2. 在 worktree 中开发
cd ../resource-meter-worktrees/story-06-01-pod-handler
# ... 开发代码 ...
git add .
git commit -m "feat: implement pod handler"

# 3. 推送到远程（非 master 分支）
git push origin feat/story-06-01-pod-handler

# 4. 创建 GitLab MR
glab mr create --title "feat: implement pod handler" \
  --target-branch master --source-branch feat/story-06-01-pod-handler

# 5. MR 合并后，清理 worktree
cd ../../resource-meter
git worktree remove ../resource-meter-worktrees/story-06-01-pod-handler
git branch -d feat/story-06-01-pod-handler
```

**Worktree 管理**：
```bash
# 列出所有 worktree
git worktree list

# 清理孤立的 worktree
git worktree prune
```

**推荐**：同时维护 2-3 个工作树，不超过 5 个

---

## 开发工作流

### Bug 修复流程

1. **问题定位**：阅读 SIT 测试报告，查看代码，确定根因
2. **修复实现**：编写修复代码，添加单元测试
3. **单元测试**：运行 `make test`
4. **SIT 验证**：`./tests/sit/run_sit_tests.sh --quick`
5. **提交代码**：撰写清晰的 Commit Message
6. **生成报告**：如果修改影响核心功能，运行完整 SIT 测试

### 新功能开发流程

1. **需求分析**：阅读 PRD 和 Story 文档
2. **设计实现**：参考设计文档，设计数据结构、接口、流程
3. **编码实现**：遵循代码规范，编写单元测试
4. **单元测试**：运行 `make test`，确保覆盖率达标
5. **SIT 验证**：`./tests/sit/run_sit_tests.sh --auto`
6. **文档更新**：更新设计文档、API 文档、CLAUDE.md
7. **代码审查**：提交 PR，根据反馈修改
8. **合并发布**：合并到主分支，生成 SIT 测试报告

---

## MR 创建、监控与调试（完整工作流）

### 核心工作模式

```
MR 创建 → Pipeline 监听 → 状态判断 → 成功/失败处理
                ↓                      ↓
           持续监听               Yolo Mode 修复
                                   ↓
                              重新推送 → 继续监听
                                       ↓
                                   闭环验证
```

### 阶段一：MR 创建（6 步流程）

#### 前置检查（7 项必须）

- [ ] 功能完整性：所有 AC 已满足
- [ ] 代码质量：单元测试覆盖率 ≥ 80%
- [ ] 测试验证：UT/API/SIT/UAT 全部通过
- [ ] 代码规范：符合项目编码规范
- [ ] 文档更新：设计文档、API 文档已更新
- [ ] Git 规范：Commit Message 包含 Story ID
- [ ] 分支状态：feature 分支提交已整理

#### Step 1: 盘点变更

```bash
cd /home/mini/Proj/llv/resource-meter-worktrees/<worktree-name>
git status
git log origin/master..HEAD --oneline
git log origin/master..HEAD --stat  # 关键：提交数、文件数、行数变更
```

#### Step 2: 生成 MR Description（40-100 行）

```bash
cat > /tmp/mr_desc.md << 'EOF'
## 📋 功能说明
[简述功能目标 + 核心改进点 3-5 条]

## 📝 变更说明
### 新增文件 (N 个)
- `path/file.go` (X lines) - 简短说明

### 修改文件 (M 个)
- `path/file2.go` - 修改说明

### 代码统计
- 新增: +X lines
- 删除: -Y lines
- 测试覆盖率: XX%

## ✅ 测试验证结果
### 单元测试
✅ N/N tests passed, XX% coverage

### 真实环境验证
| 场景 | 预期 | 实际 | 状态 |
|------|------|------|------|
| 场景1 | XXX | XXX | ✅ |

## 📚 相关文档
- Story: `docs/scrum/story/story-XX-YY.md`
- Design: `docs/design/xxx.md`

## 🎯 验收标准
- [x] AC1
- [x] AC2

**Story**: STORY-XX-YY | **Sprint**: Sprint X | **Status**: IN_REVIEW
EOF
```

#### Step 3: 验证 GitLab Token

```bash
GITLAB_TOKEN="your-token"
curl -s --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "https://gitlab.example.com/api/v4/user" | jq -r '.username'
```

#### Step 4: 创建 JSON Payload

```bash
jq -n \
  --arg title "feat(story-XX-YY): 简短标题" \
  --arg desc "$(cat /tmp/mr_desc.md)" \
  --arg source "feat/story-XX-YY-summary" \
  --arg target "master" \
  '{source_branch: $source, target_branch: $target, title: $title, description: $desc, labels: "story::XX-YY,type::feat"}' \
  > /tmp/mr_payload.json
```

#### Step 5: 调用 API 创建 MR

**⚠️ 关键**：变量设置和使用必须在同一行

```bash
GITLAB_TOKEN="your-token" && \
curl -s -X POST "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/merge_requests" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --header "Content-Type: application/json" \
  --data @/tmp/mr_payload.json | jq '{iid, web_url, state}'
```

#### Step 6: 验证 MR 成功

```bash
MR_IID=17  # 从上一步输出获取
curl -s "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/merge_requests/${MR_IID}" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" | jq '.web_url'
```

**成功标志**: 返回 MR URL，状态为 "opened"

### 阶段二：Pipeline 监控与调试

#### 监控工作流

```
创建 MR / 推送代码
    ↓
开始监听 Pipeline
    ↓
┌───┴───┐
│       │
SUCCESS FAILED
│       │
↓       ↓
停止  Yolo Mode
通知   修复 → 推送 → 继续监听 ⟲
```

#### 核心命令集

**1. 查询 MR Pipeline 状态**

```bash
MR_IID=17
GITLAB_TOKEN="your-token"

curl -s "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/merge_requests/${MR_IID}" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" | jq '{
    pipeline_id: .pipeline.id,
    status: .pipeline.status,
    web_url: .pipeline.web_url
  }'
```

**状态值**: pending, running, success, failed, canceled, skipped

**2. 获取失败 Jobs**

```bash
PIPELINE_ID=334081

curl -s "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/pipelines/${PIPELINE_ID}/jobs" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" | jq '.[] | select(.status == "failed") | {
    name, stage, failure_reason, id, web_url
  }'
```

**3. 获取失败日志（核心分析能力）**

```bash
JOB_ID=1165485

# 方式1: 直接输出到终端（适合小日志）
curl -s "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/jobs/${JOB_ID}/trace" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}"

# 方式2: 保存到文件（适合大日志）
curl -s "https://gitlab.example.com/api/v4/projects/team-a%2Fsample-project/jobs/${JOB_ID}/trace" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" > /tmp/ci_failure_${JOB_ID}.log

# 分析关键错误
grep -E "(error|Error|ERROR|fail|Fail|FAIL)" /tmp/ci_failure_${JOB_ID}.log | head -20
```

**日志过大时**: 会保存到 `/home/mini/.claude/projects/*/tool-results/call_*.txt`

#### CI 失败类型与处理

| 失败类型 | failure_reason | 负责团队 | 典型场景 |
|---------|----------------|---------|----------|
| 编译错误 | script_failure | Dev | 语法错误、类型不匹配、依赖缺失 |
| 测试失败 | script_failure | Dev/QA | 断言失败、集成测试失败 |
| 超时 | job_execution_timeout | Dev | 死锁、网络延迟、性能问题 |
| Runner 异常 | runner_system_failure | Ops | Runner 不可用、资源不足 |

### 阶段三：Yolo Mode 快速修复

**触发条件**: Pipeline 失败

**5 步修复流程**：

#### Step 3.1: 同步 Master（必须）

```bash
cd /home/mini/Proj/llv/resource-meter-worktrees/<worktree-name>
git fetch origin master
git rebase origin/master
```

#### Step 3.2: 本地修复

根据 CI 日志定位问题并修复：

```bash
# 示例：修复测试编译错误
vim internal/pkgs/k8s/informer/pod_event_handler_test.go
```

#### Step 3.3: 本地验证（必须全部通过）

```bash
make test      # 单元测试
make fmt       # 代码格式化
make build     # 构建验证
```

#### Step 3.4: 提交并推送

```bash
git add -A
git commit -m "fix(story-XX-YY): fix CI failures

- Fix issue 1
- Fix issue 2

CI Pipeline: #OLD → #NEW

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"

git push origin feat/story-XX-YY-summary
```

#### Step 3.5: 继续监听

回到阶段二，重新查询 Pipeline 状态，直到 success

### 关键技术点

**1. Shell 变量作用域陷阱**

```bash
# ❌ 错误：变量在下一行命令中丢失
GITLAB_TOKEN="xxx"
curl -s "https://..." --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}"

# ✅ 正确：同一行设置和使用
GITLAB_TOKEN="xxx" && curl -s "https://..." --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}"
```

**2. MR Description 长度控制**

- 推荐范围: 40-100 行
- 超过 200 行: GitLab API 可能拒绝
- 精简策略: 删除冗余的 commit 列表、合并相似内容

**3. Pipeline 状态轮询**

```bash
# 简单轮询脚本（每分钟检查一次）
while true; do
  STATUS=$(curl -s "..." | jq -r '.pipeline.status')
  echo "[$(date)] Pipeline: $STATUS"

  if [ "$STATUS" == "success" ]; then
    echo "✅ 成功！"
    break
  elif [ "$STATUS" == "failed" ]; then
    echo "❌ 失败，进入 Yolo Mode"
    break
  fi

  sleep 60
done
```

**4. 日志分析技巧**

```bash
# 提取关键错误信息
grep -E "^(Error|FAIL|fatal)" /tmp/ci_failure.log | uniq

# 查看错误上下文（前后 5 行）
grep -B5 -A5 "error:" /tmp/ci_failure.log

# 统计错误类型
grep -o "error: [^[:space:]]*" /tmp/ci_failure.log | sort | uniq -c
```

### 常见问题排查

| 症状 | 原因 | 解决方案 |
|------|------|----------|
| 401 Unauthorized | Token 无效/过期 | 重新生成 PAT，确保有 api 权限 |
| MR 已存在 | 之前创建过 | 查询现有 MR，更新描述而非新建 |
| Description 太长 | 超过限制 | 精简到 40-100 行 |
| 环境变量丢失 | Shell 变量跨命令 | 同一行设置和使用 |
| Pipeline 一直 pending | Runner 资源不足 | 联系 Ops 或稍后重试 |
| 日志过大无法查看 | 超过终端输出限制 | 保存到文件，使用 grep 分析 |

---

## 常见错误

### ❌ 错误1：自己编写SIT测试脚本

```bash
# ❌ 错误：自写测试脚本
cat > /tmp/my_sit_test.sh << 'EOF'
...自己编写的测试逻辑...
EOF

# ✅ 正确：使用官方SIT测试
./tests/sit/run_sit_tests.sh --auto
```

### ❌ 错误2：提交前不运行测试

```bash
# ❌ 错误：直接提交
git add . && git commit -m "fix: something" && git push

# ✅ 正确：提交前检查
make fmt && make lint && make test
./tests/sit/run_sit_tests.sh --quick
git add . && git commit -m "fix: something"
```

### ❌ 错误3：测试覆盖率不达标

```bash
# ❌ 错误：忽略覆盖率
go test ./internal/pkgs/calculator/...
# PASS (no coverage files)

# ✅ 正确：检查覆盖率
go test -v --cover ./internal/pkgs/calculator/...
# coverage: 75.2% of statements
```

---

## 最佳实践

1. **测试驱动开发（TDD）**：先写测试，再写代码
2. **持续集成（CI）**：每次提交前运行测试，使用官方SIT测试验证
3. **代码审查**：重要修改需要 Code Review，遵循项目代码规范
4. **文档更新**：代码变更后及时更新文档，保持文档与代码同步
5. **问题排查**：遇到问题时先查看日志，使用官方测试脚本验证

---

## 关键资源

**必读文档**：
- `CLAUDE.md` - 项目概述、核心架构、开发规范
- `tests/sit/README.md` - SIT 测试使用指南
- `docs/design/cmdb_design_v2.3.md` - Pod 资源管理 + CMDB 设计

**SKILL 文档**：
- `.claude/skills/naming-conventions.skill.md` - 代码命名规范
- `.claude/skills/qa/SKILL.md` - QA 工作流程和测试规范
- `.claude/skills/scrum_master/SKILL.md` - Scrum 工作流程

**Scrum 文档**：
- `docs/scrum/prd/README.md` - 8 个 Epic 的规划
- `docs/scrum/story/story-*.md` - 每个 Story 的执行指南
- `docs/scrum/DASHBOARD.md` - 项目进度仪表盘

---

**版本**: v3.0
**更新日期**: 2026-02-12
**维护者**: Development Team

**更新日志**：
- v3.0 (2026-02-12): ⚠️ 重要：从 scrum_master SKILL 迁移 MR 创建、监控与调试工作流
- v2.0 (2026-02-03): 初始版本，定义开发核心职责和代码规范
