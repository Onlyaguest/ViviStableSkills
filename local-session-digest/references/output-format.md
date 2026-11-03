# 输出合同

目录：summaries/ 每会话一份；activity-digest.md 一份；manifest.json 一份。
文件名用窗口日期、短主题和稳定会话 ID，避免同名会话相互覆盖。

## 独立摘要

```markdown
# 会话标题

- Agent：当前宿主
- Session ID：真实 ID
- Session：[原始标题](真实会话链接或本地记录)
- Session开始时间：真实创建时间和时区；缺失写未知
- 本次处理窗口：起点（含）至终点（不含）
- 来源：用户主动 / 明确派工 / 自动任务 / 自动派生

## Events

### 1. 可读的活动标题

- 活动时间：窗口内真实 turn 起止时间
- 活动一句话：低上下文、日常语言
- 高层总结：这件事带来了什么变化
- 判断/状态：已完成 / 进行中 / 中断 / 失败 / 阻塞或等待 / 等待验收 / 无新增产物
- 证据/结果：
  - 1–3 条可核验结果，包含必要结果链接或路径
- 下一步：有依据的复核点；没有就写无，由用户决定是否继续
- 项目标签：一个稳定标签
- 细节线索：原 turn ID、材料原日期、验证限制等
```

“活动一句话”取代外部笔记专用字段名，保留同样的摘要信息结构。
同一会话多主题按事件续写，不把敏感私聊全文贴入。

## Activity Digest

```markdown
- Session Activity Digest · YYYY-MM-DD
  - 窗口：起止时间和时区
  - 范围：当前本地 agent，跨项目；主动/自动纳入口径
  - 来源：宿主名称及读取范围
  - 活动：N 个 Session，M 段活动，K 个真实 turn
  - 覆盖：complete 或 partial；说明本地来源与缺口
  - 说明：实际 turn 时间；原会话自报验证与本轮核验分开
- HH:MM [一句可读的活动标题](真实入口) #项目标签
  - Session：[原始标题](真实入口)（真实 ID）
  - 运行时间：YYYY-MM-DD HH:MM:SS–HH:MM:SS 时区
  - 状态：事实状态；触发来源
  - 证据
    - 2–4 条有实际内容的证据；必要时引用真实产物
  - 判断：这件事意味着什么，不复述状态或使用通用套话
  - 下一检查：有依据的复核点，或无
  - source：真实会话入口；本地独立摘要路径
```

不提供深链的宿主可使用本地来源链接；没有可核验路径时保留真实 ID 并明确说明，不伪造链接。
分成主动/自动两组时，组内保持升序，顶部同时给总数和分组数量。

## manifest 最小字段

```json
{
  "schema_version": 1,
  "agent": "host-name",
  "source_scope": "current-local-profile",
  "window": {"start": "ISO8601", "end_exclusive": "ISO8601", "timezone": "IANA timezone"},
  "coverage": {"status": "partial", "missing": ["具体缺口"], "sources_checked": []},
  "sessions": [],
  "excluded": [],
  "digest_path": "activity-digest.md"
}
```

sessions 每项包含 session_id、真实标题、source_locator、turn_ids、首次/最后活动时间、触发来源、summary_path、证据截至时间。
excluded 只存 ID 与排除原因，不存敏感消息正文。
相同来源、窗口和 session ID 是稳定去重键；同一任务跨日分别记录，不覆盖旧窗口。
