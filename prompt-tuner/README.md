# 提示词工程工作台 (Prompt Engineering Workbench)

本目录是稳定版 `prompt-tuner` skill。它把提示词当代码管理：`prompt.txt` 是源代码，`cases.yaml` 是 Golden Dataset，`tuner.py` 是测试运行器。

## Visual Guide

打开 `guide.html` 可以直接看到：

- 这个 skill 解决什么问题
- 什么时候触发
- 本地最小验证怎么跑
- 完整回归测试怎么跑
- TDD for prompts 的工作流

## 📂 项目结构

*   `prompt.txt`: **源代码**。即输入给 LLM 的系统提示词 (System Prompt)。
*   `cases.yaml`: **测试套件**。一个包含“输入 / 期望输出”键值对的黄金数据集 (Golden Dataset)。
*   `tuner.py`: **测试运行器**。一个 Python 脚本，负责调用 LLM API (Gemini/OpenAI) 并对照测试套件验证提示词的表现。
*   `CHANGELOG.md`: 提示词逻辑的版本演进历史。
*   `.env`: API 密钥和 Provider 配置。

## 🚀 快速开始

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **先做本地检查（不打 API）**:
    ```bash
    python tuner.py --check
    ```
3.  **运行回归测试**:
    ```bash
    python tuner.py
    ```
    *   **✅ 通过 (PASS)**: 输出全绿。说明提示词状态稳定。
    *   **⚠️ 失败 (FAIL)**: `Actual` (实际输出) 与 `Expected` (期望输出) 不一致。脚本会打印出 `Raw Actual` (原始实际输出)，方便你复制并更新用例。

## 🔄 迭代工作流 ("TDD" 循环)

当你发现 AI 表现不符合预期（例如：漏了 Tag，格式错误）时：

1.  **捕获失败案例**:
    *   将有问题的“输入”和你心中*理想的*“期望输出”添加到 `cases.yaml` 文件中（可以放在 `# New Regression Case` 注释下）。
2.  **运行测试 (变红)**:
    *   运行 `python tuner.py`。确认测试失败（显示红色或黄色警告）。
3.  **优化提示词**:
    *   修改 `prompt.txt`。增加规则、调整指令顺序或优化示例。
4.  **运行测试 (变绿)**:
    *   再次运行 `python tuner.py`。
    *   重复步骤 3，直到 *所有* 用例都通过（全绿）。
5.  **提交版本**:
    *   在 `CHANGELOG.md` 中记录新版本号和变更内容。

---

## 🤖 如何指令 Agent (恢复会话)

如果你开启了一个新的对话会话来继续这项工作，请直接复制粘贴以下指令给 Agent。这能让它立刻获取所有必要的上下文。

> **"我正在 `/tasks/prompt-tuner` 目录下进行 Prompt 调优工作。请你：**
>
> 1.  **读取核心文件**：请先阅读 `prompt.txt` (当前逻辑), `cases.yaml` (测试集), 和 `tuner.py` (测试脚本)。
> 2.  **检查当前状态**：运行一下 `python tuner.py`，确认当前的 Golden Dataset 是全绿通过的。
> 3.  **接收新任务**：我有一个新的 Case 处理得不好，或者我想修改某条规则。
>
> **这是我要解决的新 Input / Expected Output：**
> [在此处粘贴你的 Input/Output]"

---

## ⚙️ 配置

复制 `.env.example` 为 `.env` 后，编辑服务商配置：
```ini
# PROVIDER=gemini
PROVIDER=openai
OPENAI_MODEL=gpt-4o
# GEMINI_MODEL=gemini-1.5-flash
```
