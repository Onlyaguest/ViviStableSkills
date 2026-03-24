#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
BASE_DIR="$HOME/.openclaw/workspace/skills/pomodoro"
DATA_DIR="$BASE_DIR/data"
STATE_FILE="$DATA_DIR/current.json"
LOG_FILE="$DATA_DIR/sessions.json"

mkdir -p "$DATA_DIR"

init_log() {
  if [ ! -f "$LOG_FILE" ]; then
    echo '{"sessions":[]}' > "$LOG_FILE"
  fi
}

notify() {
  local title="$1"
  local msg="$2"
  osascript -e "display notification \"$msg\" with title \"$title\""
}

new_id() {
  date +"%Y%m%d-%H%M%S"
}

start_timer() {
  local task="${1:-未命名任务}"
  local duration="${2:-25}"
  local now_ts now_human
  now_ts=$(date +%s)
  now_human=$(date +"%Y-%m-%d %H:%M:%S")

  cat > "$STATE_FILE" <<EOF
{
  "id": "$(new_id)",
  "task": "$task",
  "duration": $duration,
  "startTs": $now_ts,
  "startAt": "$now_human",
  "status": "running"
}
EOF

  notify "🍅 番茄钟开始" "$task（${duration}分钟）"

  # 后台计时器 - 自动完成
  (
    sleep $((duration * 60))
    if [ -f "$STATE_FILE" ]; then
      local st
      st=$(python3 -c "import json;print(json.load(open('$STATE_FILE')).get('status',''))")
      if [ "$st" = "running" ]; then
        "$SCRIPT_PATH" done "自动完成"
      fi
    fi
  ) &

  echo "✅ 已开始：$task（${duration}分钟）"
}

finish_timer() {
  local final_status="$1" # complete / interrupted
  local note="${2:-}"

  if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 当前没有进行中的番茄钟"
    exit 1
  fi

  # 保存状态用于 Roam 写入
  local task duration
  task=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['task'])")
  duration=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['duration'])")

  python3 - "$STATE_FILE" "$LOG_FILE" "$final_status" "$note" <<'PY'
import json,sys,time,datetime
state_path,log_path,status,note = sys.argv[1:]
state = json.load(open(state_path))
log = json.load(open(log_path))

end_ts = int(time.time())
start_ts = int(state['startTs'])
actual_min = max(1, round((end_ts - start_ts)/60))

def hm(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M')

def d(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

entry = {
    "id": state["id"],
    "date": d(start_ts),
    "startTime": hm(start_ts),
    "endTime": hm(end_ts),
    "duration": int(state["duration"]),
    "actualDuration": actual_min,
    "task": state["task"],
    "status": status,
    "note": note,
    "energy": -15 if status=="complete" else -8
}

log.setdefault("sessions", []).append(entry)
json.dump(log, open(log_path,'w'), ensure_ascii=False, indent=2)
print(entry["id"])
PY

rm -f "$STATE_FILE"

# 写入 Roam Research
if command -v bb &> /dev/null; then
  local icon
  icon=$([[ "$final_status" = "complete" ]] && echo "🍅" || echo "⚡")
  (cd ~/qq && bb roam-write :yuanvv "${icon} 番茄钟：${task}（${duration}分钟）#番茄钟") 2>/dev/null || true
fi

if [ "$final_status" = "complete" ]; then
  notify "✅ 番茄完成" "已记录到日志"
  echo "✅ 已完成并记录"
else
  notify "⚡ 番茄中断" "已记录中断"
  echo "⚡ 已中断并记录"
fi
}

show_status() {
  if [ -f "$STATE_FILE" ]; then
    cat "$STATE_FILE"
  else
    echo "🟢 当前没有进行中的番茄钟"
  fi
}

show_today() {
  python3 - "$LOG_FILE" <<'PY'
import json,sys,datetime
p=sys.argv[1]
log=json.load(open(p))
today=datetime.date.today().strftime('%Y-%m-%d')
arr=[x for x in log.get('sessions',[]) if x.get('date')==today]
print(f"📊 今日番茄：{len(arr)} 个")
for x in arr[-10:]:
    icon='🍅' if x['status']=='complete' else '⚡'
    print(f"{icon} {x['startTime']}-{x['endTime']} | {x['task']} | {x['status']}")
PY
}

init_log

cmd="${1:-status}"
case "$cmd" in
  start)
    shift || true
    start_timer "${1:-未命名任务}" "${2:-25}"
    ;;
  done)
    shift || true
    finish_timer "complete" "${1:-}"
    ;;
  interrupt)
    shift || true
    finish_timer "interrupted" "${1:-}"
    ;;
  status)
    show_status
    ;;
  today)
    show_today
    ;;
  *)
    echo "用法: $0 {start <任务> [分钟]|done [备注]|interrupt [备注]|status|today}"
    ;;
esac
