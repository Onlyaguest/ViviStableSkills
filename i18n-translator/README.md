# i18n-kit - AI-Powered Multi-Language Translation

一个"工程无关"的国际化工具：自动提取中文文案、AI 翻译多语言、生成多语言版本。

## ✨ 支持的语言

- 🇺🇸 English (en-US)
- 🇯🇵 Japanese (ja-JP)
- 🇰🇷 Korean (ko-KR)
- 🇪🇸 Spanish (es-ES)
- 🇫🇷 French (fr-FR)
- 🇩🇪 German (de-DE)

## 🚀 快速开始

### 方案 1：翻译到所有语言（推荐）

```bash
# 设置 API key
export GEMINI_API_KEY="your-api-key"

# 一键翻译到所有语言
./translate-all.sh /path/to/your-project

# 完成！生成 6 个语言版本：
# - /path/to/your-project__all-langs__en-US
# - /path/to/your-project__all-langs__ja-JP
# - /path/to/your-project__all-langs__ko-KR
# - /path/to/your-project__all-langs__es-ES
# - /path/to/your-project__all-langs__fr-FR
# - /path/to/your-project__all-langs__de-DE
```

### 方案 2：选择特定语言

```bash
# 只翻译英文和日文
./auto-translate.sh /path/to/project "en-US,ja-JP"

# 只翻译英文
./auto-translate.sh /path/to/project "en-US"

# 英日韩三语
./auto-translate.sh /path/to/project "en-US,ja-JP,ko-KR"
```

### 方案 3：分步执行（高级）

```bash
# Step 1: 提取中文文案
python3 main.py extract --root /path/to/project --lang zh-CN --write

# Step 2: 翻译到多语言
python3 translate.py --root /path/to/project --targets "en-US,ja-JP,ko-KR"

# Step 3: 生成各语言版本
python3 main.py apply --root /path/to/project --lang en-US --out-dir /path/to/project__en
python3 main.py apply --root /path/to/project --lang ja-JP --out-dir /path/to/project__ja
python3 main.py apply --root /path/to/project --lang ko-KR --out-dir /path/to/project__ko
```

## 📋 使用场景

### 1. 单个 HTML 报告 → 多语言版本

```bash
# 生成英日韩三语版本
./auto-translate.sh ~/reports/dashboard.html "en-US,ja-JP,ko-KR"

# 为每个版本添加语言切换器
python3 main.py embed-switch \
  --html ~/reports/dashboard.html__multilang__en-US/dashboard.html \
  --root ~/reports/dashboard.html \
  --langs zh-CN,en-US,ja-JP,ko-KR
```

### 2. 整个网站 → 全语言版本

```bash
# 翻译到所有支持的语言
./translate-all.sh ~/my-website

# 结果：
# ~/my-website__all-langs__en-US/  (英文版)
# ~/my-website__all-langs__ja-JP/  (日文版)
# ~/my-website__all-langs__ko-KR/  (韩文版)
# ~/my-website__all-langs__es-ES/  (西班牙文版)
# ~/my-website__all-langs__fr-FR/  (法文版)
# ~/my-website__all-langs__de-DE/  (德文版)
```

### 3. 只翻译新增内容（增量更新）

```bash
# 第一次：翻译所有内容
./auto-translate.sh ~/project "en-US,ja-JP"

# 修改了中文内容后，再次运行
./auto-translate.sh ~/project "en-US,ja-JP"
# → 只翻译新增/修改的部分！
```

## 🔧 命令参考

### translate.py - AI 翻译核心

```bash
# 翻译到单个语言
python3 translate.py --root <dir> --target en-US

# 翻译到多个语言
python3 translate.py --root <dir> --targets "en-US,ja-JP,ko-KR"

# 翻译到所有支持的语言
python3 translate.py --root <dir>

# 列出支持的语言
python3 translate.py --list-languages

# 预览不写入
python3 translate.py --root <dir> --targets "en-US,ja-JP" --dry-run

# 自定义批量大小
python3 translate.py --root <dir> --targets "en-US,ja-JP" --batch-size 10
```

### auto-translate.sh - 一键脚本

