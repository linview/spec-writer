---
spec_version: "1.0.0"
spec_template: "all_in_one"
spec_template_version: "1.0.0"
project_name: "CI Health Tracker"
spec_type: "project"
spec_scope: "ci-monitor"
last_edited: "2026-02-27T10:30:00Z"
status: "Draft"
edited_by: "Claude (spec-writer)"
---

# CI Health Tracker - 工程规范文档示例

## 📋 第一部分：业务需求描述（BRD）

### 1. 需求背景
- **业务痛点**：
  - CI/CD 流水线失败后，DevOps 团队需要花费大量时间手动定位失败原因
  - GitLab UI 不支持按时间范围、失败类型、stage 等维度分析流水线数据
  - 缺乏历史趋势分析，难以识别系统性问题
  - 团队每周平均花费 10+ 小时排查 CI 失败

- **为什么要做**：
  - 提升故障定位效率
  - 实现数据驱动的 CI 优化决策
  - 降低 CI 维护成本

---

### 2. 客户是谁
- **目标客户**：内部 DevOps 团队（约 20 人）
- **是否付费**：内部工具，无直接付费需求，但间接节省人力成本
- **投入成本**：
  - 时间：4 周（1 个 Sprint）
  - 金钱：$0（使用现有基础设施）
  - 人力：1 名后端开发 + 1 名前端开发

---

### 3. 预期收益
- **收益类型**：
  - 效率提升：CI 故障定位时间减少 70%（从 30 分钟降至 9 分钟）
  - 成本节约：每周节省约 7 小时 × 20 人 = 140 小时/周
  - 质量改进：通过数据分析识别高频失败 stage，针对性优化

- **收益规模**：
  - 年节省工时：140 小时/周 × 52 周 = 7,280 小时
  - 等效 FTE（全职人力）：约 3.65 人年

---

### 4. 是否值得做
- **ROI 分析**：
  - 投入成本：2 人 × 4 周 = 8 人周
  - 预期收益：7,280 小时/年 = 182 人周/年
  - ROI = (182 - 8) / 8 = **21.75**（投产比 1:22）

- **结论**：✅ 强烈推荐，ROI 极高

---
**[上下文切换点: BRD → PRD]**
---

## 📱 第二部分：产品需求描述（PRD）

### 1. 功能范围/边界

#### 🎯 在范围内（In Scope）
- **功能 1**：从 GitLab 同步流水线数据（pipelines + jobs）
- **功能 2**：支持按时间范围、项目、分支筛选数据
- **功能 3**：生成 CI 健康度报告（Markdown 格式）
- **功能 4**：失败原因统计与趋势分析
- **功能 5**：RESTful API 接口

#### 🚫 不在范围内（Out of Scope）
- **暂不做的功能**：
  - 实时通知（Webhook/邮件/Slack）
  - 自动重试失败流水线
  - 可视化 Dashboard（初期仅提供 Markdown 报告）
- **后续版本考虑**：v2.0 支持 Web UI 和实时告警

---

### 2. 用户场景/用例

#### 用户画像
- **目标用户**：DevOps 工程师、QA 团队
- **用户特征**：
  - 熟悉 GitLab CI/CD 流程
  - 经常需要排查流水线失败原因
  - 有基本的数据分析需求

#### 典型场景

| 场景编号 | 场景描述 | 用户操作 | 预期结果 |
|---------|---------|---------|---------|
| 场景 1 | 日报排查 | 运行 CLI 工具生成昨日 CI 报告 | 输出包含失败统计、高频失败 stage 的 Markdown 报告 |
| 场景 2 | 周报分析 | 生成上周 CI 健康度趋势报告 | 输出包含失败率趋势、TOP 5 失败原因的汇总报告 |
| 场景 3 | 故障复盘 | 查询特定时间范围的流水线数据 | 按时间范围、项目、分支过滤，导出详细数据 |

---

### 3. 功能需求清单

| 功能编号 | 功能名称 | 优先级 | 验收标准 |
|---------|---------|-------|---------|
| F-001 | GitLab API 集成 | P0 | 支持同步 pipelines 和 jobs 数据，支持增量同步 |
| F-002 | 数据存储与查询 | P0 | 支持按时间、项目、分支过滤，查询响应 < 1s |
| F-003 | CLI 报告生成 | P0 | 支持生成 Markdown 格式的 CI 健康报告 |
| F-004 | 失败原因分析 | P1 | 自动统计失败 stage、失败原因分布 |
| F-005 | RESTful API | P1 | 提供 HTTP API 供第三方系统集成 |
| F-006 | 数据缓存优化 | P2 | 支持 Redis 缓存，减少 GitLab API 调用 |

