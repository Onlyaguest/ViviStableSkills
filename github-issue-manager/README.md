# GitHub Issue Manager

自动化 GitHub Issue 创建和管理工具。

## 快速开始

### 1. 设置 GitHub Token

```bash
# 方法 A：环境变量
export GITHUB_TOKEN="ghp_your_token_here"

# 方法 B：使用 gh CLI
gh auth login
```

### 2. 创建 Issue

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "功能标题" \
  --type feature \
  --priority high
```

## 功能特性

- ✅ 结构化 Issue 模板
- ✅ 自动标签管理
- ✅ 命令触发（/bug, /feature）
- ✅ GitHub API 集成

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 安全提示

⚠️ **永远不要把 GitHub Token 提交到 Git！**

- 使用环境变量
- 添加到 .gitignore
- 定期轮换 token
