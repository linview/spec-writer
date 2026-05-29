# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## v1.2.0 (2026-05-29)

### Added

- `hld_backend.template.md` v1.0.0 — 后端架构设计模板，分片输出（10 个独立文档 + metadata.json + changelog.jsonl）
- `brd_prd.template.md` 声明到 `templates/README.md`

### Changed

- 重写 `CLAUDE.md`，从用户教程（530 行）精简为架构指引（~120 行）
- `README.md` 标题从 `Doc Template` 改为 `Spec Writer`
- `README.md` 移除所有不存在的 `scrum_master` skill 引用

## v1.1.1 (2026-04-18)

### Added

- 初始项目结构和配置（`.claude/`, `templates/`, `depot/`）
- `depot/` 目录占位结构
- spec-writer skill 初始版本

## v1.1.0 (2026-02-27)

### Changed

- 明确文档边界为"方案论证专用"，不包含项目管理内容

### Added

- 技术实施要点章节（替代实施计划）
- 技术债务与已知问题章节（替代风险与待办）

### Removed

- 项目管理内容（里程碑、任务排期、人力分配）

### Fixed

- 使用方式改为通过 `/spec-writer` 对话（替代错误的 `/spec` 命令）