---

### 4. 非功能需求

#### 性能要求
- **查询响应时间**：< 1 秒（1000 条记录以内）
- **同步性能**：10,000 条 pipelines 同步时间 < 5 分钟
- **并发用户数**：支持 10+ 并发 API 请求

#### 安全要求
- **认证方式**：API Token（Bearer Token）
- **权限控制**：
  - 只读权限（默认）：仅查询数据
  - 管理员权限：可触发同步、清空缓存
- **数据加密**：传输层使用 HTTPS

#### 可用性要求
- **可用性目标**：99.5%（月度）
- **容错机制**：GitLab API 调用失败自动重试 3 次

#### 兼容性要求
- **支持的 GitLab 版本**：GitLab 14.x+
- **浏览器支持**：Chrome 90+, Firefox 88+, Safari 14+
- **向后兼容性**：API v1.0 保持稳定，不破坏性变更

---

### 5. UI/UX 需求

#### 页面流转图

**典型用户流程**：

```
登录 → Dashboard → 选择项目 → 查看流水线列表 → 点击详情 → 查看失败原因
```

**设计稿链接**：
- [Figma 设计稿](https://figma.com/example-ci-health-tracker)
- [飞书流程图](https://feishu.cn/example-flow)

---

#### 关键页面元素

| 页面名称 | 页面用途 | 关键元素 | 交互说明 |
|---------|---------|---------|---------|
| **登录页** | 用户身份认证 | GitLab OAuth 登录按钮 | 点击跳转 GitLab 授权 |
| **Dashboard** | 概览 CI 健康度 | 时间选择器、项目筛选器、统计卡片 | 选择时间范围后自动刷新数据 |
| **流水线列表页** | 查看所有流水线 | 搜索框、筛选器、数据表格 | 支持按状态、分支筛选 |
| **流水线详情页** | 查看单个流水线详情 | Stage 进度条、Job 列表、失败原因标签 | 点击 Job 可查看日志 |

---

#### 设计规范

- **颜色方案**：
  - 主色：`#1890ff`（Ant Design 蓝）
  - 成功：`#52c41a`（绿色）
  - 失败：`#ff4d4f`（红色）
  - 警告：`#faad14`（橙色）

- **字体规范**：
  - 中文：思源黑体（Noto Sans SC）
  - 英文/数字：Inter
  - 代码：JetBrains Mono

- **组件库**：Ant Design 5.x

---

#### 设计稿链接

- **Figma**：[CI Health Tracker 设计稿](https://figma.com/file/ci-health-tracker)
- **原型图**：[交互原型](https://figma.com/proto/ci-health-tracker)
- **设计 Token**：[Design Tokens](https://figma.com/tokens/ci-health-tracker)

---
**[上下文切换点: PRD → Design Spec]**
---

## 🔧 第三部分：技术方案设计（Design Spec）

### 架构分层说明

> 本项目为**平台开发**类型，技术方案分为三个层级：
> - **前端（应用层/接入层）**：CLI 工具 + HTTP API
> - **后端（服务层/调度层）**：数据同步服务 + 业务逻辑
> - **数据库/中间件（服务层/中间层）**：PostgreSQL + Redis

---
**[上下文切换点: Design Spec → 前端设计]**
---

### 1. 前端设计（应用层/接入层）

#### 技术栈
- **CLI 工具**：Python 3.10 + Click（命令行框架）
- **HTTP 客户端**：Python `requests` 库
- **输出格式**：Markdown（使用 `markdown2` 生成）

#### 核心功能实现

| 功能模块 | 技术方案 | 实现要点 |
|---------|---------|---------|
| CLI 参数解析 | Click 框架 | 支持 `--time-after`, `--project-id`, `--output` 等选项 |
| API 调用 | requests + Session | 使用连接池优化，支持 Bearer Token 认证 |
| 报告生成 | 模板引擎 | 使用 Jinja2 模板生成 Markdown 报告 |

#### 接口对接
- **API 接口规范**：RESTful API
- **认证方式**：Bearer Token（HTTP Header: `Authorization: Bearer <token>`）
- **数据格式**：JSON（响应）/ JSON（请求）
- **错误处理**：统一错误码（200 成功，4xx 客户端错误，5xx 服务端错误）

**实现示例**：
```python
# CLI 调用 API 生成报告
@click.command()
@click.option('--tracker-url', required=True, help='CI Health Tracker API URL')
@click.option('--time-after', required=True, help='查询起始时间')
@click.option('--project-id', required=True, help='GitLab 项目 ID')
def report(tracker_url, time_after, project_id):
    api_client = APIClient(tracker_url)
    data = api_client.get_pipelines(project_id, time_after)
    report = MarkdownReport(data)
    report.save('output.md')
```

---

#### UI/UX 设计实现

##### 页面结构设计

| 页面名称 | 路由路径 | 组件结构 | 状态管理 |
|---------|---------|---------|---------|
| 登录页 | `/login` | `LoginPage > OAuthButton` | - |
| Dashboard | `/` | `MainLayout > Dashboard > StatCard` | Redux (pipelinesStats) |
| 流水线列表 | `/pipelines` | `MainLayout > PipelineList > FilterBar + DataTable` | Redux (pipelinesList) |
| 流水线详情 | `/pipelines/:id` | `MainLayout > PipelineDetail > StageProgress + JobList` | Redux (pipelineDetail) |

---

##### 组件设计

- **布局组件**：
  - `MainLayout`：主布局（Header + Sidebar + Content）
  - `LoginPage`：登录页面布局

- **业务组件**：
  - `Dashboard`：数据看板（统计卡片、趋势图）
  - `PipelineList`：流水线列表（筛选器、数据表格）
  - `PipelineDetail`：流水线详情（Stage 进度条、Job 列表）
  - `JobLogViewer`：日志查看器（语法高亮、搜索）

- **通用组件**：
  - `StatCard`：统计卡片
  - `FilterBar`：筛选栏
  - `DataTable`：数据表格

**组件树示例**：
```
App
├── LoginPage
└── MainLayout
    ├── Header (顶部导航)
    ├── Sidebar (侧边菜单)
    └── Content
        ├── Dashboard
        │   ├── StatCard × 4
        │   └── TrendChart (ECharts)
        ├── PipelineList
        │   ├── FilterBar
        │   └── DataTable (Ant Design Table)
        └── PipelineDetail
            ├── StageProgress (进度条组件)
            └── JobList
                └── JobItem
                    ├── JobStatusBadge
                    └── ExpandableLog
```

---

##### 交互实现

- **路由管理**：React Router 6.x
- **状态管理**：Redux Toolkit + RTK Query
- **表单处理**：Ant Design Form
- **数据可视化**：ECharts 5.x

**交互场景实现**：
| 交互场景 | 技术方案 | 关键代码/库 |
|---------|---------|-----------|
| 页面切换 | React Router | `<Navigate to="/pipelines" />` |
| 数据加载 | RTK Query | `useGetPipelinesQuery()` |
| 表单筛选 | Ant Design Form | `Form.useForm()` + `onFinish` |
| 日志展开 | Ant Design Collapse | `<Collapse expandIconPosition="end" />` |
| 数据导出 | `file-saver` | `saveAs(new Blob([data]), 'pipelines.csv')` |

---

##### 响应式设计

- **断点设置**：
  - Mobile：< 768px
  - Tablet：768px - 1024px
  - Desktop：>= 1024px

- **适配方案**：
  - 使用 Ant Design Grid 系统（Row + Col）
  - 侧边栏在移动端自动收起为抽屉
  - 表格在小屏幕上支持横向滚动

- **移动端优化**：
  - 支持触摸滑动切换 Tab
  - 关键操作按钮加大点击区域（44px × 44px）

---

##### 设计系统集成

- **设计 Token**：
  - 使用 CSS Variables 定义颜色、间距、字体
  - 示例：`--primary-color: #1890ff; --spacing-unit: 8px;`

- **主题切换**：
  - 使用 Ant Design ConfigProvider
  - 支持亮色/暗色主题切换（后续版本）

- **设计稿对接**：
  - 使用 Figma API 导出图标资源
  - 设计 Token 通过 Style Dictionary 统一管理

---
**[上下文切换点: 前端设计 → 后端设计]**
---

### 2. 后端设计（服务层/调度层）

#### 技术栈
- **语言/框架**：Python 3.10 + FastAPI
- **异步框架**：asyncio + httpx（异步 HTTP 客户端）
- **任务调度**：APScheduler（定时同步）

#### 核心服务设计

| 服务名称 | 职责 | 关键接口 |
|---------|-----|---------|
| **Pipeline Service** | 流水线数据同步与查询 | `sync_pipelines()`, `get_pipelines()` |
| **Report Service** | 报告生成逻辑 | `generate_health_report()` |
| **API Server** | HTTP API 路由 | `GET /pipelines`, `POST /sync` |

#### 业务逻辑实现

- **功能需求 F-001（GitLab API 集成）**：
  - 使用 GitLab REST API（`/projects/:id/pipelines` 和 `/pipelines/:id/jobs`）
  - 支持增量同步：基于 `updated_at` 字段判断是否需要更新
  - 异步并发拉取：使用 `asyncio.gather()` 并发请求多个 pipelines

- **功能需求 F-002（数据存储与查询）**：
  - PostgreSQL 存储流水线和作业数据
  - 支持复合索引：`(project_id, updated_at, status)`
  - 查询优化：使用 SQLAlchemy ORM，查询结果缓存（TTL 5 分钟）

- **功能需求 F-003（CLI 报告生成）**：
  - 报告 Service 计算失败率、高频失败 stage
  - 使用 Jinja2 模板渲染 Markdown
  - 支持自定义报告范围（日报/周报/月报）

#### 性能优化方案
- **缓存策略**：
  - Redis 缓存查询结果（key: `pipelines:{project_id}:{time_range}`, TTL: 300s）
  - 本地内存缓存 GitLab 项目配置（避免频繁查询 GitLab API）
- **异步处理**：
  - 使用 `asyncio` 并发拉取 GitLab 数据
  - 同步任务放入后台队列（Celery + Redis）
- **负载均衡**：
  - 使用 Nginx 反向代理
  - 支持 Gunicorn 多 worker 部署

**架构图**：
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  CLI Tool   │─────▶│  FastAPI     │─────▶│ PostgreSQL  │
└─────────────┘      │  API Server  │      └─────────────┘
                     └──────────────┘             ▲
                           │                      │
                           ▼                      │
                     ┌──────────────┐             │
                     │   Redis      │─────────────┘
                     │   Cache      │
                     └──────────────┘
                           ▲
                           │
                     ┌──────────────┐
                     │  GitLab API  │
                     └──────────────┘
```

---
**[上下文切换点: 后端设计 → 数据库设计]**
---

### 3. 数据库/中间件设计（服务层/中间层）

#### 数据存储

| 数据类型 | 存储方案 | 选型理由 |
|---------|---------|---------|
| **业务数据** | PostgreSQL 15 | 支持 JSON 字段、ACID 事务、复杂查询 |
| **缓存数据** | Redis 7.0 | 高性能 KV 存储、支持 TTL |
| **日志数据** | 文本文件（初期） | 简单可靠，后续可迁移到 ELK |

#### 数据模型设计

**核心表：`pipelines`**
```sql
CREATE TABLE pipelines (
    id BIGINT PRIMARY KEY,
    project_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,  -- success/failed/running
    ref VARCHAR(255),              -- 分支名
    sha VARCHAR(40),               -- commit hash
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    duration INTEGER,              -- 执行时长（秒）
    INDEX idx_project_updated (project_id, updated_at),
    INDEX idx_status (status)
);
```

**核心表：`jobs`**
```sql
CREATE TABLE jobs (
    id BIGINT PRIMARY KEY,
    pipeline_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,    -- stage/job name
    status VARCHAR(20) NOT NULL,
    stage VARCHAR(100),
    failure_reason TEXT,           -- 失败原因
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (pipeline_id) REFERENCES pipelines(id),
    INDEX idx_pipeline (pipeline_id),
    INDEX idx_stage_status (stage, status)
);
```

**关联关系**：
- 一个 Pipeline 包含多个 Jobs（一对多）
- Pipeline 通过 `project_id` 关联 GitLab 项目

#### 中间件使用
- **Redis**：
  - 用途 1：缓存查询结果（`pipelines:{project_id}:{time_hash}`）
  - 用途 2：分布式锁（防止重复同步任务）
  - 用途 3：Celery 任务队列 backend

#### 数据安全
- **数据备份策略**：
  - PostgreSQL：每日凌晨 2 点全量备份（`pg_dump`），保留 7 天
  - Redis：开启 AOF 持久化，每秒 fsync
- **数据加密方式**：
  - 传输层：TLS 1.3
  - 存储层：PostgreSQL 透明数据加密（TDE）
- **数据一致性保证**：
  - Pipeline 和 Job 使用外键约束
  - 同步任务使用数据库事务（要么全部成功，要么全部回滚）

---
**[上下文切换点: 数据库设计 → 实施计划]**
---

### 4. 实施计划

#### 阶段划分

| 阶段 | 任务 | 预计工期 | 依赖 |
|-----|------|---------|------|
| **阶段 1：基础框架** | 搭建 FastAPI 项目、数据库 schema 设计、GitLab API 集成 | 1 周 | 无 |
| **阶段 2：核心功能** | 实现数据同步、查询 API、CLI 工具 | 1.5 周 | 阶段 1 |
| **阶段 3：报告生成** | 实现报告统计逻辑、Markdown 模板、Redis 缓存 | 0.5 周 | 阶段 2 |

#### 里程碑
- **M1**（第 1 周末）：基础框架完成，可以从 GitLab 拉取数据并存入 DB
- **M2**（第 2.5 周末）：API 和 CLI 完成，可以查询数据并生成简单报告
- **M3**（第 3 周末）：完整功能上线，包含失败分析和缓存优化

---
**[上下文切换点: 实施计划 → 风险评估]**
---

### 5. 风险评估

| 风险类型 | 风险描述 | 影响等级 | 缓解方案 |
|---------|---------|---------|---------|
| **技术风险** | GitLab API 限流（429 错误） | 中 | 实现指数退避重试，增加请求间隔 |
| **进度风险** | 数据模型设计变更导致返工 | 低 | 前期充分调研 GitLab API 字段，预留扩展性 |
| **资源风险** | 开发人力不足（只有 1 人） | 低 | 与其他项目协调人力，或延长 1 周工期 |

---
**[上下文切换点: 风险评估 → 相关文档]**
---

## 🔗 相关文档

- **父文档**：无（项目级文档）
- **子特性**：
  - [ci-health-tracker_feature-dashboard_v1.0.0.md](./ci-health-tracker_feature-dashboard_v1.0.0.md)
  - [ci-health-tracker_feature-alert_v1.0.0.md](./ci-health-tracker_feature-alert_v1.0.0.md)
- **依赖文档**：
  - [ci-monitor_domain_v1.0.0.md](../../ci-monitor-platform/ci-monitor_domain_v1.0.0.md)
- **参考资料**：
  - [GitLab Pipelines API](https://docs.gitlab.com/ee/api/pipelines.html)
  - [FastAPI 文档](https://fastapi.tiangolo.com/)

---
**[上下文切换点: 相关文档 → 风险与待办]**
---

## ⚠️ 风险与待办

### 风险（Risks）
- [ ] **技术风险**：GitLab API 限流（429 错误）
  - 影响：中
  - 缓解方案：实现指数退避重试，增加请求间隔

- [ ] **进度风险**：开发人力不足（只有 1 人）
  - 影响：低
  - 缓解方案：与其他项目协调人力，或延长 1 周工期

### 待办（TODOs）
- [ ] **TODO**：确定实时通知方案（WebSocket vs 轮询）
  - 优先级：中
  - 计划版本：v2.0

- [ ] **TODO**：补充数据备份详细方案
  - 优先级：高
  - 负责人：DevOps 团队

---
**[上下文切换点: 风险与待办 → 附录]**
---

## 📝 附录

### 术语表

| 术语 | 定义 |
|------|------|
| **Pipeline** | GitLab CI/CD 流水线，包含多个 stage 和 job |
| **Job** | 流水线中的单个任务，如 `test`、`build`、`deploy` |
| **Stage** | 流水线的阶段，如 `build` → `test` → `deploy` |
| **Branch/Ref** | Git 分支名，如 `main`、`develop` |
| **ROI** | Return on Investment，投资回报率 |

### 参考资料
- [GitLab Pipelines API 文档](https://docs.gitlab.com/ee/api/pipelines.html)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [PostgreSQL 15 性能优化指南](https://www.postgresql.org/docs/15/performance-tips.html)
