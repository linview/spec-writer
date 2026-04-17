---
skill: "qa"
description: "QA 工作技能 - UT回归测试、SIT系统集成测试、UAT用户验收测试"
version: "3.0"
---

# QA 工作技能

## 核心职责

1. **UT 回归测试**：收集单元测试结果，不负责实现
2. **SIT 系统集成测试**：实现测试框架、用例开发、执行测试、问题排查
3. **UAT 用户验收测试**：实现测试框架、用例开发、端到端测试
4. **API 接口测试**：根据 .api 元数据文件和设计文档设计测试用例
5. **测试报告**：生成测试报告，反馈给架构师和开发专家

---

## ⚠️ Worktree 开发与测试强制规则（铁律）

### 🔴 致命错误案例（2026-02-11 血的教训）

**问题**：QA 在主仓库 master 分支测试，但 MR 是从 worktree 创建的，导致代码不一致。

**错误操作**：
```bash
# ❌ 致命错误：在主仓库测试 worktree 的代码
cd /home/mini/Proj/llv/resource-meter  # 主仓库 master 分支
make test  # 测试通过 ✅ (但测试的是旧代码！)

# 但是 MR 是从这里创建的：
/home/mini/Proj/llv/resource-meter-worktrees/node-informer  # 新代码
# 结果：CI Pipeline 失败 ❌
```

**根本原因**：
- 主仓库代码：`NewPodEventHandler(queue, tz, logger)` （旧签名）
- Worktree 代码：`NewPodEventHandler(queue, tz, nodeLister, logger)` （新签名）
- QA 测试的是主仓库（旧代码），MR 推送的是 worktree（新代码）
- **环境不一致 = 虚假测试通过 = CI 失败**

**后果**：
- CI Pipeline #334081 失败
- 浪费时间排查和修复
- 信任度受损

---

### 📋 强制规则（必须遵守）

#### 规则 1：开发和测试必须在同一环境

```bash
# ✅ 正确做法：在 worktree 中开发和测试
cd /home/mini/Proj/llv/resource-meter-worktrees/node-informer

# 1. 确认在正确的 worktree
pwd
# 应该显示：/home/mini/Proj/llv/resource-meter-worktrees/<worktree-name>

# 2. 确认在正确的分支
git branch --show-current
# 应该显示：feat/story-XX-YY-summary

# 3. 在 worktree 中运行测试
make test
make fmt
make build

# 4. 然后才推送代码或创建 MR
git push origin feat/story-XX-YY-summary
```

#### 规则 2：严禁跨环境测试

| 环境 | 用途 | 测试命令 |
|------|------|---------|
| **主仓库** (`/home/mini/Proj/llv/resource-meter`) | **仅用于 master 分支** | `make test` (仅测试 master 代码) |
| **Worktree** (`/home/mini/Proj/llv/resource-meter-worktrees/*`) | **功能开发** | `make test` (测试 feature 代码) |

**❌ 禁止操作**：
- 在主仓库测试 worktree 的代码
- 在 worktree 测试主仓库的代码
- 假设两边的代码是一样的

**✅ 正确操作**：
- 开发在 worktree，测试也在 worktree
- 开发在主仓库，测试也在主仓库
- **始终测试实际要推送的代码**

#### 规则 3：创建 MR 前的强制检查清单

QA 在验证 MR 前**必须**确认：

```bash
# 1. 进入 worktree（如果是 feature 分支）
cd /home/mini/Proj/llv/resource-meter-worktrees/<worktree-name>

# 2. 确认分支正确
git branch --show-current
# 应该是 feat/story-XX-YY-*

# 3. 确认代码是最新的
git status
git log origin/master..HEAD --oneline

# 4. 在 worktree 中运行完整测试
make test
make fmt
make build

# 5. 所有测试通过后，才能报告"QA 验证通过"
```

#### 规则 4：CI 失败后的 Yolo Mode 工作流程

当 CI Pipeline 失败时：

```bash
# Step 1: 切换到 worktree
cd /home/mini/Proj/llv/resource-meter-worktrees/<worktree-name>

# Step 2: 同步 master 分支
git fetch origin master
git rebase origin/master

# Step 3: 本地修复问题

# Step 4: 在 worktree 中验证
make test
make fmt
make build

# Step 5: 自动推送
git push origin feat/story-XX-YY-summary

# Step 6: 继续监听新的 Pipeline
```

---

### 🎯 记住这个铁律

> **"开发和测试必须在同一环境，严禁在主仓库测试 worktree 的代码"**

**简单记忆法**：
```
Where you code = Where you test
(哪里开发 = 哪里测试)
```

**检验标准**：
```bash
# 在运行测试前，先问自己：
# 1. 我当前在哪个目录？(pwd)
# 2. 这个目录的代码是我要推送的吗？(git status)
# 3. 如果答案是否，那就 cd 到正确的目录！
```

---

## 🔧 Docker 测试环境规范（⚠️ 关键）

**黄金规则**：执行测试前，必须确保 Docker 容器运行的是最新代码

```bash
# ✅ 测试前准备：重新构建并启动所有服务
cd deploy/docker
docker compose up -d --build

# ✅ 验证服务已使用最新代码
docker logs resource-meter-api --tail 20
# 查看启动时间戳，应该是最近几分钟内

# ✅ 确认所有服务健康
docker ps --format "table {{.Names}}\t{{.Status}}"
# 应该显示所有服务为 "Up XX seconds (healthy)"
```

**常见陷阱**：
- ❌ 只执行 `docker compose restart` - **不会应用新代码**
- ❌ 直接运行测试而忘记重新构建 - **测试的是旧代码**
- ✅ 每次代码变更后都执行 `docker compose up -d --build`

**验证新代码已生效**：
```bash
# 检查容器内二进制文件时间戳
docker exec resource-meter-api ls -lh /app/resource-meter
# 应该显示最近的时间（几分钟内），而不是几天前
```

---

## 🏗️ 测试分层架构（铁律）

### ⚠️ 核心原则：每个测试层级对应固定的目录

**Resource Meter 采用标准测试金字塔模型**：

