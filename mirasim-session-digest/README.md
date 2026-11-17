# Mirasim Session Digest

给 mirasim 空间里的某个人出「会话摘要」，并能每天增量更新：先是按时间的活动记录，后面每个会话一份摘要，每件事带状态（已完成 / 进行中 / 阻塞或等待 / 等待验收）。产出一份 md 和一份每条都能收起的网页。

和同仓库的 [local-session-digest](../local-session-digest/) 的区别：那个总结任意本地 agent 自己的会话；这个专门读 mirasim 空间（工作台会话、私信和群里叫助手的、助手派出的任务、定时任务），按「请求人能看到的范围」过滤。

安装：把本目录放进 mirasim 的技能目录，例如 `~/.mirasim/skills/mirasim-session-digest/`。

使用：

> 出一份我的会话摘要
> 给 某人 出最近 7 天的会话摘要
> 每天早上更新我的会话摘要

第一次运行 `init`，之后每次照 SKILL.md 的步骤补增量；要每天自动更新，按 `references/schedule-prompt.md` 设一个定时任务。

隐私：只读请求人能看到的地方，私信和私密群只读请求人本人在里面的；不写邮箱、手机号、密钥；摘要只交给请求人。本目录只有方法和脚本，不含任何人的会话内容，真实摘要不要提交进仓库。

依赖：python3（只用标准库）。

详细规则见 [SKILL.md](SKILL.md)。
