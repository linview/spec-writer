---
name: event-db-cmdb-design
description: PostgreSQL CMDB 扩展设计 - 为 event_db 添加 Dev-Pod 生命周期管理、GPU 用量追踪、业务属性关联
tags: [postgresql, cmdb, gpu-tracking, dev-pod, event-db]
---

# Event DB CMDB 设计技能

## 适用场景

当需要在 PostgreSQL event_db 中管理 Dev-Pod 生命周期、追踪 GPU 用量、关联业务属性时使用此设计模式。

**典型场景**：
- Dev-Pod 生命周期管理（创建→运行→停止→释放）
- GPU 用量追踪（gpu_count × hours，支持多次启停）
- CMDB 业务属性关联（用户、团队、项目维度）

---

## 设计原则

### 简单化 Trigger（符合 event_db 策略）

- ✅ **Trigger 只做简单计算**：3-5 行代码（类似 `algorithm_artifact_meta`）
- ✅ **存储过程封装复杂逻辑**：多表操作、状态转换、业务逻辑
- ✅ **BEFORE 触发器为主**：自动维护字段、计算值
- ✅ **遵循命名规范**：`trg_*` trigger，`verb_noun_*` function

### 独立系统设计

- ✅ **Dev-Pod 是独立系统**：与 event_db.tasks 表无关
- ✅ **独立主键**：使用 UUID 作为 `pod_id`，不依赖 tasks.uuid
- ✅ **应用层调用存储过程**：不依赖 trigger 执行复杂业务逻辑

### 状态机设计

支持 Dev-Pod 多次启停，精确计算 GPU 算力：

```
PENDING → RUNNING → STOPPED → RUNNING → RELEASED
            ↑         ↓
            └─────────┘
```

---

## 快速开始

### 1. 创建 CMDB 维度表

```sql
-- 用户表
CREATE TABLE cmdb_users (
    user_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(128) UNIQUE NOT NULL,
    display_name VARCHAR(128),
    email VARCHAR(255),
    employee_id VARCHAR(64)
);

-- 团队表（支持层级）
CREATE TABLE cmdb_teams (
    team_id VARCHAR(64) PRIMARY KEY,
    team_code VARCHAR(64) UNIQUE NOT NULL,
    team_name VARCHAR(128) NOT NULL,
    parent_team_id VARCHAR(64),
    leader_user_id VARCHAR(64)
);

-- 用户-团队关系（多对多）
CREATE TABLE cmdb_user_team_memberships (
    membership_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    team_id VARCHAR(64) NOT NULL,
    role VARCHAR(32) DEFAULT 'MEMBER',
    joined_at TIMESTAMP,
    left_at TIMESTAMP
);

-- 项目表（含 GPU 配额）
CREATE TABLE cmdb_projects (
    project_id VARCHAR(64) PRIMARY KEY,
    project_code VARCHAR(64) UNIQUE NOT NULL,
    project_name VARCHAR(128) NOT NULL,
    owner_team_id VARCHAR(64),
    monthly_gpu_quota_hours DECIMAL(10,2) DEFAULT 0
);
```

### 2. 创建 Dev-Pod 状态表

```sql
CREATE TABLE dev_pod_status (
    pod_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_name VARCHAR(128) UNIQUE NOT NULL,
    k8s_statefulset_name VARCHAR(128),

    -- 业务归属
    user_id VARCHAR(64),
    team_id VARCHAR(64),
    project_id VARCHAR(64),

    -- 资源规格
    cpu_request VARCHAR(16),
    memory_request VARCHAR(16),
    gpu_count INTEGER DEFAULT 0,
    gpu_product VARCHAR(64),
    rdma_enabled BOOLEAN DEFAULT FALSE,

    -- 生命周期状态
    status VARCHAR(32) DEFAULT 'PENDING',

    -- 时间轴
    requested_at TIMESTAMP,
    approved_at TIMESTAMP,
    first_active_at TIMESTAMP,
    last_active_at TIMESTAMP,
    stopped_at TIMESTAMP,
    released_at TIMESTAMP,

    -- 镜像和访问信息
    image_name VARCHAR(255),
    image_tag VARCHAR(128),
    ssh_node_port INTEGER,
    ssh_host_ip VARCHAR(64),
    workspace_pvc_name VARCHAR(128),

    FOREIGN KEY (user_id) REFERENCES cmdb_users(user_id),
    FOREIGN KEY (team_id) REFERENCES cmdb_teams(team_id),
    FOREIGN KEY (project_id) REFERENCES cmdb_projects(project_id)
);
```