```
tests/
├── api/                          # 📡 API 接口测试层
│   ├── api_test.sh              # Shell 脚本测试
│   └── README.md
│
├── sit/                          # 🔧 系统集成测试层（SIT）
│   ├── test_sit.py              # 功能测试（10 个）
│   ├── test_data_quality_validation.py  # 数据质量验证（6 个）
│   ├── conftest.py
│   └── sit_helpers.py
│
├── uat/                          # 👥 用户验收测试层（UAT）
│   ├── test_argo_workflow.py    # ArgoWorkflow 场景（2 个）
│   ├── test_cmdb_dimensions.py  # CMDB 维度场景（2 个）
│   ├── test_gpu_accuracy.py     # GPU 精度测试（5 个）
│   ├── test_gpu_accuracy_mock.py # GPU Mock 测试（4 个）
│   ├── test_multicycle.py       # 多次启停场景（2 个）
│   ├── test_rest_api.py         # REST API 场景（2 个）
│   └── helpers/
│
└── ut/                           # 🧪 单元测试层（UT）
    └── spec_scenarios.md        # 测试场景规范

总计：33+ 个测试用例
```

### 测试层级定义（铁律）

| 测试层级 | 目录规则 | 用例数 | 测试目标 | 测试对象 | 执行频率 |
|---------|---------|--------|---------|----------|----------|
| **UT** | `internal/.../*_test.go` | - | 函数/方法正确性 | 单元代码 | 每次提交 |
| **API** | `tests/api/` | Shell | 接口契约验证 | RESTful API | 每次提交 |
| **SIT** | `tests/sit/` | **16 个** | 系统集成正确性 | K8s + DB + Service | 每次发布前 |
| **UAT** | `tests/uat/` | **17 个** | 端到端业务场景 | 完整用户流程 | 每次发布前 |

### ⚠️ 核心规则（强制执行）

**规则 1：目录对应关系（铁律）**
- ✅ **API 测试** → `tests/api/` 目录下**所有**测试文件
- ✅ **SIT 测试** → `tests/sit/` 目录下**所有**测试文件
- ✅ **UAT 测试** → `tests/uat/` 目录下**所有**测试文件
- ❌ **禁止**：将 SIT 测试放在 `tests/sit/subfolder/` 子目录中
- ❌ **禁止**：将 UAT 测试放在 `tests/uat/subfolder/` 子目录中

**规则 2：SIT 测试包含内容（铁律）**
- ✅ **功能测试**：`test_sit.py`（10 个用例）
  - Pod 生命周期测试（ADD/UPDATE/DELETE）
  - Pod 来源识别测试（DevPod/ArgoWorkflow）
  - GPU 元数据提取测试
  - CMDB 维度提取测试
  - 多次启停测试
- ✅ **数据质量验证**：`test_data_quality_validation.py`（6 个用例）
  - BUG-001: 时区一致性测试
  - BUG-002: Pod 元数据完整性测试
  - BUG-003: GPU 用量计算测试
  - BUG-004: GPU Count 验证测试
  - BUG-005: 数据一致性测试
  - BUG-006: 数据质量评分

**规则 3：SIT 回归测试必须包含所有用例（铁律）**
```bash
# ✅ 正确：运行 tests/sit/ 下所有测试（16 个用例）
pytest tests/sit/ -v -m sit

# ❌ 错误：只运行功能测试，遗漏数据质量验证
pytest tests/sit/test_sit.py -v

# ❌ 错误：只运行数据质量验证，遗漏功能测试
pytest tests/sit/test_data_quality_validation.py -v
```

**规则 4：UAT 测试包含内容（铁律）**
- ✅ `test_argo_workflow.py` - ArgoWorkflow 场景（2 个用例）
- ✅ `test_cmdb_dimensions.py` - CMDB 维度场景（2 个用例）
- ✅ `test_gpu_accuracy.py` - GPU 精度测试（5 个用例）
- ✅ `test_gpu_accuracy_mock.py` - GPU Mock 测试（4 个用例）
- ✅ `test_multicycle.py` - 多次启停场景（2 个用例）
- ✅ `test_rest_api.py` - REST API 场景（2 个用例）

### 测试执行命令（标准流程）

**完整回归测试（发布前）**：
```bash
# 1. 单元测试
make test

# 2. SIT 系统集成测试（16 个用例）
pytest tests/sit/ -v -m sit \
  --html=test_reports/sit-report-full.html \
  --self-contained-html

# 3. UAT 用户验收测试（17 个用例）
pytest tests/uat/ -v -m uat \
  --html=test_reports/uat-report.html \
  --self-contained-html

# 4. API 接口测试
cd tests/api && ./api_test.sh
```

**快速验证（开发阶段）**：
```bash
# 只运行核心 SIT 测试（功能测试）
pytest tests/sit/test_sit.py -v -m sit
```

**数据质量巡检（生产监控）**：
```bash
# 只运行数据质量验证（6 个用例）
pytest tests/sit/test_data_quality_validation.py -v -m bug_detection
```

### SIT 测试用例清单（标准）

| ID | 测试名称 | 文件位置 | 优先级 |
|----|---------|----------|--------|
| SIT-001 | K8s 集群连接测试 | test_sit.py:28 | P0 |
| SIT-002 | Pod ADD 事件接收测试 | test_sit.py:41 | P0 |
| SIT-003 | Pod UPDATE 事件接收测试 | test_sit.py:69 | P0 |
| SIT-004 | Pod DELETE 事件接收测试 | test_sit.py:107 | P0 |
| SIT-005 | 数据库写入验证 | test_sit.py:142 | P0 |
| SIT-006 | DevPod 识别测试 | test_sit.py:185 | P1 |
| SIT-007 | ArgoWorkflow 识别测试 | test_sit.py:214 | P1 |
| SIT-008 | GPU 元数据提取测试 | test_sit.py:243 | P1 |
| SIT-009 | CMDB 维度提取测试 | test_sit.py:273 | P1 |
| SIT-010 | 多次启停测试 | test_sit.py:324 | P2 |
| BUG-001 | 时区一致性测试 | test_data_quality_validation.py:50 | P0 |
| BUG-002 | Pod 元数据完整性测试 | test_data_quality_validation.py:138 | P0 |
| BUG-003 | GPU 用量计算测试 | test_data_quality_validation.py:237 | P0 |
| BUG-004 | GPU Count 验证测试 | test_data_quality_validation.py:361 | P1 |
| BUG-005 | 数据一致性测试 | test_data_quality_validation.py:471 | P1 |
| BUG-006 | 数据质量评分 | test_data_quality_validation.py:595 | P2 |

### 测试覆盖率目标

