---
name: github-issue-manager
description: GitHub Issue 管理技能 - 自动化创建、追踪和管理 GitHub Issues。支持 /bug 和 /feature 触发，结构化 issue 模板，自动标签管理。
---

# GitHub Issue Manager

自动化 GitHub Issue 创建和管理的完整工作流。

## 功能特性

- ✅ 结构化 Issue 模板（Feature / Bug / Enhancement）
- ✅ 自动标签管理（feature, bug, priority-*, phase-*）
- ✅ 命令触发（/bug, /feature）
- ✅ 多轮对话起草
- ✅ GitHub API 集成
- ✅ 进度追踪（可选）

## 前置条件

### 1. 获取 GitHub Personal Access Token

访问：https://github.com/settings/tokens

**所需权限：**
- `repo` - Full control of private repositories（包含 issues 读写）

或更精细的权限：
- `public_repo` - Access public repositories
- `repo:status` - Access commit status

**生成后立即保存 token！** 格式：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. 安全存储 Token

**方法 A：环境变量（推荐）**
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export GITHUB_TOKEN="ghp_your_token_here"
```

**方法 B：secrets.edn（Clojure 项目）**
```clojure
{:github {:token "ghp_your_token_here"}}
```

**方法 C：gh CLI**
```bash
gh auth login
# gh CLI 会自动管理 token
```

## 使用方法

### 快速开始

**1. 创建 Issue（使用脚本）**
```bash
cd ~/ViviStableSkills/github-issue-manager
./create-issue.sh \
  --repo "owner/repo" \
  --title "支持新功能" \
  --type feature \
  --priority high \
  --phase 1
```

**2. 创建 Issue（使用 API）**
```bash
# 使用模板文件
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/owner/repo/issues \
  -d @templates/feature.json
```

### Issue 模板

#### Feature Issue
```json
{
  "title": "功能标题",
  "body": "## 功能描述\n...\n\n## 使用场景\n...\n\n## 验收标准\n- [ ] 标准1\n\n## 技术考虑\n...",
  "labels": ["feature", "priority-high", "phase-1"]
}
```

#### Bug Issue
```json
{
  "title": "Bug 标题",
  "body": "## 问题描述\n...\n\n## 预期行为\n...\n\n## 实际行为\n...\n\n## 复现步骤\n1. ...\n\n## 影响范围\n...",
  "labels": ["bug", "priority-high"]
}
```

### 工作流集成

**触发命令：**
- `/feature [描述]` - 提出新功能
- `/bug [描述]` - 报告 bug

**流程：**
```
用户：/feature 支持多设备数据采集
  ↓
AI：判断类型 + 起草 Issue（可能多轮讨论）
  ↓
用户：快速 review
  ↓
AI：提交到 GitHub
  ↓
开发团队：认领和执行
```

## Label 规范

### 类型标签（必选一个）
- `feature` - 新功能需求
- `bug` - 功能不正常
- `enhancement` - 现有功能改进
- `documentation` - 文档相关

### 优先级标签
- `priority-high` - 阻塞使用或核心功能
- `priority-medium` - 重要但不紧急
- `priority-low` - 优化类

### 阶段标签
- `phase-1` - 当前阶段
- `phase-2` - 下一阶段
- `phase-3` - 未来规划

## 进度追踪（可选）

### 方法 1：手动查询
```bash
# 查看所有 open issues
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues?state=open

# 查看特定 issue
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3
```

### 方法 2：定时任务（Cron）
```bash
# 每天下午 2 点检查进度
0 14 * * * /path/to/check-issues.sh
```

### 方法 3：MATA 集成（如果使用 MATA 系统）
```bash
# 询问开发团队进度
bb ask ems-crew Scribe "Issue #3 的进度如何？"
```

## 安全最佳实践

### 1. Token 管理
- ✅ 使用环境变量或 secrets 文件
- ✅ 添加到 .gitignore
- ✅ 定期轮换（建议 90 天）
- ❌ 不要硬编码在脚本中
- ❌ 不要提交到 Git

### 2. 权限最小化
- 只给需要的权限
- 不同用途用不同 token
- 定期检查 token 使用情况

### 3. 检查泄露
```bash
# 检查 Git 历史中是否有 token
git log -p | grep "ghp_"

# 如果发现泄露，立即在 GitHub 上 revoke
```

## 故障排查

### Issue 创建失败

**问题：JSON parsing error**
```bash
# 解决方案：使用文件而不是内联 JSON
echo '{"title":"标题","body":"内容","labels":["feature"]}' > /tmp/issue.json
curl -d @/tmp/issue.json ...
```

**问题：401 Unauthorized**
- 检查 token 是否正确
- 检查 token 是否过期
- 检查 token 权限

**问题：404 Not Found**
- 检查仓库名是否正确
- 检查仓库是否是私有的（需要登录）
- 检查 token 是否有访问该仓库的权限

### Issue 链接返回 404

**原因：** 仓库是私有的

**解决方案：**
1. 确认登录的 GitHub 账号有权限
2. 或添加为 collaborator
3. 或通过 API 访问（使用 token）

## 示例场景

### 场景 1：快速创建 Feature Issue
```bash
./create-issue.sh \
  --repo "Onlyaguest/MySanityCheck" \
  --title "支持 iPhone Screen Time 数据采集" \
  --type feature \
  --priority high \
  --phase 1 \
  --body "完整的功能描述..."
```

### 场景 2：批量创建 Issues
```bash
# 从 CSV 或 JSON 文件读取
cat issues.json | jq -c '.[]' | while read issue; do
  curl -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/repos/owner/repo/issues \
    -d "$issue"
done
```

### 场景 3：更新 Issue 标签
```bash
# 添加标签
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3/labels \
  -d '{"labels":["priority-high"]}'
```

## 参考资料

- [GitHub Issues API](https://docs.github.com/en/rest/issues/issues)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Labels API](https://docs.github.com/en/rest/issues/labels)

## 更新日志

- **2026-03-25**: 初始版本
  - 支持 Feature/Bug Issue 创建
  - 结构化模板
  - 标签管理
  - 安全最佳实践
