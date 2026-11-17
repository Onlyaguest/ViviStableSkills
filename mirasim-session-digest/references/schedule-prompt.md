# 每日增量定时任务的 prompt 模板

把尖括号换掉后整段作为 schedule_task 的 prompt。第一句里的「会话摘要每日增量」不要改：脚本靠这几个字认出定时任务自己的轮次。

```text
你在跑定时任务「<名字> · 会话摘要每日增量」。每次触发把下面几步做完就结束，不要停下来问人。

用 mirasim-session-digest 技能（<技能目录>/SKILL.md），摘要目录 <dir>，脚本 <技能目录>/scripts/digest.py，命令前都加 nice -n 10。

1. 跑 prep --dir <dir>。打印的 sessions 为 0 就跑 empty <label> --dir <dir>，跳到第 4 步。prep 报「材料包…还没并」：说明上次没做完或有人在跑，接着那个 label 做第 2、3 步，不加 --force。
2. 每批派一个帮手（Agent 工具，general-purpose，同一条消息里并行），提示照 SKILL.md 第 2 步。全部交回后抽查会话数、有没有路径和邮箱。
3. 跑 check <label> --dir <dir>，problems 非空就改对应 out 文件；再跑 merge <label> --dir <dir>。报「已经并过了」就不要重并，用它打印的那次新增写第 4 步。
4. 交付：chat_reply 发到 room <请求人跟你说话的 room>（<填 thread 或不填 = 主线>），attachments 放 <dir>/<标题>.md 和 <dir>/<标题>.html；text 两三行：更新到几点、新增几个会话几段、最值得看的一两件（等<名字>定的先说）。没有新东西只发一句「上次以来没有新的会话活动，会话摘要还是 X 月 X 日那份」，不附文件。不发群，不 @ 人。

规矩：只读源会话和聊天记录，不改别的定时任务；话里不贴路径、uid、消息编号；不写邮箱和密钥，别人私信里的原话不引。出错或一小时还没出完：照样在同一处用一句人话说今天没更新上、卡在哪。
```