| 测试层级 | 当前覆盖率 | 目标覆盖率 | 状态 |
|---------|-----------|-----------|------|
| **UT** | 62.6% (calculator), 52.7% (informer) | ≥80% | 🟡 进行中 |
| **SIT** | 75% (功能覆盖度) | ≥90% | 🟡 良好 |
| **UAT** | 待评估 | ≥85% | 🟡 待评估 |
| **API** | 待评估 | 100% | 🟡 待评估 |

---

## 📋 测试用例设计原则（铁律）

### ⚠️ 核心原则：测试用例必须体现设计文档意图

**设计文档是测试用例的唯一真实来源**：

1. **API 测试用例**必须基于 `.api` 元数据文件（如 `desc/resource-meter-v1.0.api`）
   - ✅ 每个定义的 API 端点都必须有对应的测试用例
   - ✅ 每个请求参数都必须测试（required、optional、default）
   - ✅ 每个响应字段都必须验证
   - ❌ 禁止凭空想象测试场景

2. **SIT 测试用例**必须基于设计文档（如 `docs/design/service_layer_architecture_v1.0.md`）
   - ✅ 测试场景必须覆盖设计文档中的业务流程
   - ✅ 验收标准必须符合设计文档的功能要求
   - ❌ 禁止遗漏设计文档中的关键功能

3. **UAT 测试用例**必须基于 PRD 文档（如 `docs/scrum/prd/`）
   - ✅ 端到端测试场景必须覆盖用户故事
   - ✅ 验收标准必须符合用户需求
   - ❌ 禁止偏离 PRD 中的验收标准

### 测试用例过期的判断标准

**如果出现以下情况，说明测试用例已过期**：

1. ❌ .api 文件定义了新端点，但测试脚本中缺少对应测试
2. ❌ 设计文档添加了新功能，但 SIT/UAT 用例未覆盖
3. ❌ API 响应结构变化，但测试仍验证旧字段
4. ❌ 新增了可选参数，但测试未验证其行为

### 更新流程

**当设计文档更新时**：

```bash
# 1. 检查 .api 文件变更
git diff desc/resource-meter-v1.0.api

# 2. 更新测试用例以匹配新的 API 定义
vim tests/api_test.sh

# 3. 验证测试覆盖率
./tests/api_test.sh

# 4. 更新 QA SKILL 文档（如有新原则）
vim .claude/skills/qa/SKILL.md
```

**关键检查清单**：

- [ ] 每个 `@doc` 注释的 API 都有测试用例
- [ ] 每个 `get/post/put/delete` 路由都被测试
- [ ] 每个请求参数（optional/required）都有测试场景
- [ ] 每个响应字段都被验证
- [ ] 错误场景（400/404/500）都有测试

---

## 🔐 数据准备幂等性原则（铁律）

### ⚠️ 核心原则：测试数据清理必须完整且幂等

**数据准备阶段必须保证**：
1. **完整性**：清理所有相关表的数据，避免残留影响测试结果
2. **幂等性**：测试可以重复执行，每次都从干净状态开始
3. **原子性**：使用事务保证多表操作的原子性

### 反面教材

**❌ 错误示例 1：不完整的清理（只清理主表）**

```python
# ❌ 错误：只清理 pod_resource_status
cur.execute("DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
           (f"{test_pod_name}%",))

# 问题：GPU 用量表和历史记录残留，导致后续测试失败
```

**问题**：
- `pod_resource_gpu_usage` 表有残留数据
- `pod_resource_history` 表有残留数据
- 下次测试可能查询到旧数据

**❌ 错误示例 2：只在测试后清理**

```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_connection, test_pod_name):
    yield  # 测试执行

    # ❌ 错误：只在测试后清理
    cur.execute("DELETE FROM pod_resource_status WHERE pod_name LIKE %s", (...))
```

**问题**：
- 如果上次测试异常中断，数据库会有残留数据
- 本次测试会读取到脏数据
- 测试结果不可靠

### 正确实现

**✅ 正确示例 1：完整清理（所有相关表）**

```python
def _cleanup_pod_data(db_connection, test_pod_name):
    """
    清理 Pod 相关的所有表数据（使用事务保证原子性）

    清理顺序（考虑外键依赖）：
    1. pod_resource_gpu_usage（依赖 pod_resource_status）
    2. pod_resource_history（依赖 pod_resource_status）
    3. pod_resource_status（主表）
    """
    with db_connection.cursor() as cur:
        try:
            # 开始事务
            cur.execute("BEGIN")

            # 删除 GPU 用量记录
            cur.execute("DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE %s",
                       (f"{test_pod_name}%",))

            # 删除历史记录（使用子查询避免外键约束）
            cur.execute("""
                DELETE FROM pod_resource_history
                WHERE resource_id IN (
                    SELECT resource_id FROM pod_resource_status WHERE pod_name LIKE %s
                )
            """, (f"{test_pod_name}%",))

            # 删除 Pod 资源状态记录
            cur.execute("DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
                       (f"{test_pod_name}%",))

            # 提交事务
            db_connection.commit()

        except Exception as e:
            # 回滚事务
            db_connection.rollback()
            raise e
```

**✅ 正确示例 2：幂等操作（测试前后都清理）**

```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_connection, test_pod_name):
    """
    自动清理测试数据（幂等操作）

    ✅ 测试前清理：确保环境干净（关键！）
    ✅ 测试后清理：避免数据残留
    """
    # 测试前清理：确保环境干净（幂等操作的关键）
    _cleanup_pod_data(db_connection, test_pod_name)

    yield

    # 测试后清理：避免数据残留
    _cleanup_pod_data(db_connection, test_pod_name)
```

### 关键检查清单

**SIT 测试数据准备必须满足**：

- [ ] **测试前清理**：fixture 在 yield 之前执行清理
- [ ] **测试后清理**：fixture 在 yield 之后执行清理
- [ ] **完整清理**：清理所有相关表（gpu_usage, history, status）
- [ ] **使用事务**：多表操作使用 BEGIN/COMMIT，失败时 ROLLBACK
- [ ] **考虑外键**：按照依赖顺序删除（先删除子表，再删除主表）
- [ ] **LIKE 匹配**：支持模糊匹配（`test-sit%`），避免精确匹配遗漏数据

### 常见问题排查

**问题 1：测试数据残留**

