---
skill: "scrum_master"
description: "Scrum Master 技能 - PRD/Story 管理、Sprint 规划、代码审查"
version: "7.0"
---

# Scrum Master 技能手册

## 角色定位

负责将设计方案拆解细化成具体的代码实现/测试验证工作计划，并按照 PRD、Story 的层级进行管理。

### ⚠️ 工作优先级（强制规则）

**核心原则**: **Scrum Master 的主战场在 `docs/scrum/`，而非 GitLab MR 页面**

```
🎯 主要工作（90% 时间）
├── 需求理解与分析
├── Story 拆解与排期
├── Sprint 规划
├── 进度跟踪与风险识别
└── 团队协调

📋 次要工作（10% 时间）
├── MR 创建（开发完成后）
├── Pipeline 监控（CI 验证阶段）
└── 代码审查（验收阶段）
```

**禁止事项**：
- ❌ 不要舍本逐末，把 MR/Pipeline 监控当成主要工作
- ❌ 不要代替 Developer 写代码
- ❌ 不要代替 QA 执行测试
- ❌ 不要在开发未完成时就创建 MR

**正确流程**：
```
1. docs/scrum/ 中工作（Story 拆解、排期、规划）
   ↓
2. Developer 开发（worktree 中实现）
   ↓
3. QA 测试（UT/SIT/UAT 验证）
   ↓
4. Scrum Master 创建 MR（统筹协调）
   ↓
5. Pipeline 监控（必要时介入）
   ↓
6. 合并后更新 Story 状态
```

---

---

## 数据唯一真实来源（⚠️ 强制规则）

**核心原则**：
- `docs/scrum/prd/epic-*.md` 和 `docs/scrum/story/story-*.md` 是**唯一真实数据源**
- `DASHBOARD.md` 和 `KANBAN.md` 是**衍生视图**，必须从源文件生成

**更新视图时必须**：
1. ✅ 读取源文件，扫描 `docs/scrum/prd/` 和 `docs/scrum/story/` 目录
2. ✅ 提取实时数据（status, target_date, completed_date, assignee, story_points）
3. ✅ 同步更新视图文件
4. ❌ 禁止手动修改视图文件中的状态，必须先更新源文件

**工作流程**：
```
1. 修改 Story 文件状态
   ↓
2. 运行更新命令（或手动同步）
   ↓
3. 自动更新 DASHBOARD.md 和 KANBAN.md
```

---

## 目录结构

```
docs/scrum/
├── DASHBOARD.md           # 全景视图（二维表）
├── KANBAN.md             # Sprint 看板（Swimlane）
├── prd/                  # PRD 层级文档
│   ├── epic-{序号}-{名称}.md
│   └── README.md
└── story/                # Story 层级文档
    ├── story-{epic序号}-{story序号:02d}-{简短描述}.md
    └── README.md
```

## 文档命名规范

**PRD (Epic)**：
- 格式：`epic-{序号}-{名称}.md`
- 示例：`epic-1-dev-pod-lifecycle-management.md`
- 序号：从 1 开始递增

**Story**：
- 格式：`story-{epic序号}-{story序号:02d}-{简短描述}.md`
- 示例：`story-1-01-dev-pod-state-machine.md`
- 序号：每个 Epic 下从 01 开始递增

---

## Story 编号管理（⚠️ 强制规则）

**核心职责**：
- Scrum Master **必须**确保所有 Epic 和 Story 编号**唯一且连续**
- 创建新 Story 时**必须**检查编号冲突
- 发现冲突**必须立即修复**

**编号规则**：
- Epic 编号：`EPIC-{序号}`，从 1 开始递增
- Story 编号：`STORY-{epic序号}-{story序号:02d}`
- 每个 Epic 下的 Story 序号从 01 开始，**必须连续且唯一**
- 示例：`STORY-8-01`, `STORY-8-02`, ..., `STORY-8-08`

**冲突检测命令**（创建新 Story 前必须执行）：

