# Usage Examples

## Create a Feature Issue

```bash
export GITHUB_TOKEN="ghp_your_token_here"

./create-issue.sh \
  --repo "owner/repo" \
  --title "Add multi-device support" \
  --type feature \
  --priority high \
  --phase 1
```

## Create a Bug Issue

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "Fix data sync error" \
  --type bug \
  --priority high
```

## Preview Before Creating (Dry Run)

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "New feature" \
  --type feature \
  --dry-run
```

## Custom Body Text

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "Improve performance" \
  --type enhancement \
  --priority medium \
  --body "Optimize database queries to reduce response time."
```

## Extra Labels

```bash
./create-issue.sh \
  --repo "owner/repo" \
  --title "Breaking change" \
  --type feature \
  --labels "needs-review,breaking-change"
```

## Query Issues via API

```bash
# List open issues
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/issues?state=open" | jq '.[].title'

# Close an issue
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/issues/1" \
  -d '{"state":"closed"}'
```