```bash
# 症状：测试间歇性失败，查询到旧数据
# 原因：上次测试异常中断，数据未清理

# 排查：查询是否有残留数据
docker exec resource-meter-db psql -U postgres -d event_db-dev -c \
  "SELECT pod_name, user_id, created_at FROM pod_resource_status WHERE pod_name LIKE 'test-sit%' ORDER BY created_at DESC LIMIT 10;"

# 修复：手动清理所有测试数据
docker exec resource-meter-db psql -U postgres -d event_db-dev -c \
  "DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE 'test-sit%'; \
   DELETE FROM pod_resource_history WHERE resource_id IN (SELECT resource_id FROM pod_resource_status WHERE pod_name LIKE 'test-sit%'); \
   DELETE FROM pod_resource_status WHERE pod_name LIKE 'test-sit%';"
```

**问题 2：外键约束错误**

```sql
-- 症状：ERROR: cannot delete table row due to foreign key constraint
-- 原因：删除顺序错误，先删除主表导致子表引用失败

-- 修复：按照子表 → 主表的顺序删除
DELETE FROM pod_resource_gpu_usage WHERE ...;  -- 子表
DELETE FROM pod_resource_history WHERE ...;    -- 子表
DELETE FROM pod_resource_status WHERE ...;     -- 主表
```

---

## 🧹 SIT 测试幂等性策略（v2.0 更新）

### ⚠️ 核心原则：测试数据隔离与幂等性保障

**问题背景**：
- 旧实现使用共享 `test_pod_name` fixture（所有测试用例使用相同名称）
- 测试异常中断时，数据库和 K8s 集群残留测试数据
- 下次测试运行时，读取到脏数据导致测试失败
- Informer 重复处理同一 Pod 事件导致数据库冲突

### 测试策略四阶段

**1. 测试开始前：全局清理**
```python
@pytest.fixture(scope="session", autouse=True)
def global_sit_cleanup(k8s_client, db_connection):
    """
    SIT 测试会话级别的全局清理（幂等操作）

    ✅ 清理范围：
      - K8s 集群：所有 test-* Pod（dev-pod, argo, dcs, default namespace）
      - 数据库：所有 test-% 记录（pod_resource_status, gpu_usage, history）

    ✅ 清理时机：
      - 测试会话开始前（pytest_sessionstart）
      - 测试会话结束后（pytest_sessionfinish）
    """
    print("🧹 SIT 全局清理：清理所有 test-* 数据（K8s + Database）")

    # 步骤 1: 清理 K8s 资源
    clean_k8s_pods(k8s_client, "test-")

    # 步骤 2: 清理数据库
    clean_db_data(db_connection, "test-%")

    yield

    # 会话结束后再次清理
    clean_k8s_pods(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
```

**2. 数据准备阶段：独立命名**
```python
@pytest.mark.sit
def test_sit_002_pod_add_event(k8s_client, db_connection, create_devpod):
    """SIT-002: Pod ADD 事件接收测试"""
    pod_name = "test-sit-002-pod-add"  # ✅ 独立命名，避免冲突

    # Given: 创建 DevPod
    create_devpod(pod_name, gpu_count=1, namespace="dev-pod")

    # When & Then: ...
```

**命名规范**：
- 格式：`test-sit-{编号}-{用途描述}`
- 示例：
  - `test-sit-002-pod-add`
  - `test-sit-009-cmdb-dimensions`
  - `test-sit-010-multicycle`

**3. 测试执行阶段：数据隔离**
```python
# ✅ 正确：每个测试用例使用独立 pod_name
def test_sit_002_pod_add_event():
    pod_name = "test-sit-002-pod-add"  # 独立命名

def test_sit_003_pod_update_event():
    pod_name = "test-sit-003-pod-update"  # 独立命名

# ❌ 错误：多个测试用例共享同一个 pod_name
def test_sit_002_pod_add_event(test_pod_name):  # 共享 fixture
    create_devpod(test_pod_name, ...)

def test_sit_003_pod_update_event(test_pod_name):  # 共享 fixture
    create_devpod(test_pod_name, ...)  # ⚠️ 冲突！
```

**4. 测试结束后：自动清理**
```python
@pytest.fixture(scope="session", autouse=True)
def global_sit_cleanup(k8s_client, db_connection):
    """..."""
    yield

    # ✅ 自动清理所有 test-* 数据（无论测试成功/失败）
    clean_k8s_pods(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
```

### 清理函数实现

**K8s 资源清理**：
```python
def clean_k8s_pods(k8s_client, prefix, max_retries=2):
    """
    清理 K8s 中指定前缀的 Pod（幂等操作）

    ✅ 清理策略：
      - 遍历所有测试相关 namespace（dev-pod, argo, dcs, default）
      - 删除所有匹配前缀的 Pod
      - 容忍 404 错误（Pod 已不存在）

    ✅ 重试机制：
      - 网络超时或临时 API 错误时自动重试
      - 最多重试 2 次
    """
    namespaces = ["dev-pod", "argo", "dcs", "default"]

    for namespace in namespaces:
        for attempt in range(max_retries):
            try:
                pods = k8s_client.v1.list_namespaced_pod(namespace)
                deleted_count = 0

                for pod in pods.items:
                    if pod.metadata.name.startswith(prefix):
                        k8s_client.v1.delete_namespaced_pod(
                            pod.metadata.name, namespace
                        )
                        deleted_count += 1

                if deleted_count > 0:
                    print(f"   ✅ Namespace {namespace}: 删除了 {deleted_count} 个测试 Pod")
                break

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"   ⚠️  清理 K8s Pod 失败 ({namespace}): {e}")
                else:
                    time.sleep(1)  # 重试前等待
```

**数据库清理**：
```python
def clean_db_data(db_connection, pattern, max_retries=3):
    """
    清理数据库中指定模式的记录（幂等操作）

    ✅ 清理策略：
      1. pod_resource_gpu_usage: 直接删除（有 pod_name 列）
      2. pod_resource_status: 最后删除（触发 CASCADE 清理 history）

    ✅ 事务完整性：
      - 使用 BEGIN/COMMIT/ROLLBACK 保证原子性
      - 失败时自动回滚
      - 支持重试机制（最多 3 次）
    """
    for attempt in range(max_retries):
        try:
            with db_connection.cursor() as cur:
                cur.execute("BEGIN")

                # 删除 GPU 用量记录
                cur.execute(
                    "DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE %s",
                    (pattern,)
                )
                gpu_count = cur.rowcount

                # 删除 Pod 资源状态（触发 CASCADE 清理 history）
                cur.execute(
                    "DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
                    (pattern,)
                )
                status_count = cur.rowcount

                db_connection.commit()

                if gpu_count > 0 or status_count > 0:
                    print(f"   ✅ 数据库清理: GPU用量={gpu_count}, Status={status_count}")

                return

        except Exception as e:
            db_connection.rollback()

            if attempt == max_retries - 1:
                raise
            else:
                time.sleep(1)  # 重试前等待
```

