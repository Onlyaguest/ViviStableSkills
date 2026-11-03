# Local Session Digest

让当前本地 AI agent 总结自己的会话：每会话一份摘要，再给一条按时间排序的活动记录。

安装：将本目录复制到当前 agent 支持的 skills 目录；Codex 通常为 `${CODEX_HOME:-$HOME/.codex}/skills/local-session-digest`。

使用：

> 使用 local-session-digest，总结昨天这个本地 agent 的所有会话。

默认覆盖当前本地配置、跨所有项目的昨日真实活动；不是只看当前聊天。可指定日期、时区、输出目录，或明确要求全部历史。

产物默认写入 `output/session-digest/`：

- `summaries/`：逐会话总结。
- `activity-digest.md`：时间线。
- `manifest.json`：覆盖、去重和证据索引。

无需额外依赖或 API key。由宿主 agent 通过已有本地读取能力执行；没有可靠全量接口时会报告覆盖缺口。

不接 Cohub，不读写 Roam，不上传历史，不创建自动任务。真实摘要仍是私人资料，不能随 skill 一起提交。

详细规则见 [SKILL.md](SKILL.md)。
