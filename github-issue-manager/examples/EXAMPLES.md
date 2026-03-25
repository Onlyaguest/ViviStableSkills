# GitHub Issue Manager 使用示例

## 示例 1：创建 Feature Issue

```bash
# 设置环境变量
export GITHUB_TOKEN="ghp_your_token_here"

# 创建 Feature Issue
./create-issue.sh \
  --repo "Onlyaguest/MySanityCheck" \
  --title "支持 iPhone Screen Time 数据采集" \
  --type feature \
  --priority high \
  --phase 1
```

**输出：**
```
正在创建 Issue...
仓库: Onlyaguest/MySanityCheck
标题: 支持 iPhone Screen Time 数据采集
类型: feature
标签: ["feature", "priority-high", "phase-1"]

✅ Issue 创建成功！
Issue #3: https://github.com/Onlyaguest/MySanityCheck/issues/3
```

## 示例 2：创建 Bug Issue

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "修复数据同步错误" \
  --type bug \
  --priority high
```

## 示例 3：使用自定义内容

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "优化性能" \
  --type enhancement \
  --priority medium \
  --body "需要优化数据库查询性能，减少响应时间。"
```

## 示例 4：添加额外标签

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "添加新功能" \
  --type feature \
  --priority high \
  --labels "needs-review,breaking-change"
```

## 示例 5：使用 curl 直接调用 API

```bash
# 创建 JSON 文件
cat > /tmp/issue.json << 'EOF'
{
  "title": "支持多语言",
  "body": "## 功能描述\n添加国际化支持\n\n## 验收标准\n- [ ] 支持中英文切换",
  "labels": ["feature", "priority-medium"]
}
EOF

# 调用 API
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/owner/repo/issues \
  -d @/tmp/issue.json
```

## 示例 6：查询 Issue 状态

```bash
# 查看特定 Issue
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3

# 查看所有 open issues
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/owner/repo/issues?state=open"

# 查看带特定标签的 issues
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/owner/repo/issues?labels=feature,priority-high"
```

## 示例 7：更新 Issue

```bash
# 添加评论
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3/comments \
  -d '{"body":"进度更新：已完成 50%"}'

# 更新标签
curl -X PUT \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3/labels \
  -d '{"labels":["feature","priority-high","in-progress"]}'

# 关闭 Issue
curl -X PATCH \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/owner/repo/issues/3 \
  -d '{"state":"closed"}'
```

## 工作流集成示例

### 与 AI Agent 集成

```bash
# AI Agent 收到 /feature 命令后
# 1. 起草 Issue
# 2. 用户 review
# 3. 调用脚本创建

./create-issue.sh \
  --repo "$REPO" \
  --title "$TITLE" \
  --type feature \
  --priority high \
  --phase 1
```

### 与 Cron 集成（进度追踪）

```bash
# 每天下午 2 点检查 open issues
0 14 * * * /path/to/check-issues.sh

# check-issues.sh 内容：
#!/bin/bash
ISSUES=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/owner/repo/issues?state=open")

COUNT=$(echo "$ISSUES" | jq '. | length')
echo "当前有 $COUNT 个 open issues"

# 如果有更新，通知用户
if [ $COUNT -gt 0 ]; then
  echo "$ISSUES" | jq -r '.[] | "Issue #\(.number): \(.title)"'
fi
```

## 常见问题

### Q: Token 从哪里获取？
A: 访问 https://github.com/settings/tokens 创建 Personal Access Token

### Q: 需要什么权限？
A: 至少需要 `repo` 权限（包含 issues 读写）

### Q: 如何避免 token 泄露？
A: 
1. 使用环境变量
2. 添加到 .gitignore
3. 定期轮换 token
4. 不要硬编码在脚本中

### Q: 私有仓库的 Issue 为什么返回 404？
A: 需要用有权限的账号登录 GitHub，或通过 API（使用 token）访问
