# Open in Omia

让 AI Agent 把本地交付物直接交给 **Xiaoer Omia** 打开审阅。

Omia 是一款本地优先的 macOS 万能阅览器，适合查看 HTML、Markdown、PDF、Office、图片、音视频、数据文件、压缩包、代码和 3D 文件。

## Omia

- [Omia 官方网站](https://xiaoeromia.com/)
- [下载 Omia 最新版本](https://github.com/Jane-xiaoer/xiaoer-omia-app/releases/latest)

安装并首次启动 Omia 后即可使用本 Skill。当前支持 macOS。

## Quick Start

```bash
chmod +x bin/open-in-omia.sh

# 检查文件是否可以交给 Omia
bin/open-in-omia.sh --check "/path/to/report.html"

# 用 Omia 打开
bin/open-in-omia.sh "/path/to/report.html"
```

## Install for Codex

从 `ViviStableSkills` 仓库根目录执行：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/open-in-omia"
cp -R open-in-omia/. "${CODEX_HOME:-$HOME/.codex}/skills/open-in-omia/"
chmod +x "${CODEX_HOME:-$HOME/.codex}/skills/open-in-omia/bin/open-in-omia.sh"
```

之后可以直接对 Codex 说：

> 用 Omia 打开最新的 HTML 看看。

## Behavior

- 只负责打开和审阅，不编辑或转换文件
- 不修改 macOS 全局文件关联
- 不会在失败时偷偷切换到其他应用
- 多个候选产物默认只打开主交付物

完整说明见 [SKILL.md](./SKILL.md)。