### 3. 创建 GPU 使用记录表（支持多次启停）

```sql
CREATE TABLE dev_pod_gpu_usage (
    usage_id BIGSERIAL PRIMARY KEY,
    pod_id UUID NOT NULL,
    pod_name VARCHAR(128),

    -- GPU 信息
    gpu_count INTEGER NOT NULL,
    gpu_product VARCHAR(64),

    -- 使用时段（支持多次启停）
    usage_cycle INTEGER NOT NULL DEFAULT 1,
    usage_start_at TIMESTAMP NOT NULL,
    usage_end_at TIMESTAMP,

    -- GPU 使用率
    gpu_avg_usage_percentage DECIMAL(5,2),

    -- 计算结果（由 trigger 自动计算）
    duration_seconds INTEGER,
    gpu_hours DECIMAL(10,4),

    FOREIGN KEY (pod_id) REFERENCES dev_pod_status(pod_id) ON DELETE CASCADE
);
```

### 4. 创建运维历史表

```sql
CREATE TABLE dev_pod_history (
    history_id BIGSERIAL PRIMARY KEY,
    pod_id UUID NOT NULL,
    pod_name VARCHAR(128),

    -- 操作信息
    action VARCHAR(32) NOT NULL,
    action_from_status VARCHAR(32),
    action_to_status VARCHAR(32),

    -- 操作者信息
    operator_user_id VARCHAR(64),
    operator_username VARCHAR(128),
    operator_type VARCHAR(32) DEFAULT 'USER',

    -- 操作详情
    action_description TEXT,
    action_metadata JSONB,

    action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pod_id) REFERENCES dev_pod_status(pod_id) ON DELETE CASCADE
);
```

### 5. 创建简单 Trigger（符合 event_db 策略）

```sql
-- Trigger 1: 自动更新时间戳（3 行代码）
CREATE OR REPLACE FUNCTION update_dev_pod_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_dev_pod_status_timestamp
BEFORE UPDATE ON dev_pod_status
FOR EACH ROW
EXECUTE FUNCTION update_dev_pod_status_timestamp();

-- Trigger 2: 自动计算 GPU hours（7 行代码）
CREATE OR REPLACE FUNCTION calculate_dev_pod_gpu_hours()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.usage_end_at IS NOT NULL AND OLD.usage_end_at IS NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.usage_end_at - NEW.usage_start_at));
        NEW.gpu_hours := NEW.gpu_count
                      * (NEW.duration_seconds / 3600.0)
                      * COALESCE(NEW.gpu_avg_usage_percentage, 100.0) / 100.0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_dev_pod_gpu_hours
BEFORE UPDATE ON dev_pod_gpu_usage
FOR EACH ROW
EXECUTE FUNCTION calculate_dev_pod_gpu_hours();
```

---

## 核心 API：存储过程

### 存储过程 1: 创建 Dev-Pod

```sql
CREATE OR REPLACE FUNCTION create_dev_pod(
    p_pod_name VARCHAR,
    p_k8s_statefulset_name VARCHAR,
    p_user_id VARCHAR,
    p_team_id VARCHAR,
    p_project_id VARCHAR,
    p_cpu_request VARCHAR,
    p_memory_request VARCHAR,
    p_gpu_count INTEGER,
    p_gpu_product VARCHAR
) RETURNS UUID AS $$
DECLARE
    v_pod_id UUID;
    v_team_id VARCHAR;
BEGIN
    -- 自动推断 team_id（如果未提供）
    IF p_team_id IS NULL THEN
        SELECT team_id INTO v_team_id
        FROM cmdb_user_team_memberships
        WHERE user_id = p_user_id AND left_at IS NULL
        LIMIT 1;
    ELSE
        v_team_id := p_team_id;
    END IF;

    -- 创建 Dev-Pod 记录
    INSERT INTO dev_pod_status (
        pod_name, k8s_statefulset_name, user_id, team_id, project_id,
        cpu_request, memory_request, gpu_count, gpu_product,
        status, requested_at
    ) VALUES (
        p_pod_name, p_k8s_statefulset_name, p_user_id, v_team_id, p_project_id,
        p_cpu_request, p_memory_request, p_gpu_count, p_gpu_product,
        'PENDING', CURRENT_TIMESTAMP
    ) RETURNING pod_id INTO v_pod_id;

    -- 记录历史
    INSERT INTO dev_pod_history (
        pod_id, pod_name, action, action_from_status, action_to_status,
        operator_user_id, operator_username, action_description
    ) VALUES (
        v_pod_id, p_pod_name, 'CREATE', NULL, 'PENDING',
        p_user_id, NULL, '创建 Dev-Pod'
    );

    RETURN v_pod_id;
END;
$$ LANGUAGE plpgsql;
```

