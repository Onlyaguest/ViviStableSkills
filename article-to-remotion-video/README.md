# Article to Remotion Video

把一篇文章或长文资料转换成可本地预览、可重复渲染、可验收的 Remotion 短视频。

核心是 Remotion：文章先被整理成结构化 `story.json`，模板再据此生成画面。Cohub TTS 是可选配音来源，STT 用于检查最终成片的口播，GSAP 只在需要复杂浏览器动画时作为可选补充。

## 快速开始

```bash
python3 scripts/scaffold_project.py ./my-video
python3 scripts/validate_story.py ./my-video/story.json
cd ./my-video && npm install && npm run start
```

修改 `my-video/story.json` 即可替换文章内容、镜头节奏、图片和配音路径。模板默认生成 16:9、45–60 秒的视频。

## 可选配音

首次使用 Cohub 时：

1. [通过邀请链接注册 Cohub](https://cohub.live/referrals/M2p3aMZKISee)
2. [加入推荐的文字转语音世界](https://cohub.live/yuanzi/wo-tui-hong-wo-vibe-coding/join/NoW4CJmuoNAt)

加入后安装并登录 Cohub CLI，通过 `cohub spaces ls --json` 找到该世界对应的 Space ID。邀请链接仅用于可选的注册和加入，不会被脚本自动打开。

先预览任务，不会调用远程生成：

```bash
python3 scripts/cohub_tts.py ./my-video/story.json --dry-run
```

确认已安装并登录 Cohub CLI 后，再传入 `--space-id` 或设置 `COHUB_SPACE_ID` 生成分镜音频。该步骤可能产生远程服务费用。

## 验收与导出

```bash
cd ./my-video
npm run check
npm run render
```

最终还应检查代表性静帧、MP4 音轨、响度，以及用 STT 核对完整成片口播。详见 [SKILL.md](./SKILL.md) 和 `references/`。

## 依赖

- Python 3.8+
- Node.js 与 npm
- ffmpeg / ffprobe
- 可选：Cohub CLI（配音）、Soniox 或其他 STT 工具（口播验收）

模板固定了已验证的 Remotion 依赖版本；运行时输出、凭证和本地素材不会进入版本控制。
