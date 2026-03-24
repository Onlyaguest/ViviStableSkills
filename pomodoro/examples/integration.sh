#!/usr/bin/env bash
# Pomodoro Integration Examples
# Shows how to integrate the Pomodoro skill with various AI agents and workflows

set -euo pipefail

POMODORO_BIN="$(cd "$(dirname "$0")/.." && pwd)/bin/pomodoro.sh"

# Example 1: Simple AI Agent Integration
example_simple_agent() {
    echo "=== Example 1: Simple AI Agent Integration ==="
    
    # Agent checks if it's work hours
    current_hour=$(date +%H)
    if [ "$current_hour" -ge 9 ] && [ "$current_hour" -lt 18 ]; then
        echo "Work hours detected. Starting pomodoro..."
        "$POMODORO_BIN" start "AI Agent Task" 25
    else
        echo "Outside work hours. Skipping pomodoro."
    fi
}

# Example 2: Task Queue Integration
example_task_queue() {
    echo "=== Example 2: Task Queue Integration ==="
    
    # Simulate task queue
    tasks=(
        "处理邮件:15"
        "代码审查:25"
        "文档更新:15"
    )
    
    for task_entry in "${tasks[@]}"; do
        IFS=':' read -r task duration <<< "$task_entry"
        echo "Starting: $task ($duration minutes)"
        "$POMODORO_BIN" start "$task" "$duration"
        
        # Wait for completion (in real scenario, this would be async)
        sleep $((duration * 60))
        
        echo "Completed: $task"
    done
}

# Example 3: Roam Research Integration
example_roam_integration() {
    echo "=== Example 3: Roam Research Integration ==="
    
    # Get today's tasks from Roam (simulated)
    # In real scenario: bb roam-query :yuanvv '[:find ?task ...]'
    
    tasks=(
        "学习新技能"
        "写技术文档"
        "团队会议准备"
    )
    
    for task in "${tasks[@]}"; do
        echo "Starting Roam task: $task"
        "$POMODORO_BIN" start "$task" 25
        
        # Simulate work
        sleep 5
        
        # Complete with note
        "$POMODORO_BIN" done "从Roam同步"
        echo "Completed and synced back to Roam"
    done
}

# Example 4: Dashboard Auto-Update
example_dashboard_update() {
    echo "=== Example 4: Dashboard Auto-Update ==="
    
    # Start session
    "$POMODORO_BIN" start "Dashboard测试" 1
    
    # Wait for completion
    sleep 65
    
    # Update dashboard
    DASHBOARD_BIN="$(cd "$(dirname "$0")/.." && pwd)/bin/dashboard.sh"
    if [ -f "$DASHBOARD_BIN" ]; then
        echo "Updating dashboard..."
        "$DASHBOARD_BIN"
        echo "Dashboard updated!"
    fi
}

# Example 5: Energy Tracking Integration
example_energy_tracking() {
    echo "=== Example 5: Energy Tracking Integration ==="
    
    # Read today's sessions
    DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"
    if [ -f "$DATA_DIR/sessions.json" ]; then
        total_energy=$(python3 -c "
import json
data = json.load(open('$DATA_DIR/sessions.json'))
today = '$(date +%Y-%m-%d)'
sessions = [s for s in data.get('sessions', []) if s.get('date') == today]
total = sum(s.get('energy', 0) for s in sessions)
print(total)
")
        echo "Today's total energy cost: $total_energy"
        
        # Alert if energy is too low
        if [ "$total_energy" -lt -100 ]; then
            echo "⚠️ Warning: High energy consumption today!"
            echo "Consider taking a longer break."
        fi
    fi
}

# Example 6: Interruption Handling
example_interruption_handling() {
    echo "=== Example 6: Interruption Handling ==="
    
    # Start session
    "$POMODORO_BIN" start "可能被打断的任务" 25
    
    # Simulate interruption after 10 seconds
    sleep 10
    
    # Check if urgent event occurred (simulated)
    urgent_event=true
    
    if [ "$urgent_event" = true ]; then
        echo "Urgent event detected. Interrupting session..."
        "$POMODORO_BIN" interrupt "紧急会议"
        echo "Session interrupted and logged."
    fi
}

# Example 7: Multi-Agent Coordination
example_multi_agent() {
    echo "=== Example 7: Multi-Agent Coordination ==="
    
    # Agent A starts a task
    echo "[Agent A] Starting task..."
    "$POMODORO_BIN" start "Agent A Task" 15
    
    # Agent B monitors progress
    sleep 5
    echo "[Agent B] Checking status..."
    "$POMODORO_BIN" status
    
    # Wait for completion
    sleep 10
    
    # Agent C updates dashboard
    echo "[Agent C] Updating dashboard..."
    # Dashboard update would happen here
}

# Main menu
show_menu() {
    echo ""
    echo "Pomodoro Integration Examples"
    echo "=============================="
    echo "1. Simple AI Agent Integration"
    echo "2. Task Queue Integration"
    echo "3. Roam Research Integration"
    echo "4. Dashboard Auto-Update"
    echo "5. Energy Tracking Integration"
    echo "6. Interruption Handling"
    echo "7. Multi-Agent Coordination"
    echo "0. Exit"
    echo ""
}

# Run examples
if [ $# -eq 0 ]; then
    show_menu
    read -p "Select example (0-7): " choice
    
    case $choice in
        1) example_simple_agent ;;
        2) example_task_queue ;;
        3) example_roam_integration ;;
        4) example_dashboard_update ;;
        5) example_energy_tracking ;;
        6) example_interruption_handling ;;
        7) example_multi_agent ;;
        0) echo "Goodbye!" ;;
        *) echo "Invalid choice" ;;
    esac
else
    # Run specific example
    case $1 in
        simple) example_simple_agent ;;
        queue) example_task_queue ;;
        roam) example_roam_integration ;;
        dashboard) example_dashboard_update ;;
        energy) example_energy_tracking ;;
        interrupt) example_interruption_handling ;;
        multi) example_multi_agent ;;
        *) echo "Unknown example: $1" ;;
    esac
fi