### 存储过程 2: 更新 Dev-Pod 状态（核心逻辑）

```sql
CREATE OR REPLACE FUNCTION update_dev_pod_status(
    p_pod_id UUID,
    p_new_status VARCHAR,
    p_operator_user_id VARCHAR,
    p_operator_username VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    v_old_status VARCHAR;
    v_pod_name VARCHAR;
BEGIN
    -- 获取当前状态
    SELECT status, pod_name INTO v_old_status, v_pod_name
    FROM dev_pod_status
    WHERE pod_id = p_pod_id;

    -- 状态转换验证
    IF p_new_status = 'RUNNING' AND v_old_status NOT IN ('PENDING', 'STOPPED') THEN
        RAISE EXCEPTION '无效状态转换: % TO %', v_old_status, p_new_status;
    END IF;

    -- 更新状态表
    UPDATE dev_pod_status SET
        status = p_new_status,
        first_active_at = CASE WHEN p_new_status = 'RUNNING' AND first_active_at IS NULL
                               THEN CURRENT_TIMESTAMP ELSE first_active_at END,
        last_active_at = CASE WHEN p_new_status = 'RUNNING'
                              THEN CURRENT_TIMESTAMP ELSE last_active_at END,
        stopped_at = CASE WHEN p_new_status = 'STOPPED'
                         THEN CURRENT_TIMESTAMP ELSE stopped_at END,
        released_at = CASE WHEN p_new_status = 'RELEASED'
                          THEN CURRENT_TIMESTAMP ELSE released_at END
    WHERE pod_id = p_pod_id;

    -- 记录历史
    INSERT INTO dev_pod_history (
        pod_id, pod_name, action, action_from_status, action_to_status,
        operator_user_id, operator_username, action_description
    ) VALUES (
        p_pod_id, v_pod_name, 'STATUS_CHANGE', v_old_status, p_new_status,
        p_operator_user_id, p_operator_username, '状态变更'
    );

    -- 管理 GPU 用量记录
    IF p_new_status = 'RUNNING' THEN
        -- 创建新的 GPU 使用记录
        INSERT INTO dev_pod_gpu_usage (
            pod_id, pod_name, gpu_count, gpu_product,
            usage_cycle, usage_start_at
        ) SELECT
            p_pod_id, v_pod_name, gpu_count, gpu_product,
            COALESCE(MAX(usage_cycle) + 1, 1), CURRENT_TIMESTAMP
        FROM dev_pod_gpu_usage
        WHERE pod_id = p_pod_id;

    ELSIF p_new_status IN ('STOPPED', 'RELEASED') THEN
        -- 关闭当前的 GPU 使用记录（触发器会自动计算 gpu_hours）
        UPDATE dev_pod_gpu_usage
        SET usage_end_at = CURRENT_TIMESTAMP
        WHERE pod_id = p_pod_id AND usage_end_at IS NULL;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

---

## 常用查询

### 按用户统计 Dev-Pod 和 GPU 用量

```sql
SELECT
    u.username,
    s.pod_name,
    s.status,
    s.gpu_count,
    s.first_active_at,
    COALESCE(SUM(gu.gpu_hours), 0) AS total_gpu_hours
FROM cmdb_users u
JOIN dev_pod_status s ON u.user_id = s.user_id
LEFT JOIN dev_pod_gpu_usage gu ON s.pod_id = gu.pod_id
WHERE u.username = 'zhangsan'
GROUP BY u.username, s.pod_id
ORDER BY s.first_active_at DESC;
```

### 按团队统计 GPU 用量（按项目聚合）

```sql
SELECT
    t.team_name,
    p.project_name,
    COUNT(DISTINCT s.user_id) AS user_count,
    COUNT(DISTINCT s.pod_id) AS pod_count,
    SUM(s.gpu_count) AS total_gpu_count,
    COALESCE(SUM(gu.gpu_hours), 0) AS total_gpu_hours
