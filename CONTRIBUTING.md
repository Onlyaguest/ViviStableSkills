# ViviStableSkills 贡献指南

> 让每个 skill 都是即插即用的独立工具，让整个仓库始终保持整洁统一。

---

## 核心原则

1. **Clone 即用** — 任何人 clone 下来不改配置就能跑基础功能
2. **零泄露** — 绝不提交密钥、token、个人账号信息
3. **自包含** — 每个 skill 目录是独立单元，不依赖其他 skill
4. **简洁优先** — 文档说清楚怎么用就行，不堆砌重复内容

---

## 目录结构规范

每个 skill 必须遵循以下结构：

```
skill-name/
├── SKILL.md              # [必须] 完整文档（含 YAML frontmatter）
├── README.md             # [必须] 快速入门（不超过 80 行）
├── .gitignore            # [必须] 忽略运行时产出和敏感文件
├── bin/                  # [推荐] 可执行脚本入口
│   └── *.sh
├── examples/             # [推荐] 使用示例
├── assets/               # [可选] 静态资源（HTML 模板等）
├── requirements.txt      # [按需] Python 依赖（必须完整）
└── package.json          # [按需] Node.js 依赖
```

**禁止出现在仓库中的文件：**
- `.env`、`credentials.json` 等敏感文件
- `data/`、`output/`、`*__multilang__*` 等运行时产出
- `node_modules/`、`__pycache__/`、`.venv/` 等依赖目录

---

## SKILL.md 规范

### YAML Frontmatter（必填）

```yaml
---
name: skill-name              # 小写，用连字符分隔
description: 一句话说明        # 不超过 120 字符
version: 1.0.0                # 语义化版本
author: 作者名
tags: [category1, category2]  # 方便检索
platforms: [macos, linux]     # 支持的平台，可选值：macos / linux / windows / all
dependencies:                 # 运行时依赖（非 pip/npm 的系统级依赖）
  - python3
  - bash
---
```

### 文档正文结构

```markdown
# Skill 名称

一句话说清楚这个工具做什么。

## 功能概览
（要点列表，不超过 8 项）

## 快速开始
（3 步以内能跑起来）

## 命令参考
（表格形式，列出所有命令/参数）

## 配置说明
（环境变量、配置文件的完整说明）

## 常见问题
（精选 3-5 个高频问题）
```

**文档原则：**
- SKILL.md 总长度控制在 **200 行以内**
- 不要在 SKILL.md 和 README.md 之间复制粘贴内容
- README.md 是极简快速入门，SKILL.md 是完整参考手册
- 用例/示例放在 `examples/` 目录，不要全塞进文档

---

## 配置与安全规范

### 绝对禁止

| 类型 | 示例 | 说明 |
|------|------|------|
| 硬编码密钥 | `API_KEY = "sk-xxx"` | 必须用环境变量 |
| 硬编码个人路径 | `$HOME/MyWebsite/` | 必须用相对路径或环境变量 |
| 硬编码账号 | `bb roam-write :yuanvv` | 必须做成可配置参数 |
| 未确认的危险操作 | `git push origin main` | 需要用户明确确认 |

### 路径规范

```bash
# ❌ 错误：路径写死
BASE_DIR="$HOME/.openclaw/workspace/skills/pomodoro"

# ✅ 正确：相对于脚本自身定位
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${POMODORO_DATA_DIR:-$BASE_DIR/data}"
```

### 密钥/凭证规范

```bash
# ❌ 错误：硬编码
API_KEY="AQ.Ab8RN6Kb..."

# ✅ 正确：从环境变量读取，缺失时给出清晰报错
API_KEY="${GEMINI_API_KEY:?错误：请设置 GEMINI_API_KEY 环境变量}"
```

### 可选功能的隔离

对于依赖外部服务的功能（如 Roam 同步、Vercel 部署），必须：

1. 设计为**可选模块**，缺失时不影响核心功能
2. 通过环境变量或配置文件开关
3. 在文档中明确标注为 `[可选]`

```bash
# ✅ 正确：可选功能优雅降级
if [ -n "$ROAM_GRAPH" ] && command -v bb &> /dev/null; then
  (cd ~/qq && bb roam-write ":$ROAM_GRAPH" "$message") 2>/dev/null || true
else
  echo "ℹ️  Roam 同步已跳过（未配置 ROAM_GRAPH 或未安装 bb）"
fi
```

---

## 脚本编写规范

### Shell 脚本

```bash
#!/usr/bin/env bash
set -euo pipefail    # 必须：严格模式

# 路径：相对于脚本自身
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
```

- Git 中设置好执行权限（`chmod +x` 后提交）
- 文件路径用双引号包裹
- 依赖的外部命令在启动时检查

### Python 脚本

- 兼容 Python 3.8+（不使用 3.10+ 语法如 `match`）
- `requirements.txt` 列出**所有**直接依赖，包括标准库之外的一切
- 使用 `argparse` 提供 `--help`
- 关键操作提供 `--dry-run` 预览模式

### 幂等性

- 同一命令运行两次不应报错或产生副作用
- 输出目录已存在时，提供覆盖/跳过/报错三种策略

---

## .gitignore 模板

每个 skill 目录下的 `.gitignore` 至少包含：

```gitignore
# 运行时数据
data/
output/
*__multilang__*/
*__all-langs__*/

# 敏感文件
.env
.env.*
credentials.json
**/secrets/

# 系统/编辑器
.DS_Store
__pycache__/
*.pyc
node_modules/
.venv/
```

---

## 根目录 README.md 维护

添加新 skill 时，必须更新根目录 `README.md` 的 skill 索引表：

```markdown
## Available Skills

| Skill | 说明 | 平台 |
|-------|------|------|
| [skill-name](./skill-name/) | 一句话说明 | macOS / Linux |
```

---

## 新 Skill 上线检查清单

提交 PR 前，逐项确认：

```
[ ] 目录结构符合规范
[ ] SKILL.md 包含完整 YAML frontmatter
[ ] README.md 不超过 80 行
[ ] .gitignore 已创建且覆盖运行时产出
[ ] 无硬编码密钥、个人路径、个人账号
[ ] 路径基于脚本自身或环境变量，非绝对路径
[ ] Shell 脚本有执行权限
[ ] requirements.txt / package.json 依赖完整
[ ] 核心功能 clone 后不改配置可直接运行
[ ] 可选功能缺失时优雅降级，不报错
[ ] --help 可用，关键操作有 --dry-run
[ ] 根目录 README.md 已更新索引
```

---

## 版本与发布

- 每个 skill 独立版本号（在 SKILL.md frontmatter 中）
- 仓库整体使用 git tag 标记里程碑版本
- 破坏性变更（接口改动）必须升 major 版本

---

*规则由团队共同维护，有更好的想法随时提 PR。*
