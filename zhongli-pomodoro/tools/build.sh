#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build runtime /tmp/zhongli-swift-cache
swiftc -module-cache-path /tmp/zhongli-swift-cache Sources/TimerModel.swift tests/TimerTests.swift -o build/timer-tests
build/timer-tests
swiftc -module-cache-path /tmp/zhongli-swift-cache Sources/CompanionMode.swift tests/ModeTests.swift -o build/mode-tests
build/mode-tests
APP="$PWD/build/钟离茶伴.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
swiftc -O -module-cache-path /tmp/zhongli-swift-cache Sources/TimerModel.swift Sources/CompanionMode.swift Sources/main.swift -o "$APP/Contents/MacOS/ZhongliCompanion" -framework AppKit
if [[ ! -f Assets/Animations/manifest.json ]]; then
  mkdir -p Assets
  swift -module-cache-path /tmp/zhongli-swift-cache tools/placeholder.swift "$PWD/Assets"
fi
if [[ ! -f Assets/beeps.wav ]]; then
  python3 - <<'AUDIO'
import wave, math, struct
with wave.open('Assets/beeps.wav','wb') as w:
 w.setparams((1,2,22050,0,'NONE','not compressed'))
 w.writeframes(b''.join(struct.pack('<h',int(6000*math.sin(2*math.pi*880*i/22050))* (1 if i%6615<3969 else 0)) for i in range(19845)))
AUDIO
fi
cp -R Assets/Animations "$APP/Contents/Resources/"
cp Assets/beeps.wav "$APP/Contents/Resources/"
if [[ -f Assets/break-voice.mp3 ]]; then cp Assets/break-voice.mp3 "$APP/Contents/Resources/"; fi
: > "$APP/Contents/Resources/session.txt"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>ZhongliCompanion</string>
<key>CFBundleIdentifier</key><string>online.yuanzi.zhongli-companion</string>
<key>CFBundleName</key><string>钟离茶伴</string>
<key>CFBundleVersion</key><string>1</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>LSUIElement</key><true/>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --deep --sign - "$APP"
echo "$APP"