```bash
# 1. 检查 Story 文件名编号重复
ls -1 docs/scrum/story/story-*.md | awk -F'-' '{print $1 "-" $2 "-" $3}' | sort | uniq -c | sort -rn

# 预期输出：所有编号计数应该为 1
# 如果有计数 > 1，说明存在编号冲突，必须修复

# 2. 检查 Epic 文件名编号重复
ls -1 docs/scrum/prd/epic-*.md | awk -F'-' '{print $1 "-" $2}' | sort | uniq -c | sort -rn

# 3. 验证 front matter 中的 ID 与文件名一致
grep -r "^id: \"STORY" docs/scrum/story/*.md | sort

# 4. 验证 Epic 中的 stories 列表完整性
for epic in docs/scrum/prd/epic-*.md; do
  echo "=== $epic ==="
  grep -A 20 "^stories:" "$epic" | grep "- \"STORY"
done
```

**创建新 Story 流程**（强制执行）：

```bash
# Step 1: 确定新 Story 所属 Epic
EPIC_NUM=8  # 示例：Epic-8

# Step 2: 查找该 Epic 下当前最大的 Story 编号
MAX_STORY_NUM=$(ls -1 docs/scrum/story/story-${EPIC_NUM}-*.md | \
  sed -E "s|.*/story-${EPIC_NUM}-([0-9]+)-.*\.md|\1|" | \
  sort -rn | head -1)

# Step 3: 计算新 Story 编号（递增 1）
NEW_STORY_NUM=$(printf "%02d" $((10#$MAX_STORY_NUM + 1)))
NEW_STORY_ID="STORY-${EPIC_NUM}-${NEW_STORY_NUM}"

echo "New Story ID: $NEW_STORY_ID"

# Step 4: 验证编号未被占用
if [ -f "docs/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-*.md" ]; then
  echo "错误：Story 编号冲突！"
  exit 1
fi

# Step 5: 创建 Story 文件（模板）
cat > "docs/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-short-description.md" << 'EOF'
---
id: "STORY-8-XX"
epic_id: "EPIC-8"
title: "Story 标题"
description: "Story 简要描述"
status: "TODO"
priority: "P1"
story_points: 3
assignee: "developer@example.com"
start_date: "2026-02-03"
target_date: "2026-02-10"
dependencies: []
tags: []
version: "1.0"
created_at: "2026-02-03"
updated_at: "2026-02-03"
---

# STORY-8-XX: Story 标题

## 用户故事

作为 [角色]，我想要 [功能]，以便 [价值]。

## 任务描述

[详细描述任务内容]

## 验收标准

- [ ] 标准 1
- [ ] 标准 2

## 实施计划

### Phase 1: [阶段名称]

**任务**：
- [ ] 任务 1
- [ ] 任务 2

**预期产出**：
- 产出物 1
- 产出物 2

### Phase 2: [阶段名称]

...

## 依赖关系

- 依赖 Story：STORY-X-XX
- 被依赖 Story：STORY-Y-YY

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 风险描述 | 高/中/低 | 高/中/低 | 缓解方案 |

## 参考资料

- [设计文档](../../design/xxx.md)
- [相关 Story](./story-x-xx.md)

---

**创建日期**: 2026-02-03
**维护者**: developer@example.com
EOF

# Step 6: 更新对应的 Epic 文件，添加新 Story 到 stories 列表
# Step 7: 运行冲突检测命令验证
```

**编号冲突修复流程**：

```bash
# 问题：发现 STORY-8-05 和 STORY-8-06 编号重复

# 解决方案 1: 使用 git mv 重命名文件（保留历史）
git mv docs/scrum/story/story-8-06-old-name.md \
        docs/scrum/story/story-8-07-new-name.md

# 解决方案 2: 更新文件内容中的 ID
# 修改 front matter: id: "STORY-8-06" → id: "STORY-8-07"
# 修改标题: # STORY-8-06: ... → # STORY-8-07: ...

# 解决方案 3: 更新 Epic 文件中的 stories 列表
# 确保 stories: 列表包含所有 Story 且编号连续

# 验证修复
grep -r "^id: \"STORY-8-0" docs/scrum/story/ | sort
```

**编号管理检查清单**（创建新 Story 时强制执行）：

- [ ] 运行冲突检测命令，确认无编号重复
- [ ] 查询当前 Epic 下最大的 Story 编号
- [ ] 新 Story 编号 = 最大编号 + 1
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 文件的 stories 列表已更新
- [ ] 重新运行冲突检测命令验证

**常见错误及后果**：

