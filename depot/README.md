# Depot - 文档仓库

生成的工程规范文档存放在此目录。

## 目录结构

```
depot/
└── <team>/                        # 团队名称（如 team-alpha）
    └── <project>/                 # 项目名称（如 sample-project）
        ├── <project>_<type>_vX.Y.Z.md   # 正式文档
        ├── drafts/                # 草稿（已加入 .gitignore）
        │   └── draft-*.json
        └── ...
```

## 文档命名

`{project-name}_{spec-type}_v{X.Y.Z}.md`

| spec-type | 说明 | 示例 |
|-----------|------|------|
| `project` | 新项目立项 | `sample-project_project_v1.0.0.md` |
| `feature` | 新功能开发 | `sample-project_feature-api_v1.0.0.md` |
| `enhance` | 功能优化 | `sample-project_enhance-ui_v1.0.0.md` |
| `fix` | Bug 修复 | `sample-project_fix-xxx_v1.0.0.md` |

## 示例

```
depot/
├── team-alpha/
│   └── sample-project/
│       └── sample-project_project_v1.0.0.md
└── team-beta/
    └── another-project/
        └── another-project_feature-dashboard_v1.0.0.md
```