FROM cmdb_teams t
JOIN dev_pod_status s ON t.team_id = s.team_id
LEFT JOIN dev_pod_gpu_usage gu ON s.pod_id = gu.pod_id
LEFT JOIN cmdb_projects p ON s.project_id = p.project_id
WHERE t.team_name = '算法团队'
GROUP BY t.team_name, p.project_name
ORDER BY total_gpu_hours DESC;
```

### 查询项目月度 GPU 配额使用情况

```sql
SELECT
    p.project_name,
    p.monthly_gpu_quota_hours AS quota,
    COALESCE(SUM(gu.gpu_hours) FILTER (
        WHERE gu.usage_start_at >= DATE_TRUNC('month', CURRENT_TIMESTAMP)
    ), 0) AS used_hours,
    p.monthly_gpu_quota_hours - COALESCE(SUM(gu.gpu_hours) FILTER (
        WHERE gu.usage_start_at >= DATE_TRUNC('month', CURRENT_TIMESTAMP)
    ), 0) AS remaining_hours
FROM cmdb_projects p
LEFT JOIN dev_pod_status s ON p.project_id = s.project_id
LEFT JOIN dev_pod_gpu_usage gu ON s.pod_id = gu.pod_id
WHERE p.project_name = 'D4Q2项目'
GROUP BY p.project_name, p.monthly_gpu_quota_hours;
```

### 查询活跃的 Dev-Pod

```sql
SELECT
    s.pod_name,
    u.username,
    t.team_name,
    p.project_name,
    s.gpu_count,
    s.gpu_product,
    s.last_active_at,
    s.ssh_host_ip,
    s.ssh_node_port
FROM dev_pod_status s
JOIN cmdb_users u ON s.user_id = u.user_id
LEFT JOIN cmdb_teams t ON s.team_id = t.team_id
LEFT JOIN cmdb_projects p ON s.project_id = p.project_id
WHERE s.status = 'RUNNING'
ORDER BY s.last_active_at DESC;
```

---

## 应用层调用示例（Go 代码）

### 创建 Dev-Pod

```go
func (s *DevPodService) CreateDevPod(req *CreateDevPodRequest) (uuid.UUID, error) {
    var podID uuid.UUID
    err := s.db.QueryRow(`
        SELECT create_dev_pod($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `, req.PodName, req.K8sStatefulSetName,
       req.UserID, req.TeamID, req.ProjectID,
       req.CPURequest, req.MemoryRequest,
       req.GPUCount, req.GPUProduct).Scan(&podID)

    return podID, err
}
```

### 更新 Dev-Pod 状态

```go
func (s *DevPodService) StopDevPod(podID uuid.UUID, operator string) error {
    _, err := s.db.Exec(`
        SELECT update_dev_pod_status($1, 'STOPPED', $2, $2)
    `, podID, operator)
    return err
}

func (s *DevPodService) ReleaseDevPod(podID uuid.UUID, operator string) error {
    _, err := s.db.Exec(`
        SELECT update_dev_pod_status($1, 'RELEASED', $2, $2)
    `, podID, operator)
    return err
}
```

---

## 最佳实践

### 1. Trigger 简单化

```sql
-- ✅ Trigger 只做 3-5 行简单计算
CREATE OR REPLACE FUNCTION calculate_dev_pod_gpu_hours()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.usage_end_at IS NOT NULL AND OLD.usage_end_at IS NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.usage_end_at - NEW.usage_start_at));
        NEW.gpu_hours := NEW.gpu_count * (NEW.duration_seconds / 3600.0)
                      * COALESCE(NEW.gpu_avg_usage_percentage, 100.0) / 100.0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ❌ 不要在 Trigger 中做多表操作
-- ❌ 不要在 Trigger 中做业务逻辑判断
```

### 2. 存储过程封装复杂逻辑

```sql
-- ✅ 多表操作、状态转换放在存储过程
CREATE OR REPLACE FUNCTION update_dev_pod_status(...) RETURNS BOOLEAN AS $$
BEGIN
    -- 状态转换验证
    -- 更新状态表
    -- 记录历史
    -- 管理 GPU 用量记录
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ❌ 不要让应用层直接操作多张表
```

### 3. 遵循命名规范

```sql
-- ✅ Trigger: trg_*
CREATE TRIGGER trg_update_dev_pod_status_timestamp

