#!/bin/bash
# GitHub Issue Creator
# 使用 GitHub API 创建 Issue

set -euo pipefail

# 默认值
REPO=""
TITLE=""
BODY=""
TYPE="feature"
PRIORITY="medium"
PHASE=""
LABELS=""
DRY_RUN=false

# 帮助信息
show_help() {
    cat << EOF
使用方法: $0 [选项]

选项:
    --repo REPO         仓库名称 (格式: owner/repo)
    --title TITLE       Issue 标题
    --body BODY         Issue 内容 (可选，会使用模板)
    --type TYPE         Issue 类型: feature|bug|enhancement (默认: feature)
    --priority LEVEL    优先级: high|medium|low (默认: medium)
    --phase NUMBER      阶段: 1|2|3 (可选)
    --labels LABELS     额外标签，逗号分隔 (可选)
    --template FILE     使用自定义模板文件 (可选)
    --dry-run           预览 Issue 内容，不实际创建
    -h, --help          显示帮助信息

环境变量:
    GITHUB_TOKEN        GitHub Personal Access Token (必需)

示例:
    # 创建 Feature Issue
    $0 --repo "owner/repo" --title "支持新功能" --type feature --priority high --phase 1

    # 创建 Bug Issue
    $0 --repo "owner/repo" --title "修复错误" --type bug --priority high

    # 使用自定义模板
    $0 --repo "owner/repo" --title "标题" --template custom.json
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
            shift 2
            ;;
        --type)
            TYPE="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --labels)
            LABELS="$2"
            shift 2
            ;;
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$GITHUB_TOKEN" ]; then
    echo "错误: 未设置 GITHUB_TOKEN 环境变量"
    echo "请运行: export GITHUB_TOKEN='your_token_here'"
    exit 1
fi

if [ -z "$REPO" ]; then
    echo "错误: 必须指定 --repo"
    show_help
    exit 1
fi

if [ -z "$TITLE" ]; then
    echo "错误: 必须指定 --title"
    show_help
    exit 1
fi

# 构建标签数组
LABEL_ARRAY="[\"$TYPE\""

if [ -n "$PRIORITY" ]; then
    LABEL_ARRAY="$LABEL_ARRAY, \"priority-$PRIORITY\""
fi

if [ -n "$PHASE" ]; then
    LABEL_ARRAY="$LABEL_ARRAY, \"phase-$PHASE\""
fi

if [ -n "$LABELS" ]; then
    IFS=',' read -ra EXTRA_LABELS <<< "$LABELS"
    for label in "${EXTRA_LABELS[@]}"; do
        LABEL_ARRAY="$LABEL_ARRAY, \"$label\""
    done
fi

LABEL_ARRAY="$LABEL_ARRAY]"

# 如果指定了模板文件，使用模板
if [ -n "$TEMPLATE" ]; then
    if [ ! -f "$TEMPLATE" ]; then
        echo "错误: 模板文件不存在: $TEMPLATE"
        exit 1
    fi
    
    # 读取模板并替换标题和标签
    ISSUE_JSON=$(cat "$TEMPLATE" | jq --arg title "$TITLE" --argjson labels "$LABEL_ARRAY" '.title = $title | .labels = $labels')
else
    # 使用默认模板
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TEMPLATE_FILE="$SCRIPT_DIR/templates/$TYPE.json"
    
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "错误: 模板文件不存在: $TEMPLATE_FILE"
        exit 1
    fi
    
    ISSUE_JSON=$(cat "$TEMPLATE_FILE" | jq --arg title "$TITLE" --argjson labels "$LABEL_ARRAY" '.title = $title | .labels = $labels')
fi

# 如果指定了自定义 body，覆盖模板
if [ -n "$BODY" ]; then
    ISSUE_JSON=$(echo "$ISSUE_JSON" | jq --arg body "$BODY" '.body = $body')
fi

# 创建临时文件
TEMP_FILE=$(mktemp)
echo "$ISSUE_JSON" > "$TEMP_FILE"

# 预览信息
echo "仓库: $REPO"
echo "标题: $TITLE"
echo "类型: $TYPE"
echo "标签: $LABEL_ARRAY"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Issue 内容预览："
    echo "$ISSUE_JSON" | jq '.'
    echo ""
    echo "（未创建，使用时去掉 --dry-run 即可）"
    rm -f "$TEMP_FILE"
    exit 0
fi

# 调用 GitHub API
echo "正在创建 Issue..."

RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/issues" \
  -d @"$TEMP_FILE")

# 清理临时文件
rm "$TEMP_FILE"

# 检查响应
if echo "$RESPONSE" | jq -e '.html_url' > /dev/null 2>&1; then
    ISSUE_URL=$(echo "$RESPONSE" | jq -r '.html_url')
    ISSUE_NUMBER=$(echo "$RESPONSE" | jq -r '.number')
    echo "✅ Issue 创建成功！"
    echo "Issue #$ISSUE_NUMBER: $ISSUE_URL"
else
    echo "❌ Issue 创建失败"
    echo "$RESPONSE" | jq '.'
    exit 1
fi
