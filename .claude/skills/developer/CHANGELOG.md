# Developer SKILL 更新日志

## v1.3 (2026-02-02) - Git Workflow 脚本通用化

### 🎯 核心改进

**问题**：v1.2 版本的 `git-workflow.skill.sh` 脚本使用硬编码的绝对路径，不适用于其他项目。

**解决方案**：完全重写配置部分，使用自动检测机制。

### ✨ 新特性

#### 1. 自动检测机制

```bash
# 自动检测 Git 仓库根目录
PROJ_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

# 自动检测项目名称
PROJECT_NAME=$(basename "$PROJ_ROOT")

# Worktree 根目录（与主仓库同级）
WORKTREE_ROOT=${WORKTREE_ROOT_OVERRIDE:-$(dirname "$PROJ_ROOT")/${PROJECT_NAME}-worktrees}
```

#### 2. 环境变量支持

- `WORKTREE_ROOT_OVERRIDE` - 覆盖 worktree 根目录路径
- `GIT_WORKFLOW_DEBUG=1` - 启用调试输出

#### 3. master/main 分支自动切换

```bash
git checkout master 2>/dev/null || git checkout main
git pull origin master 2>/dev/null || git pull origin main
```

#### 4. 新增辅助函数

```bash
cd_to_main_repo() {
  check_in_main_repo
  cd "$PROJ_ROOT"
}
```

### 📋 改进对比

| 特性 | v1.2 (旧版本) | v1.3 (新版本) |
|------|--------------|--------------|
| 项目检测 | ❌ 硬编码 `resource-meter` | ✅ 自动检测项目名称 |
| 路径检测 | ❌ 硬编码绝对路径 | ✅ 自动检测 Git 仓库根目录 |
| 可移植性 | ❌ 仅适用于 resource-meter | ✅ 适用于任何 Git 项目 |
| 分支支持 | ⚠️  仅支持 master | ✅ 支持 master/main |
| 调试功能 | ❌ 无 | ✅ 支持 `GIT_WORKFLOW_DEBUG=1` |
| 路径覆盖 | ❌ 无 | ✅ 支持 `WORKTREE_ROOT_OVERRIDE` |

### 🔄 迁移指南

如果您已经安装了 v1.2 版本，只需：

1. **更新脚本**（已完成）：
   ```bash
   # 脚本已自动更新，无需手动操作
   ```

2. **重新加载配置**：
   ```bash
   source ~/.bashrc  # 或 source ~/.zshrc
   ```

3. **验证安装**：
   ```bash
   cd /path/to/your-git-project
   git-workflow.help
   ```

### 📖 使用示例

#### 示例 1：在 resource-meter 项目中使用

```bash
cd ~/Proj/llv/resource-meter
git-workflow.feature.start story-06-01 "pod handler"
# 输出：✅ Worktree 创建成功！
#      项目: resource-meter
#      Worktree 路径: /home/mini/Proj/llv/resource-meter-worktrees/story-06-01-pod-handler
```

#### 示例 2：在新项目 my-awesome-project 中使用

```bash
cd ~/Proj/my-awesome-project
git-workflow.feature.start story-01 "initial feature"
# 输出：✅ Worktree 创建成功！
#      项目: my-awesome-project
#      Worktree 路径: /home/mini/Proj/my-awesome-project-worktrees/story-01-initial-feature
```

#### 示例 3：自定义 worktree 根目录

```bash
cd ~/Proj/my-project
export WORKTREE_ROOT_OVERRIDE=/tmp/my-project-worktrees
git-workflow.feature.start story-01 "feature"
# Worktree 会创建在：/tmp/my-project-worktrees/story-01-feature/
```

#### 示例 4：启用调试模式

```bash
export GIT_WORKFLOW_DEBUG=1
git-workflow.feature.start story-01 "feature"
# 输出：
# 🔧 Debug Info:
#    PROJ_ROOT: /home/mini/Proj/my-project
#    PROJECT_NAME: my-project
#    WORKTREE_ROOT: /home/mini/Proj/my-project-worktrees
```

### 🧪 测试验证

```bash
# 测试 1：基本功能
cd /home/mini/Proj/llv/resource-meter
source .claude/skills/developer/git-workflow.skill.sh
git-workflow.worktree.list
# ✅ 通过：正确列出 worktree

# 测试 2：调试模式
GIT_WORKFLOW_DEBUG=1 git-workflow.worktree.list
# ✅ 通过：正确显示调试信息

# 测试 3：帮助信息
git-workflow.help
# ✅ 通过：显示完整的帮助文档
```

### 📚 相关文档

- **Developer SKILL**：`.claude/skills/developer/SKILL.md`
- **Git Workflow 脚本**：`.claude/skills/developer/git-workflow.skill.sh`
- **项目工作流指南**：`docs/guides/git-workflow.md`

---

## v1.2 (2026-02-02) - Git Worktree 工作流

### 新增内容

- 新增 "🌳 Git Worktree 工作流" 章节
- 分支命名规范：`feat/<story_id>-<summary>`
- Worktree 目录结构说明
- 标准开发流程
- Git Worktree 命令速查
- 最佳实践和常见问题排查

---

## v1.1 (2026-02-02) - Git 推送规则

### 新增内容

- Master 分支保护规则
- GitLab MR 流程
- YOLO 模式例外条件
- Commit Message 规范

---

**维护者**: Development Team
**最后更新**: 2026-02-02