```bash
# 基本用法
./auto-translate.sh <input> [languages] [output-dir]

# 示例
./auto-translate.sh ~/project                           # 默认：英日韩
./auto-translate.sh ~/project "en-US"                   # 只翻译英文
./auto-translate.sh ~/project "en-US,ja-JP"             # 英日双语
./auto-translate.sh ~/project "en-US,ja-JP" ~/output    # 自定义输出目录
```

### translate-all.sh - 全语言翻译

```bash
# 翻译到所有 6 种语言
./translate-all.sh <input> [output-dir]

# 示例
./translate-all.sh ~/project                  # 输出到 ~/project__all-langs__*
./translate-all.sh ~/project ~/translations   # 自定义输出目录
```

## 🎯 工作流程

```
1. Extract (提取)
   ├─ 扫描文件，找到中文文案
   ├─ 替换为 token: __I18N__key__
   └─ 生成 i18n/zh-CN.json

2. Translate (翻译)
   ├─ 读取 zh-CN.json
   ├─ 调用 Gemini API 批量翻译
   ├─ 生成 i18n/en-US.json
   ├─ 生成 i18n/ja-JP.json
   └─ 生成 i18n/ko-KR.json ...

3. Apply (应用)
   ├─ 读取目标语言字典
   ├─ 替换 token 为翻译文本
   └─ 输出到目标目录
```

## 💡 高级功能

### 1. 离线语言切换器

为单个 HTML 文件添加右上角语言切换按钮：

```bash
python3 main.py embed-switch \
  --html ~/output/report.html \
  --root ~/output \
  --langs zh-CN,en-US,ja-JP,ko-KR
```

打开 HTML 后可以在浏览器中切换语言，无需服务器！

### 2. 增量翻译

只翻译新增或修改的内容：

```bash
# 第一次运行：翻译所有内容
python3 translate.py --root ~/project --targets "en-US,ja-JP"

# 修改了中文内容后
python3 translate.py --root ~/project --targets "en-US,ja-JP"
# → 自动检测，只翻译新增的！
```

### 3. 自定义语言

虽然内置了 6 种语言，但你可以翻译到任何语言：

```bash
# 翻译到泰语
python3 translate.py --root ~/project --target th-TH

# 翻译到越南语
python3 translate.py --root ~/project --target vi-VN
```

### 4. 批量大小调整

如果遇到 API 限制，可以减小批量大小：

```bash
python3 translate.py --root ~/project --targets "en-US,ja-JP" --batch-size 10
```

## 📦 安装

```bash
cd ~/MyTools/tasks/i18n-kit

# 基础依赖
pip install -r requirements.txt

# AI 翻译依赖
pip install google-generativeai
```

## 🔑 环境变量

```bash
# Gemini API key（必需）
export GEMINI_API_KEY="your-api-key"

# 或者写入 .env 文件
echo 'GEMINI_API_KEY=your-api-key' > .env
```

## 🎨 实际案例

### 案例 1：技术文档多语言化

```bash
# 原始文档（中文）
~/docs/
├── index.html
├── guide.html
└── api.html

# 翻译到英日韩
./auto-translate.sh ~/docs "en-US,ja-JP,ko-KR"

# 结果
~/docs__multilang__en-US/  # 英文版
~/docs__multilang__ja-JP/  # 日文版
~/docs__multilang__ko-KR/  # 韩文版
```

### 案例 2：数据报告国际化

```bash
# 单个报告文件
./auto-translate.sh ~/reports/Q4-report.html "en-US,ja-JP"

# 添加语言切换器
python3 main.py embed-switch \
  --html ~/reports/Q4-report.html__multilang__en-US/Q4-report.html \
  --root ~/reports/Q4-report.html \
  --langs zh-CN,en-US,ja-JP

# 发送给国际团队
# → 他们可以在浏览器中切换语言！
```

### 案例 3：产品页面全球化

```bash
# 产品页面
~/product-page/
├── index.html
├── features.html
└── pricing.html

# 翻译到所有语言
./translate-all.sh ~/product-page

# 结果：6 个语言版本
~/product-page__all-langs__en-US/
~/product-page__all-langs__ja-JP/
~/product-page__all-langs__ko-KR/
~/product-page__all-langs__es-ES/
~/product-page__all-langs__fr-FR/
~/product-page__all-langs__de-DE/
```