### 幂等性保障机制

| 保护机制 | 作用范围 | 实现方式 |
|---------|---------|----------|
| **全局清理** | 测试会话级别 | `global_sit_cleanup` fixture（scope="session"） |
| **K8s 清理** | 集群资源 | `clean_k8s_pods()` 清理所有 test-* Pod |
| **数据库清理** | 持久化数据 | `clean_db_data()` 清理所有 test-% 记录 |
| **独立命名** | 测试用例级别 | 每个 SIT 用例使用独立 `test-sit-XXX-*` 名称 |
| **ON CONFLICT** | 数据库层 | DAO.Create() 的 `ON CONFLICT (k8s_pod_uid) DO NOTHING` |

### 关键检查清单

**SIT 测试幂等性必须满足**：

- [ ] **全局清理**：使用 `global_sit_cleanup` fixture（scope="session", autouse=True）
- [ ] **K8s 清理**：清理所有 namespace 的 test-* Pod（dev-pod, argo, dcs, default）
- [ ] **数据库清理**：清理所有相关表的 test-% 记录（status, gpu_usage, history）
- [ ] **独立命名**：每个测试用例使用 `test-sit-XXX-*` 格式的独立名称
- [ ] **重试机制**：清理失败时自动重试（K8s: 2次，数据库: 3次）
- [ ] **事务完整性**：数据库操作使用事务（BEGIN/COMMIT/ROLLBACK）

### 常见问题排查

**问题 1：测试间歇性失败（读取到旧数据）**
```bash
# 症状：测试通过率不稳定，有时 10/10，有时 8/10
# 原因：上次测试异常中断，数据库残留数据

# 排查：查询是否有残留数据
docker exec resource-meter-db psql -U postgres -d event_db-dev -c \
  "SELECT pod_name, user_id, created_at FROM pod_resource_status WHERE pod_name LIKE 'test-%' ORDER BY created_at DESC LIMIT 10;"

# 修复：手动清理所有测试数据
python3 -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port='5432', dbname='event_db-dev', user='postgres', password='postgres')
cur = conn.cursor()
cur.execute('BEGIN')
cur.execute(\"DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE 'test-%'\")
cur.execute(\"DELETE FROM pod_resource_status WHERE pod_name LIKE 'test-%'\")
conn.commit()
print('清理完成')
"
```

**问题 2：K8s Pod 冲突（409 Conflict）**
```bash
# 症状：SIT-010 多次启停测试失败，API 返回 409 Conflict
# 原因：Pod 正在删除中（deletion_timestamp 已设置），未完全从 etcd 删除

# 排查：查看 Pod 状态
kubectl get pod test-sit-010-multicycle -n dev-pod
kubectl describe pod test-sit-010-multicycle -n dev-pod

# 修复：使用 wait_pod_deleted() 等待 404
# ⚠️ DevPod 删除较慢（需要等待容器停止 + finalizer 处理），设置 60 秒超时
```

**问题 3：清理失败（事务超时）**
```bash
# 痘状：清理函数抛出数据库超时错误
# 原因：大量测试数据积累，单次删除超时

# 修复 1：增加重试次数
def clean_db_data(db_connection, pattern, max_retries=5):  # 增加到 5 次

# 修复 2：分批删除（如果数据量特别大）
for batch in range(10):
    cur.execute("DELETE FROM pod_resource_status WHERE pod_name LIKE %s LIMIT 1000", (pattern,))
    if cur.rowcount == 0:
        break
    conn.commit()
```

### 测试用例命名对照表

| 测试用例 | Pod 名称 | 说明 |
|---------|---------|------|
| SIT-001: K8s 连接 | （无 Pod） | 仅验证连接 |
| SIT-002: Pod ADD | `test-sit-002-pod-add` | ADD 事件接收 |
| SIT-003: Pod UPDATE | `test-sit-003-pod-update` | UPDATE 事件接收 |
| SIT-004: Pod DELETE | `test-sit-004-pod-delete` | DELETE 事件接收 |
| SIT-005: 数据库写入 | `test-sit-005-database-write` | 完整生命周期 |
| SIT-006: DevPod 识别 | `test-sit-006-devpod-identification` | 资源类型识别 |
| SIT-007: ArgoWorkflow 识别 | `test-sit-007-argo-workflow` | ArgoWorkflow 识别 |
| SIT-008: GPU 元数据 | `test-sit-008-gpu-metadata` | GPU 数量提取 |
| SIT-009: CMDB 维度 | `test-sit-009-cmdb-dimensions` | CMDB 字段提取 |
| SIT-010: 多次启停 | `test-sit-010-multicycle` | 2 次启停周期 |

---

## 测试报告管理

### 命名规范

**报告文件**：`sit_report-{desc}-{timestamp}.md`
**日志文件**：`sit_test_result-{desc}-{timestamp}.log`
- `{desc}`: auto, interactive, quick, regression
- `{timestamp}`: YYYYMMDD_HHMMSS
- 示例：`sit_report-auto-20260201_120000.md`

### 归档规则

**⚠️ 重要**：`test_reports/` 目录下只保留当前的测试报告

**执行时机**：每次新一轮测试开始之前

**归档步骤**：
```bash
mkdir -p test_reports/archive
mv test_reports/sit_report-*.md test_reports/archive/
mv test_reports/sit_test_result-*.log test_reports/archive/
mv test_reports/sit_results.csv test_reports/archive/sit_results_$(date '+%Y%m%d_%H%M%S').csv
```

**禁止事项**：
- ❌ 不要在 `test_reports/` 下保留多个往期报告
- ❌ 不要手动删除 `archive/` 目录中的文件

---

## SIT 测试框架

**位置**：`tests/sit/run_sit_tests.sh`

### 三种运行模式

**1. 全自动化（默认）**：
```bash
./tests/sit/run_sit_tests.sh --auto
```
- 无人值守，自动执行所有 10 个测试场景
- 适用：CI/CD、回归测试