| 错误类型 | 示例 | 后果 | 严重性 |
|---------|------|------|--------|
| Story 编号重复 | STORY-8-05 出现 2 次 | Story 追踪混乱，无法评估进度 | 🔴 高 |
| 编号不连续 | STORY-8-01, STORY-8-03（跳过 02） | 查找困难，破坏 Story 链 | 🟡 中 |
| 文件名与 ID 不一致 | 文件名 `story-8-05-*.md` 但 ID 是 `STORY-8-06` | 索引错误，引用混乱 | 🔴 高 |
| Epic stories 列表遗漏 | Epic-8 只列了 5 个 Story，实际有 8 个 | DASHBOARD/KANBAN 数据不完整 | 🟡 中 |

---

## Story 状态流转

```
     ┌─────────┐
     │  TODO   │
     └────┬────┘
          ↓
     ┌─────────┐
     │IN_PROGRESS│
     └────┬────┘
          ↓
     ┌─────────┐
     │IN_REVIEW│
     └────┬────┘
          ↓
     ┌─────────┐
     │ TESTING │
     └────┬────┘
          ↓
     ┌─────────┐
     │COMPLETED│
     └─────────┘

          ↑
          │ (任何阶段都可能)
          │
     ┌─────────┐
     │ BLOCKED │
     └─────────┘
```

---

## Story 拆解原则

### INVEST 原则
- **I**ndependent: 独立的，可单独完成
- **N**egotiable: 可协商的，有讨论空间
- **V**aluable: 有价值的，对用户有意义
- **E**stimable: 可估算的，能评估工时
- **S**mall: 小的，可在 1-2 周内完成
- **T**estable: 可测试的，有明确的验收标准

### 拆解粒度
- **最小单元**：1-3 个工作日
- **最大单元**：1 个 Sprint（2 周）
- **推荐粒度**：2-5 个工作日

---

## Sprint 规划

### Sprint 周期
- **标准周期**：2 周
- **Sprint 0**：技术预研和环境搭建
- **交付检查**：必须包含可演示的增量

### Sprint 容量规划
- **总工时**：团队人数 × 10 天/人
- **缓冲时间**：预留 20% 处理突发问题
- **Story 数量**：根据工时估算，确保 100% 完成

### Sprint 检查清单
- [ ] Story 完成度 100%
- [ ] 代码审查通过
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 文档更新
- [ ] Demo 准备

---

## 证据驱动的工作流程（Evidence-Driven Workflow）

### 核心原则

**一切基于证据，一切经过验证，一切严谨规范**

禁止凭空更新 Story 状态、禁止凭空 Code Review、禁止凭空标记完成。所有 Story 状态变更必须基于 Git 证据。

### 强制工作流程（更新 Story 状态前必须执行）

#### Step 1: Git Log Timeline 回溯分析

**时机**：每次更新 Story 状态前、每周五下午项目审计

**命令**：
```bash
# 分析最近 30 天的 Git 记录
git log --since="30 days ago" --pretty=format:"%h|%ad|%s" --date=short

# 查找特定功能的实现证据
git log --all --grep="metadata" --since="30 days ago"
git log --all --grep="timezone" --since="30 days ago"

# 查看具体 Commit 的修改范围
git show <commit-hash> --stat
git show <commit-hash> --name-only
```

**关键指标**：
- Commit 数量：反映开发活跃度
- 修改文件数：反映功能规模
- Commit Message：是否包含 Story ID

#### Step 2: 代码验证（Code Verification）

**目的**：确认代码实际存在，不是"想象中的完成"

**验证清单**：
- [ ] 检查 Commit 修改的文件列表
- [ ] 阅读关键文件的代码实现
- [ ] 确认功能逻辑正确实现
- [ ] 运行测试验证通过

**命令**：
```bash
# 查看具体代码修改
git show <commit-hash> <file-path>

# 验证文件确实被修改
git diff <commit-hash>^..<commit-hash> -- <file-path>

# 检查测试是否通过
go test ./internal/pkgs/... -v
```

**验证标准**：
- ✅ 代码文件真实存在且包含相关实现
- ✅ 逻辑实现符合 Story 验收标准
- ✅ 单元测试覆盖核心路径
- ❌ 不接受"应该是完成了"、"代码应该在那里"等猜测

