# 本地来源适配

只适配当前实际运行的宿主；以下接口名仅表示已知 Codex 能力，使用前以当前工具 schema 为准。

## Codex 桌面

1. list_threads 找候选，过滤到当前本地 host 和 Codex 类型；不要把 ChatGPT 云会话或远程 host 混入。
2. read_thread 读取真实 turns，沿 cursor 继续，直到越过窗口起点。每条记录保留 startedAt、completedAt、status 和用户请求/最终回复的必要证据。
3. 主列表可能有条数上限且不含归档；使用 list_archived_threads 分页或下面的本地索引补全，不凭第一页宣称全部。
4. 时间戳以实际单位解析，区分 Unix 秒、毫秒和 ISO8601。先转用户时区，再判断日期。

## Codex 本地记录（CLI 或桌面补漏）

根目录从 CODEX_HOME 读取；未设置时使用当前用户的 .codex 目录。
常见候选位置为 sessions/、archived_sessions/ 下的 rollout JSONL，以及 state_*.sqlite 内的 threads 索引。实际格式可能变化，先探测文件和表结构。

- SQLite 必须以 mode=ro 打开，只查询需要的 ID、来源、归档状态、rollout 路径及时间；不要输出整行 first_user_message、preview 等可能含密钥的字段。
- updated_at、文件修改时间、目录日期只能帮助发现候选。旧创建目录中的会话可能在今天继续活动。
- 索引不完整或损坏时，扫描 sessions 与 archived_sessions 的所有记录时间；不能只看目标日期的目录。
- 先检查少量记录的结构。常见 session_meta、turn_context、event_msg、response_item 分别承载来源、turn 归属和消息；不要把每行 JSONL 当作一个 turn。
- 优先 task_started / task_complete / turn_aborted 等生命周期事件与稳定 turn ID。只有 user_message / agent_message 的旧格式时按真实角色和时间重建，标记不能确认的边界。
- 同一消息可能同时出现在 event_msg 与 response_item；只选一条规范来源，不重复计数。
- fork 可能包含原会话历史；依据 session_meta 中的父/源引用及源 turn ID 去重。继承但没有新执行的片段不算新活动。
- 只保留截止前可见的证据。仍在写入的最后一行无法解析时记录读取缺口，保留已有完整行，不损坏源文件。
- 含 subagent/source 的记录按来源链纳入并标明派工；无法确认归属时列在覆盖缺口。
- 记录截断、丢失、无法解析、无法读取，都不能当作“没有活动”。

不要把解析脚本的猜测当成宿主官方 schema。适配不足时宁可报告 partial，保留已读会话，不造出完整覆盖。

## 其他本地 agent

使用当前宿主明确提供的会话列表、导出或本地记录格式。先检查能力说明与实际样本，再读取目标窗口。
没有已验证接口时，可请用户指定本地历史导出位置；不调用其他产品账号或远程同步作为默认替代。
用户提供导出文件时，说明覆盖仅限该导出，不声称覆盖整个 agent。

## 最小验证场景

修改适配逻辑后，用合成或私人本地样本验证：旧会话新 turn、归档会话、零活动、跨午夜未完成、自动派生、fork 重复、截断记录、超过一页的历史。
验证应检查是否纳入、时间和状态是否正确，而不只是检查标题字符串。
公开包只允许合成样本；实际运行输出留在用户指定的本地目录之外的私有存储中，不提交仓库。