**2. 交互式（半自动）**：
```bash
./tests/sit/run_sit_tests.sh --interactive
```
- 每个测试后暂停，等待用户确认
- 适用：调试、问题排查

**3. 快速模式**：
```bash
./tests/sit/run_sit_tests.sh --quick
```
- 只运行 5 个关键测试（SIT-001, 002, 005, 006, 009）
- 适用：快速验证

### 测试场景

| ID | 测试场景 | 优先级 |
|----|---------|--------|
| SIT-001 | K8s 集群连接 | P0 |
| SIT-002 | Pod ADD 事件 | P0 |
| SIT-003 | Pod UPDATE 事件 | P1 |
| SIT-004 | Pod DELETE 事件 | P0 |
| SIT-005 | 数据库写入 | P0 |
| SIT-006 | DevPod 识别 | P1 |
| SIT-007 | ArgoWorkflow 识别 | P1 |
| SIT-008 | GPU 元数据提取 | P1 |
| SIT-009 | CMDB 维度提取 | P1 |
| SIT-010 | 多次启停 | P2 |

### 快速测试

```bash
# 创建测试 Pod
./tests/sit/sit_helpers.sh create-devpod test-debug-001 4 dev-pod 600
sleep 8
./tests/sit/sit_helpers.sh query-status test-debug-001
./tests/sit/sit_helpers.sh delete test-debug-001 dev-pod
```

---

## TDD 验收标准

### 🟢 绿灯（通过）
- ✅ 所有 SIT 测试通过（10/10）
- ✅ 所有 UAT 核心测试通过
- ✅ GPU 用量计算误差 < 1%
- ✅ 无 P0/P1 级 Bug

### 🟡 黄灯（有条件通过）
- ⚠️ SIT 测试通过率 70-89%
- ⚠️ 核心功能可用，但存在问题
- ⚠️ 存在 P1 级 Bug（不影响核心功能）

### 🔴 红灯（不通过）
- ❌ SIT 测试失败（无法连接 K8s 或数据库）
- ❌ GPU 用量计算错误（误差 > 5%）
- ❌ 存在 P0 级 Bug（数据丢失、事件丢失）
- ❌ 通过率 < 70%

---

## 测试流程

### Phase 1: UT 回归测试

```bash
make test
go test -v --cover ./internal/pkgs/... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total
# 目标：核心组件覆盖率 ≥60%
```

### Phase 2: SIT 系统集成测试

```bash
# 全自动化测试
./tests/sit/run_sit_tests.sh --auto

# 查看报告
cat test_reports/sit_report-auto-*.md

# 如果发现问题，半自动化调试
./tests/sit/run_sit_tests.sh --interactive

# 修复后快速验证
./tests/sit/run_sit_tests.sh --quick
```

### Phase 3: UAT 用户验收测试

```bash
./tests/uat/run_uat_tests.sh --auto
```

---

## 问题报告模板

```markdown
## 问题 ID: QA-SIT-XXX

**严重级别**: 🔴 P0 / 🟡 P1 / 🟢 P2
**测试场景**: SIT-XXX: <测试场景名称>
**发现时间**: YYYY-MM-DD HH:MM:SS

### 问题描述
<简要描述问题>

### 实际结果
<实际发生的情况>

### 预期结果
<应该发生的情况>

### 根因分析
<问题根本原因>

### 修复位置
- <文件路径>:<行号> - <问题描述>

### 验收标准
- <验收标准 1>
- <验收标准 2>
```

---

## 🔄 重构测试标准化流程（铁律）

### ⚠️ 核心原则：基线对比法

**重构测试必须遵循"基线对比法"**：
1. 先验证环境可用
2. 建立测试基线
3. 执行重构
4. 回归测试对比
5. 判断问题来源（环境 vs 重构）

### 标准流程（四阶段）

**阶段 1: 重构前准备 ✅**
```bash
# 1. 验证环境可用
cd deploy/docker
docker compose up -d --build
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. 建立测试基线
cd ../..
make test > logs/baseline_unit.log 2>&1
echo "基线测试时间: $(date)" > TEST_BASELINE.md
echo "单元测试通过率: 100%" >> TEST_BASELINE.md

# 3. SIT 基线
pytest tests/sit/ -v --html=test_reports/baseline_sit.html \
  --self-contained-html > logs/baseline_sit.log 2>&1

# 4. 记录基线结果
echo "SIT测试通过率: XX%" >> TEST_BASELINE.md
echo "数据库状态: $(docker exec resource-meter-db psql -U postgres -d event_db-dev -c "SELECT COUNT(*) FROM pod_resource_status;")" >> TEST_BASELINE.md
```

**阶段 2: 执行重构 ✅**
```bash
# 使用 git mv 保留历史
git mv internal/pkgs internal/pkg
# 更新 import 路径...
# 提交重构
git commit -m "refactor: 合并 internal/pkgs/ 到 internal/pkg/"
```

**阶段 3: 回归测试 ✅**
```bash
# 1. 重新构建（Docker 环境）
cd deploy/docker
docker compose up -d --build
cd ../..

# 2. 单元测试回归
make test > logs/refactor_unit.log 2>&1
diff logs/baseline_unit.log logs/refactor_unit.log

# 3. SIT 完整回归（⚠️ 不使用 --maxfail）
pytest tests/sit/ -v --html=test_reports/refactor_sit.html \
  --self-contained-html > logs/refactor_sit.log 2>&1

# 4. 对比结果
# 基线通过率 vs 重构后通过率
```

**阶段 4: 问题诊断 ✅**
```bash
# 判断问题来源的决策树
if [ 重构后测试失败 ]; then
    if [ 基线测试也失败 ]; then
        echo "❌ 环境问题：测试前基线就有问题"
        echo "修复：先解决环境问题，再重构"
    else
        echo "❌ 重构问题：基线通过，重构后失败"
        echo "修复：检查重构引入的变更"
    fi
fi
```

### 反面教材（2026-02-13 经验教训）

**❌ 错误做法 1：先重构后建立基线**
```bash
# 错误：直接重构代码
git mv internal/pkgs internal/pkg

# 然后运行测试
make test
pytest tests/sit/ --maxfail=5  # ❌ 使用 --maxfail 提前终止

# 问题：没有基线对比，无法判断问题是环境导致还是重构导致
```