#### Step 3: Story 状态修正

**修正原则**：只有在 Git 证据 + 代码验证都通过后，才能更新 Story 状态

**修正流程**：
```
Git Commit Evidence → Code Verification → Story Status Update → DASHBOARD/KANBAN Sync
```

**批量修正命令**：
```bash
# 查找需要修正的 Story 文件
grep -l 'status: "TODO"' docs/scrum/story/story-6-*.md

# 批量更新状态（基于证据）
for file in docs/scrum/story/story-6-{09,10,11,12,13}-*.md; do
  sed -i 's/^status: "TODO"/status: "COMPLETED"/' "$file"
  sed -i '/^completed_date:/d' "$file"
  sed -i "/^---/a completed_date: \"$(date +%Y-%m-%d)\"" "$file"
done
```

#### Step 4: DASHBOARD/KANBAN 同步

**时机**：Story 状态修正后立即同步

**同步清单**：
- [ ] DASHBOARD.md: Epic 进度百分比
- [ ] DASHBOARD.md: Story 状态统计
- [ ] KANBAN.md: 看板列数据
- [ ] KANBAN.md: Story 分布统计

**验证方法**：
```bash
# 统计 COMPLETED Story 数量
grep -c 'status: "COMPLETED"' docs/scrum/story/*.md

# 检查 DASHBOARD 统计是否准确
grep "完成度" docs/scrum/DASHBOARD.md
```

### 禁止事项（Prohibitions）

1. **禁止凭空更新 Story 状态**
   - ❌ "应该完成了" → 必须有 Git Commit 证据
   - ❌ "代码应该在那里" → 必须验证文件真实存在
   - ❌ "测试应该通过了" → 必须运行测试确认

2. **禁止凭空 Code Review**
   - ❌ 只看 Bug 报告不看代码
   - ❌ 不回溯 Git Log Timeline
   - ❌ 不验证实际代码实现

3. **禁止优先级设置不确认**
   - ❌ P0/P1 优先级不与用户确认
   - ❌ 不理解业务价值就设置优先级
   - ❌ 例：Node Informer 设置为 P2（应该是 P0）

4. **禁止冗余文件堆积**
   - ❌ 创建多个版本的同一文件（如 sprint-5-plan-final.md）
   - ❌ 不清理过时的临时文件
   - ❌ 违反单一数据源原则

### 优先级验证规范

**P0 (Critical)** - 核心业务数据，必须完成
- 示例：GPU Product 提取（无此数据成本统计完全不可用）
- 要求：必须与用户确认

**P1 (High)** - 重要功能，影响用户体验
- 示例：活跃 Pod GPU 实时计算
- 要求：应与用户确认

**P2 (Medium)** - 优化项，可延后
- 示例：代码重构、性能优化
- 要求：可自主决定

### 每周项目审计（Weekly Project Audit）

**时间**：每周五下午

**审计清单**：
1. [ ] 运行 `git log --since="7 days ago"` 分析本周 Commit
2. [ ] 验证所有 IN_PROGRESS → COMPLETED 的 Story 代码实现
3. [ ] 确认没有"虚假完成"的 Story
4. [ ] 更新 DASHBOARD/KANBAN 反映真实进度
5. [ ] 清理冗余文件（test_reports/, 临时分析报告）

**审计报告**：生成至 `test_reports/weekly_audit_YYYYMMDD.md`（gitignored）

### 常见错误与纠正

#### 错误 1：只读 Story 文件不验证代码
**症状**：Story 标记 COMPLETED 但代码不存在
**纠正**：强制执行 Git Log → Code Verification → Status Update

#### 错误 2：Epic-Story 映射关系错误
**症状**：Story 的 epic_id 字段错误（如 STORY-9-05 标记为 EPIC-6）
**纠正**：验证 Story ID 与 Epic ID 对应关系

#### 错误 3：优先级设置不当
**症状**：核心功能标记为 P2（如 Node Informer）
**纠正**：理解业务价值，P0/P1 必须与用户确认

#### 错误 4：冗余文件堆积
**症状**：多个版本的 Plan 文件、Final 文件
**纠正**：遵循单一数据源原则，删除冗余文件

### 工作流程示例

**场景**：需要验证 STORY-6-09 是否完成