-- ✅ Function: verb_noun_*
CREATE OR REPLACE FUNCTION calculate_dev_pod_gpu_hours()
CREATE OR REPLACE FUNCTION update_dev_pod_status_timestamp()

-- ✅ 表名: dev_pod_*, cmdb_*
dev_pod_status, dev_pod_gpu_usage, dev_pod_history
cmdb_users, cmdb_teams, cmdb_projects
```

### 4. 支持多次启停

```sql
-- ✅ 使用 usage_cycle 区分多次启停
INSERT INTO dev_pod_gpu_usage (
    pod_id, pod_name, gpu_count, gpu_product,
    usage_cycle, usage_start_at
) SELECT
    p_pod_id, v_pod_name, gpu_count, gpu_product,
    COALESCE(MAX(usage_cycle) + 1, 1), CURRENT_TIMESTAMP
FROM dev_pod_gpu_usage
WHERE pod_id = p_pod_id;

-- 查询示例：
-- | usage_cycle | usage_start_at      | usage_end_at        | gpu_hours |
-- | 1           | 2026-01-29 10:00:00 | 2026-01-29 18:00:00 | 32.0      |
-- | 2           | 2026-01-30 09:00:00 | 2026-01-30 19:00:00 | 40.0      |
-- | 3           | 2026-01-31 10:00:00 | 2026-01-31 17:00:00 | 28.0      |
```

### 5. 索引优化

```sql
-- ✅ 为外键字段创建索引
CREATE INDEX idx_dev_pod_status_user_id ON dev_pod_status(user_id);
CREATE INDEX idx_dev_pod_status_team_id ON dev_pod_status(team_id);
CREATE INDEX idx_dev_pod_status_project_id ON dev_pod_status(project_id);

-- ✅ 为状态查询创建索引
CREATE INDEX idx_dev_pod_status_status ON dev_pod_status(status);
CREATE INDEX idx_dev_pod_gpu_usage_pod_id ON dev_pod_gpu_usage(pod_id);

-- ✅ 为时间范围查询创建索引
CREATE INDEX idx_dev_pod_gpu_usage_start_at ON dev_pod_gpu_usage(usage_start_at);
```

---

## 故障排查

### 问题 1: GPU hours 未自动计算

**症状**: `usage_end_at` 已更新，但 `gpu_hours` 为 NULL

**解决方案**:
```sql
-- 检查触发器是否存在
SELECT
    tgname AS trigger_name,
    tgrelid::regclass AS table_name,
    tgenabled AS enabled
FROM pg_trigger
WHERE tgname = 'trg_calculate_dev_pod_gpu_hours';

-- 手动测试触发器
UPDATE dev_pod_gpu_usage
SET usage_end_at = CURRENT_TIMESTAMP
WHERE pod_id = 'uuid-here' AND usage_end_at IS NULL;

-- 验证计算结果
SELECT * FROM dev_pod_gpu_usage WHERE pod_id = 'uuid-here';
```

### 问题 2: 状态转换失败

**症状**: 更新状态时报错 `无效状态转换`

**解决方案**:
```sql
-- 检查当前状态
SELECT pod_name, status FROM dev_pod_status WHERE pod_id = 'uuid-here';

-- 确认状态转换是否符合规则
-- PENDING → RUNNING ✅
-- RUNNING → STOPPED ✅
-- STOPPED → RUNNING ✅
-- RUNNING/STOPPED → RELEASED ✅
```

### 问题 3: GPU 使用记录未关闭

**症状**: 停止 Dev-Pod 后，`usage_end_at` 仍为 NULL

**解决方案**:
```sql
-- 检查是否有未关闭的记录
SELECT * FROM dev_pod_gpu_usage
WHERE pod_id = 'uuid-here' AND usage_end_at IS NULL;

-- 手动关闭记录
UPDATE dev_pod_gpu_usage
SET usage_end_at = CURRENT_TIMESTAMP
WHERE pod_id = 'uuid-here' AND usage_end_at IS NULL;
```

---

## 相关文档

- [完整设计文档 v2.1](../../docs/design/cmdb_design_v2.1.md) - 符合 event_db 现行策略的完整设计
- [Dev-Pod 服务集成指南](../../docs/dev_pod_eventdb_integration_guide.md) - 应用层代码集成
- [event_db 分析报告](../../docs/event_db_trigger_functions.md) - event_db 现状分析