**❌ 错误做法 2：数据库污染导致误判**
```bash
# 错误：在有残留数据的数据库上测试
pytest tests/sit/test_data_quality_validation.py::test_bug_005_data_consistency
# 结果：失败 ❌

# 误判：以为是重构导致的问题
# 实际：数据库有 37 条残留记录

# 正确：测试前清理数据库
docker compose down -v
docker compose up -d
# 重新初始化表结构
cat db/ddl/002_pod_resource_tables.sql | docker exec -i resource-meter-db psql -U postgres -d event_db-dev

# 再次测试：通过 ✅
```

### 关键检查清单

**重构测试必须满足**：

- [ ] **基线建立**：重构前先运行测试并记录基线结果
- [ ] **环境验证**：确认 Docker 容器运行的是最新代码（`--build`）
- [ ] **数据库清理**：测试前清理数据库或使用专用测试库
- [ ] **完整测试**：不使用 `--maxfail`，执行所有测试用例
- [ ] **结果对比**：基线 vs 重构后，通过率差异 ≤5%
- [ ] **问题归因**：明确区分"环境问题"和"重构问题"

---

## 🐛 问题排查方法论（铁律）

### ⚠️ 核心原则：代码优先原则

**"代码是唯一的真实来源"**：
1. 遇到问题先阅读代码，理解逻辑
2. 再检查配置，是否符合代码预期
3. 最后修改配置，而不是"试错"

### 问题排查三步法

**Step 1: 阅读代码，理解逻辑 ✅**
```bash
# 示例：K8s 认证失败问题

# 1. 阅读 Informer 工厂代码
vim internal/pkg/k8s/informer/factory.go

# 2. 理解认证优先级（lines 34-88）
# Priority 1: K8sBearerTokenPath
# Priority 2: K8sBearerToken
# Priority 3: K8sKubeconfigPath
# Priority 4: Default kubeconfig (/root/.kube/config)

# 3. 检查当前配置
cat etc/config/config-docker.yaml | grep -A 5 "Kubeconfig:"

# 4. 判断：哪个字段优先级最高？
# 如果 K8sBearerToken 不为空，会优先使用它，而不是 kubeconfig
```

**Step 2: 检查配置，是否符合预期 ✅**
```bash
# 1. 检查配置文件
cat etc/config/config-docker.yaml

# 2. 对比代码逻辑
# 代码：if cfg.K8sBearerToken != "" { use Bearer Token }
# 配置：K8sBearerToken: "invalid-token"
# 结论：会使用无效的 token，而不是 kubeconfig

# 3. 检查 kubeconfig 内容
kubectl config view --raw | head -20
# 发现：kubeconfig 使用证书认证，不是 token 认证
```

**Step 3: 修改配置，一次到位 ✅**
```bash
# ✅ 正确：根据代码逻辑，清空 K8sBearerToken
vim etc/config/config-docker.yaml
# K8sBearerToken: ""  # 留空，使用 kubeconfig 认证
# K8sBearerTokenPath: ""
# K8sKubeconfigPath: ""

# 重新启动服务
docker compose up -d --build
```

### 反面教材（2026-02-13 经验教训）

**❌ 错误做法：试错式修改配置**
```bash
# 遇到 "Unauthorized" 错误

# ❌ 尝试 1：修改 docker-compose.yml 挂载路径
vim docker-compose.yml
# volumes:
#   - /home/mini/.kube/prod_gpu/config:/root/.kube/config:ro
docker compose restart
# 结果：还是失败

# ❌ 尝试 2：再修改成别的路径
vim docker-compose.yml
# volumes:
#   - ~/.kube/config:/root/.kube/config:ro
docker compose restart
# 结果：还是失败

# ❌ 尝试 3：反复修改配置
# ...（多次试错）

# 用户明确批评：
# "这个处理方式我不满意...既然你知道bearerToken的挂载顺序已经提前了,
#  就需要根据新的挂载顺序,通过本地kubeconfig区生成新的bearerToken...
#  而不是强行再去改docker compose配置,反复拉扯!!!"

# ✅ 正确做法：
# 1. 阅读 factory.go 代码
# 2. 理解认证优先级
# 3. 发现 K8sBearerToken 有值（虽然是过期的）
# 4. 清空 K8sBearerToken，留空使用 kubeconfig
# 5. 一次修改，问题解决
```

### 关键检查清单

**遇到配置问题时，必须**：

- [ ] **阅读代码**：找到处理配置的代码逻辑
- [ ] **理解优先级**：清楚配置字段的优先级顺序
- [ ] **检查当前值**：查看当前配置文件的实际值
- [ ] **判断符合性**：当前配置是否符合代码逻辑
- [ ] **一次性修改**：基于理解，一次修改到位
- [ ] **禁止试错**：不要"试试这个"、"试试那个"

---

## ⚠️ 完整回归测试规范（铁律）

### 核心原则：回归测试必须完整执行

**禁止使用 `--maxfail` 提前终止测试**：
- ❌ `pytest tests/sit/ --maxfail=5` - 只跑 5 个测试就停止
- ✅ `pytest tests/sit/ -v` - 完整执行所有测试用例

### 为什么必须完整执行？

**场景 1：早期失败不代表后续都失败**
```bash
# 使用 --maxfail=5 的执行顺序
test_bug_005_data_consistency  # ❌ 失败（数据库有残留数据）
test_gpu_product_from_node_cache_a100  # ❌ 失败（H100 节点不存在）
test_gpu_product_from_node_cache_h100  # ❌ 失败（H100 节点不存在）
test_gpu_product_node_labels_priority[A100]  # ❌ 失败（A100 调度失败）
test_gpu_product_node_labels_priority[H100]  # ❌ 失败（H100 节点不存在）
# 🛑 提前终止，剩余 24 个测试未执行

# 实际上，后续测试可能都是通过的：
test_sit_001_k8s_connection  # ✅ 本来可以通过
test_sit_002_pod_add_event  # ✅ 本来可以通过
# ... 22 个测试本来都通过
```

**场景 2：需要完整数据生成报告**
```bash
# 不完整的测试报告：
# - 总测试数: 5（实际应该是 29）
# - 通过数: 0
# - 通过率: 0%（误导性的数据）
# - 失败原因: 无法判断（只看到前 5 个失败）

# 完整的测试报告：
# - 总测试数: 29
# - 通过数: 23 ✅
# - 失败数: 6
# - 通过率: 79.3%
# - 失败原因: 全部是 GPU 产品提取测试（环境限制）
```

