#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build /tmp/zhongli-swift-cache
swiftc -module-cache-path /tmp/zhongli-swift-cache Sources/TimerModel.swift tests/TimerTests.swift -o build/timer-tests
build/timer-tests
swiftc -module-cache-path /tmp/zhongli-swift-cache Sources/CompanionMode.swift tests/ModeTests.swift -o build/mode-tests
build/mode-tests
