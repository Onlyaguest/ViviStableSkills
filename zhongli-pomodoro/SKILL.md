---
name: zhongli-pomodoro
description: 构建、维护钟离版 Mac 桌宠番茄钟，处理独立计时与 Codex 陪伴模式、素材和本地记录。
version: 0.1.0
---
# 钟离版番茄钟

## 使用范围

本目录是 Mac AppKit 桌宠工程，不是硬件固件，也不是 ChatGPT 内置宠物插件。构建和维护本工程时使用。

## 快速开始

运行 `./tools/build.sh`，然后打开 `build/钟离茶伴.app`。无私人素材时使用简单占位图和合成提示音；私人素材的放置格式见 README。

## 维护约束

- 修改前阅读 docs/MAINTENANCE.md；待办优先级见 docs/ROADMAP.md。
- 计时和 Codex 模式独立；切换模式不暂停、不重置计时。
- 当前只有累计完成轮数，没有逐轮历史；不要把计划描述成已实现。
- 保存域 online.yuanzi.zhongli-companion 不得随升级重置；新增历史需迁移旧累计。
- 状态仅来自用户配置的本地任务；不可用不等于完成。不自行更改状态提供方钩子。
- 运行 ./tools/test.sh 验证状态模型。涉及 UI 或音频还需人工验收。
- 更新运行中的 app 前保留用户当前计时和上一版包；不要为测试启动、结束或重置用户真实轮次。
- Assets、runtime、build、个人记录不提交。仅在用户授权的范围提交发布。

## 命令参考

| 命令 | 用途 |
|---|---|
| ./tools/test.sh | 无素材运行计时与模式测试 |
| ./tools/build.sh | 编译并本地签名应用 |
| open 'build/钟离茶伴.app' --args --session UUID | 关注一个指定任务；先退出已有实例 |
| python3 tools/prepare_assets.py | 从本地视频提取透明帧，需 ffmpeg 和 Pillow |

## 配置与常见问题

状态源需要已有的 ~/.confirmo/claude-status/sessions/ 文件；本工程不会安装状态提供方。无状态源时番茄钟可离线运行。

正常退出后计时以暂停状态恢复。内部 --resume-after-update 参数仅供确认更新前正在计时的维护场景使用。

换肤、成就墙与逐轮历史尚在路线图，不是当前功能。声音舒适度、多屏和长时间性能仍需体验验证。