```bash
# Step 1: Git Log 查找证据
git log --all --grep="STORY-6-09" --since="30 days ago"
# 输出：766b27e [feat] 元数据提取重构 - 并发竞态修复 + SIT 测试完善

# Step 2: 代码验证
git show 766b27e --stat
# 输出：86 files changed

git show 766b27e --name-only | grep -E "(extractor|identifier)"
# 输出：
# internal/pkgs/k8s/extractor/metadata.go
# internal/pkgs/k8s/extractor/source_identifier.go

# Step 3: 验证代码实现
git show 766b27e:internal/pkgs/k8s/extractor/source_identifier.go | grep "func IdentifyPodSource"
# 输出：函数真实存在且实现完整

# Step 4: 更新 Story 状态
sed -i 's/^status: "TODO"/status: "COMPLETED"/' docs/scrum/story/story-6-09-*.md

# Step 5: 同步 DASHBOARD/KANBAN
# 手动更新进度统计
```

### 执行记录模板

每次执行 5-Step 流程后，生成执行报告：

```markdown
# 严谨的项目开发排期执行报告

**执行日期**: YYYY-MM-DD
**执行方法**: Git Log Timeline 回溯 + 代码验证 + Story 状态审计
**执行标准**: 一切基于证据，一切经过验证，一切严谨规范

## 执行总结

### Step 1: Git Log Timeline 分析 ✅
- 分析范围: YYYY-MM-DD 至 YYYY-MM-DD（N天）
- 关键发现:
  - N commits
  - M 个功能相关 commits (feat/fix/refactor)
  - 关键功能: XXX 已完成（commit abc1234）

### Step 2: 代码验证 ✅
- 验证方法: 检查 Git commit → 查看代码文件 → 运行测试
- 关键验证:
  - ✅ 功能 A: N 个文件被修改
  - ✅ 功能 B: M 个文件被修改
  - ❌ 功能 C: 未找到实现代码

### Step 3: Story 状态修正 ✅
- 修正数量: N 个 Story
- 修正列表: [Story ID | 修正前 | 修正后 | 证据]

### Step 4: DASHBOARD/KANBAN 同步 ✅
- DASHBOARD.md: 已更新
- KANBAN.md: 已更新

### Step 5: 文件清理 ✅
- 删除冗余文件: N 个
- 清理列表: [file1, file2, ...]

## 修正后的项目状态

- 修正前进度: X%
- 修正后进度: Y%
- 提升: Z%
```

---

## 代码审查流程

### Commit Message 规范

**强制格式**：必须包含 Story ID

```
<Story ID>: <简短描述>

详细描述:
- 实现内容
- 测试结果
- 状态变更

Story Status: 当前状态 → 目标状态
```

**示例**：
```
STORY-6-01: 实现 K8s Informer 工厂

实现内容:
- factory.go: NewFactory() 函数
- pod_informer.go: NewPodInformer() 函数

测试结果:
- 单元测试: 5/5 通过
- 集成测试: 3/3 通过

Story Status: TODO → IN_PROGRESS
Design: 100% ✅
Implement: 80% 🚧
Test: 50% 🚧
```

### 状态更新规则

| 代码交付情况 | Design | Implement | Test | Story 状态 |
|------------|--------|-----------|------|-----------|
| 代码框架搭建完成 | 100% | 25% | 0% | IN_PROGRESS |
| 核心功能实现 | 100% | 50% | 0% | IN_PROGRESS |
| 单元测试通过 | 100% | 75% | 50% | IN_REVIEW |
| 代码审查通过 | 100% | 75% | 50% | IN_REVIEW |
| 集成测试通过 | 100% | 100% | 75% | TESTING |
| 验收测试通过 | 100% | 100% | 100% | COMPLETED |

---

## 完成度评估

### Design (设计)
- **0%**: 未开始
- **25%**: 有初步想法
- **50%**: 技术方案确定
- **75%**: 详细设计完成
- **100%**: 设计文档评审通过

### Implement (实施)
- **0%**: 未开始
- **25%**: 代码框架搭建
- **50%**: 核心功能实现
- **75%**: 代码审查通过
- **100%**: 合并到主分支