## ⚠️ 注意事项

- **备份！** 使用 `--write` 前先备份或用 git
- **预览！** 先用 `--dry-run` 查看变更
- **API 限制** - Gemini 有速率限制，大量文本可能需要分批
- **翻译质量** - AI 翻译建议人工校对，特别是专业术语
- **增量更新** - 修改中文后重新运行，只翻译新增内容

## 🆚 对比其他方案

| 方案 | 优点 | 缺点 |
|------|------|------|
| **i18n-kit** | 批量、结构化、离线切换 | 需要 API key |
| Google Translate | 免费、简单 | 手动复制粘贴、无结构 |
| 人工翻译 | 质量最高 | 慢、贵 |
| react-i18next | 运行时切换 | 需要框架、复杂 |

## 🚀 性能

- **提取速度**: ~1000 文件/秒
- **翻译速度**: ~100 条/分钟（取决于 API）
- **生成速度**: ~1000 文件/秒

## 📝 文件结构

```
your-project/
├── index.html              # 原始文件（已替换为 token）
├── i18n/
│   ├── zh-CN.json         # 中文字典
│   ├── en-US.json         # 英文字典
│   ├── ja-JP.json         # 日文字典
│   └── ko-KR.json         # 韩文字典
└── ...

your-project__multilang__en-US/
├── index.html              # 英文版本
└── ...

your-project__multilang__ja-JP/
├── index.html              # 日文版本
└── ...
```

## 🔧 故障排除

### 翻译失败

```bash
# 检查 API key
echo $GEMINI_API_KEY

# 测试连接
python3 translate.py --root ~/project --target en-US --dry-run
```

### Token 未替换

```bash
# 检查字典文件
cat ~/project/i18n/en-US.json

# 重新生成
python3 main.py apply --root ~/project --lang en-US --out-dir ~/output
```

### 批量大小过大

```bash
# 减小批量大小
python3 translate.py --root ~/project --targets "en-US,ja-JP" --batch-size 10
```

### HTML 属性里的中文没有翻译

**问题：** i18n-kit 默认只提取标签内的文本，不提取 HTML 属性值。

**常见未翻译的属性：**
- `data-*` 属性（如 `data-num="第一层"`）
- `aria-label` 属性
- `title` 属性
- `placeholder` 属性

**解决方案 1：手动替换（推荐）**

```bash
# 在生成的英文版中手动替换
cd ~/project__multilang__en-US

# 替换 data-num 属性
sed -i '' 's/data-num="第一层"/data-num="Layer 1"/g' index.html
sed -i '' 's/data-num="第二层"/data-num="Layer 2"/g' index.html
sed -i '' 's/data-num="第三层"/data-num="Layer 3"/g' index.html

# 替换 aria-label 属性
sed -i '' 's/aria-label="关闭"/aria-label="Close"/g' index.html

# 替换 title 属性
sed -i '' 's/title="点击查看详情"/title="Click for details"/g' index.html
```

**解决方案 2：修改源文件（适合大量属性）**

在原始中文版中，把属性值改成 token：

```html
<!-- 原来 -->
<div data-num="第一层">

<!-- 改成 -->
<div data-num="__I18N__layer_1__">
```

然后在字典中添加翻译：

```json
{
  "layer_1": "Layer 1",
  "layer_2": "Layer 2",
  "layer_3": "Layer 3"
}
```

重新运行提取和翻译：

```bash
python3 main.py extract --root ~/project --lang zh-CN --write
python3 translate.py --root ~/project --targets "en-US,ja-JP,ko-KR"
python3 main.py apply --root ~/project --lang en-US --out-dir ~/output
```

**最佳实践：**
- 对于少量属性（<10 个），使用方案 1（手动替换）
- 对于大量属性（>10 个），使用方案 2（修改源文件）
- 在翻译前检查 HTML 中是否有需要翻译的属性

## 📚 更多资源

- [Gemini API 文档](https://ai.google.dev/docs)
- [i18n 最佳实践](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Internationalization)

## License

MIT
