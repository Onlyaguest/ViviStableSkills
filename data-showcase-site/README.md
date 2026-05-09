# data-showcase-site

把你“已经拿到的数据”整理成报告（JSON / CSV / 数据库导出 CSV），一键生成一个静态 HTML 站点（图文 + 表格 + 简单图表），并可选发布到一个**单独的静态站点仓库**（推荐）供 Vercel 直接展示。

## Visual Guide

打开 `guide.html` 可以直接看到：

- 这个 skill 的定位和边界
- 最小验证命令
- 真实构建命令
- 审核清单

## 安装与运行（Python）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py --help
```

## 最小使用（用内置示例）

```bash
python main.py build --use-examples
open out/site/index.html
```

## 你的数据放哪里？

- `reports/`：放若干 `*.json` 报告（默认会被 `.gitignore` 忽略，避免误提交原始数据）
- `reports/`：也可以直接放 `*.csv/*.tsv`（数据库导出常见），开启 `AUTO_REPORT_FROM_CSV=1` 后会自动生成“每个 CSV 一页”的基础报告
- `reports/`：也支持直接放 `*.html`（AI 直接给你 HTML）或 `*.md`（Markdown）
- `assets/`：图片/附件（同样默认忽略）

你也可以用命令行覆盖目录：

```bash
python main.py build --reports /abs/path/reports --assets /abs/path/assets --out out/site
```

## Report JSON 结构（约定）

每个 `reports/*.json` 是一份报告，最小示例：

```json
{
  "slug": "demo",
  "title": "Demo Report",
  "blocks": [
    { "type": "markdown", "content": "# Hello\\n\\n这是一段说明" },
    { "type": "table", "title": "Summary", "columns": ["k", "v"], "rows": [["a", 1], ["b", 2]] },
    { "type": "chart", "title": "Bar", "kind": "bar", "data": [{"label":"A","value":10},{"label":"B","value":22}] },
    { "type": "image", "title": "An Image", "src": "demo.svg" }
  ]
}
```

支持的 `block.type`：`markdown` / `table` / `chart` / `image` / `html`。

## 发布到单独仓库（推荐）

你说的“只 push HTML / 干净部署”更适合用单独仓库承载构建结果：这个仓库只存 `index.html + r/... + assets/...`。

配置（见 `.env.example`）：

- `PUBLISH_MODE=repo`
- `PUBLISH_REPO_URL=...`
- `PUBLISH_REPO_BRANCH=main`（或你希望的分支）

发布命令：

```bash
python main.py build
python main.py publish
```

说明：

- 默认会在本工具目录下创建/使用 `PUBLISH_REPO_DIR`（例如 `.publish-repo/`）作为本地 clone；该目录已在本工具 `.gitignore` 中忽略
- 首次发布如果本地没有 clone，会执行 `git clone` / `git push`（需要网络与 git 权限）

## 发布到“只含 HTML”的分支（可选）

思路：本工具先 `build` 生成 `out/site/`，再把 `out/site/` 同步到一个 `git worktree`（指向 `site` 分支），最后提交并 push。这样远端的 `site` 分支里只有静态站点文件。

```bash
python main.py build
python main.py publish
```

Vercel 侧建议：

- 选择分支：`site`
- Framework Preset：`Other`
- Build Command：留空（或 `None`）
- Output Directory：`.`（仓库根就是静态文件）

## 自动模式（本地 watch）

目录内容变化时自动重建（可选自动发布）：

```bash
python main.py watch --interval 2
python main.py watch --interval 2 --publish
```

## 配置

见 `.env.example`；所有项都可被命令行参数覆盖。