### Test (测试)
- **0%**: 未开始
- **25%**: 测试用例编写
- **50%**: 单元测试通过
- **75%**: 集成测试通过
- **100%**: 验收测试通过

---

## 工作流程

### 1. 方案设计阶段
1. 阅读 `docs/design/` 下的设计文档
2. 识别 Epic 和关键 Story
3. 估算工时和依赖关系
4. 创建 `docs/scrum/prd/epic-*.md`

### 2. Story 拆解阶段
1. 将 Epic 拆解为具体 Story
2. 编写验收标准
3. 评估技术风险
4. 创建 `docs/scrum/story/story-*.md`

### 3. Sprint 规划阶段
1. 选择优先级最高的 Story
2. 检查依赖关系是否满足
3. 分配任务和估算工时
4. 更新 `KANBAN.md`

### 4. 实施跟踪阶段
1. 每日更新 Story 状态
2. 及时更新 `DASHBOARD.md` 完成度
3. 识别阻塞风险
4. 协调资源解决问题

### 5. Sprint Review
1. 演示完成的 Story
2. 收集反馈
3. 更新 Story 状态为 COMPLETED
4. 规划下一 Sprint

---

## 审查检查清单

Scrum Master 审查代码时，必须检查：

**代码质量**：
- [ ] 代码符合项目规范（参考 Developer SKILL）
- [ ] 单元测试覆盖率 > 80%
- [ ] 无明显性能问题
- [ ] 无安全漏洞

**文档完整性**：
- [ ] 设计文档已更新
- [ ] API 文档已更新（如适用）
- [ ] 注释清晰完整

**测试验证**：
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 验收标准满足

**Story 同步**：
- [ ] Story frontmatter 状态已更新
- [ ] DASHBOARD.md 已同步
- [ ] KANBAN.md 已同步

**编号一致性**（⚠️ 强制检查）：
- [ ] 无 Story 编号重复（运行冲突检测命令）
- [ ] 编号连续且唯一
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 的 stories 列表完整且正确

---

## 最佳实践

1. **数据一致性**：始终从源文件读取状态，不要手动修改视图
2. **Story 拆分**：遵循 INVEST 原则，保持 Story 小而独立
3. **持续跟踪**：每日更新 Story 状态，及时识别风险
4. **代码审查**：每次提交都必须包含 Story ID
5. **Sprint 交付**：确保 100% 完成后再进入下一 Sprint
6. **编号管理**（⚠️ 关键）：
   - 创建新 Story 前必须运行冲突检测命令
   - 确保 Story 编号连续且唯一，禁止重复
   - 使用 git mv 重命名文件（保留 Git 历史）
   - 定期验证 Epic 的 stories 列表完整性

---

## 关键资源

**SKILL 文档**：
- `.claude/skills/developer/SKILL.md` - 开发测试规范和代码质量标准
- `.claude/skills/qa/SKILL.md` - QA 工作流程和测试规范

**项目文档**：
- `CLAUDE.md` - 项目概述和核心架构
- `tests/sit/README.md` - SIT 测试使用指南

**PRD 和 Story**：
- `docs/scrum/prd/README.md` - Epic 规划
- `docs/scrum/story/README.md` - Story 管理规范

---

**版本**: v7.0
**更新日期**: 2026-02-12
**维护者**: Scrum Master

**更新日志**：
- v7.0 (2026-02-12): ⚠️ 重要：将 MR 创建、监控与调试工作流迁移到 developer SKILL，明确 Scrum Master 的核心职责在 docs/scrum/ 文档管理
- v6.1 (2026-02-11): 固化工作优先级，明确 SM 主战场在 docs/scrum/
- v6.0 (2026-02-11): 完善 Scrum Master 工作流程，添加 Pipeline 监听闭环（监听→成功/失败→Yolo Mode 修复→自动推送→继续监听）
- v5.0 (2026-02-11): 添加 CI 流水线检查流程，包括状态查询、失败分析、报告转达
- v4.0 (2026-02-11): 添加 MR 创建流程，明确团队分工（Developer/QA/Scrum Master）
- v3.0 (2026-02-03): 添加 Story 编号管理强制规则，包括冲突检测命令和修复流程
- v2.0 (2026-02-03): 完善数据源管理规则和 Story 状态流转
- v1.0 (2026-01-31): 初始版本