### 什么时候可以使用 --maxfail？

**唯一允许的场景：快速开发验证**
```bash
# ✅ 允许：开发阶段，快速验证单个修复
pytest tests/sit/test_sit.py::test_sit_002_pod_add_event -v

# ✅ 允许：调试特定测试
pytest tests/sit/test_data_quality_validation.py -v -k "test_bug_005"

# ❌ 禁止：回归测试、发布前测试、重构验证
pytest tests/sit/ --maxfail=5  # 禁止！
```

### 回归测试标准命令

**完整回归（发布前、重构验证）**：
```bash
# 1. 单元测试
make test

# 2. SIT 完整回归（⚠️ 不使用 --maxfail）
pytest tests/sit/ -v \
  --html=test_reports/sit-report-full.html \
  --self-contained-html

# 3. UAT 完整回归
pytest tests/uat/ -v \
  --html=test_reports/uat-report.html \
  --self-contained-html
```

---

## 常见问题排查

### 问题 1：Pod 未被监听（数据库无记录）

```bash
# 确认 Pod 已创建
kubectl get pod test-xxx -n dev-pod

# 确认 Pod 有正确的 label
kubectl get pod test-xxx -n dev-pod -o jsonpath='{.metadata.labels}'

# 查看 Informer 日志
docker logs resource-meter-api --tail 50 | grep -i "event\|handler"
```

### 问题 2：状态未更新（PENDING 不变）

```bash
# 确认 Pod 已就绪
kubectl get pod test-xxx -n dev-pod

# 查看 Informer UPDATE 事件
docker logs resource-meter-api --tail 100 | grep -i "update\|state"
```

### 问题 3：GPU 用量为空

```bash
# 查询 Pod 状态记录
./tests/sit/sit_helpers.sh query-status test-xxx

# 查看 Informer DELETE 事件日志
docker logs resource-meter-api --tail 100 | grep -i "delete\|release\|gpu"
```

### 问题 4：K8s 认证失败（Unauthorized）【2026-02-13 新增】

```bash
# 症状：Failed to watch *v1.Pod: Unauthorized

# Step 1: 阅读 Informer 工厂代码
vim internal/pkg/k8s/informer/factory.go
# 理解认证优先级（lines 34-88）：
# 1. K8sBearerTokenPath（最高优先级）
# 2. K8sBearerToken
# 3. K8sKubeconfigPath
# 4. Default kubeconfig (/root/.kube/config)

# Step 2: 检查配置文件
cat etc/config/config-docker.yaml | grep -A 10 "Kubeconfig:"

# Step 3: 判断哪个字段优先级最高
# 如果 K8sBearerToken 不为空，会优先使用它

# Step 4: 检查 kubeconfig 认证类型
kubectl config view --raw
# 如果使用 client-certificate-data（证书认证），不需要 Bearer Token

# Step 5: 修复配置
vim etc/config/config-docker.yaml
# K8sBearerToken: ""  # 清空，使用 kubeconfig 证书认证
# K8sBearerTokenPath: ""
# K8sKubeconfigPath: ""

# 重新启动服务
docker compose up -d --build
```

---

## 最佳实践

1. **每次修改代码后**：运行快速验证（单个测试用例）
2. **每次修复 bug 后**：运行完整 SIT 测试
3. **准备发布前**：运行完整 SIT + UAT 测试
4. **发现问题时**：使用交互式模式深度调试
5. **报告管理**：每次测试前自动归档往期报告

**⚠️ 重要提醒**：开发修复后，应使用官方SIT测试验证（`./tests/sit/run_sit_tests.sh`），参考 `.claude/skills/developer/SKILL.md` 中的测试规范

---

## 关键资源

**测试文档**：
- `tests/sit/README.md` - SIT 测试使用指南
- `CLAUDE.md` - 项目 CLAUDE.md

**SKILL 文档**：
- `.claude/skills/developer/SKILL.md` - 开发测试规范（重要！）
- `.claude/skills/scrum_master/SKILL.md` - Scrum 工作流程

---

**版本**: v3.0
**更新日期**: 2026-02-13
**维护者**: QA Team

### v3.0 更新内容（2026-02-13）
- ✅ **新增重构测试标准化流程（铁律）**：基线对比法，四阶段流程
- ✅ **新增问题排查方法论（铁律）**：代码优先原则，三步排查法
- ✅ **新增完整回归测试规范（铁律）**：禁止使用 --maxfail 提前终止
- ✅ **新增 K8s 认证失败排查案例**：Unauthorized 错误排查五步法
- ✅ **固化反面教材**：2026-02-13 经验教训（试错式配置、数据库污染、不完整测试）

### v2.2 更新内容（2026-02-10）
- ✅ **新增测试分层架构（铁律）**：明确 UT/API/SIT/UAT 对应目录
- ✅ **固化 SIT 测试规则**：SIT 必须包含 `tests/sit/` 下所有 16 个用例
  - 功能测试（10 个）：`test_sit.py`
  - 数据质量验证（6 个）：`test_data_quality_validation.py`
- ✅ **固化 UAT 测试规则**：UAT 必须包含 `tests/uat/` 下所有 17 个用例
- ✅ **新增标准测试执行流程**：完整回归、快速验证、数据质量巡检
- ✅ **新增 SIT 测试用例清单**：16 个用例的完整列表和优先级
- ✅ **新增测试覆盖率目标**：UT 80%, SIT 90%, UAT 85%, API 100%

### v2.1 更新内容（2026-02-10）
- ✅ 新增 SIT 测试幂等性策略（四阶段：全局清理、独立命名、数据隔离、自动清理）
- ✅ 新增 `global_sit_cleanup` fixture（scope="session"）
- ✅ 新增 `clean_k8s_pods()` 和 `clean_db_data()` 函数
- ✅ 更新测试用例命名规范（`test-sit-XXX-*` 独立命名）
- ✅ 新增幂等性保障机制对照表
- ✅ 新增测试用例命名对照表
- ✅ 新增 SIT 常见问题排查（间歇性失败、409 Conflict、清理失败）

### v2.0 更新内容（2026-02-03）
- ✅ 新增数据准备幂等性原则（铁律）
- ✅ 新增测试用例设计原则（基于设计文档）
- ✅ 新增测试报告管理规范
