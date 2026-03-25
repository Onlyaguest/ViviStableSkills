---
name: 前端美学指南
emoji: 🎨
version: 1.0
type: meta
author: Vivi
created: 2026-03-02
tags: [frontend, design, aesthetics, anti-slop]
related_skills: []

# Meta 特有字段
stackable: true
priority: high

description: 避免平庸的"AI slop"美学，创造令人惊喜的独特前端
---

# 🎨 前端美学指南

## [Core Mission - 核心使命]

避免平庸的"AI slop"美学，创造令人惊喜的独特前端。

**什么是 AI slop？**
- Inter/Roboto 字体
- 紫色渐变 + 白色背景
- 千篇一律的布局
- 平庸的设计选择

**我们追求什么？**
- 独特、有性格的设计
- 令人难忘的视觉体验
- 真正的创意和惊喜

---

## [Five Core Dimensions - 五大核心维度]

### 1. 排版 Typography

**❌ 禁止：**
- Inter
- Roboto
- Arial
- 系统字体

**✅ 选择：**
- 独特、有性格的字体
- 展示字体 + 正文字体，高对比度

**✅ 技巧：**
- 字重极端对比（100 vs 900）
- 字号大跨度（3x+）

**示例：**
```css
/* ❌ 平庸 */
font-family: 'Inter', sans-serif;
font-weight: 400;
font-size: 16px;

/* ✅ 独特 */
font-family: 'Space Grotesk', 'JetBrains Mono', monospace;
font-weight: 900; /* 标题 */
font-size: 48px;

font-weight: 100; /* 正文 */
font-size: 14px;
```

---

### 2. 色彩 Color & Theme

**✅ 统一审美：**
- 用 CSS 变量维护
- 主导色 + 鲜明点缀色

**❌ 避免：**
- 紫色渐变 + 白色背景
- 千篇一律的配色

**✅ 灵感来源：**
- IDE 主题（VS Code Dark+, Dracula, Nord）
- 文化美学（赛博朋克、蒸汽波、新野兽派）

**示例：**
```css
/* ❌ 平庸 */
:root {
  --primary: #8B5CF6; /* 紫色 */
  --background: #FFFFFF;
}

/* ✅ 独特 - 赛博朋克 */
:root {
  --primary: #00FF41; /* 矩阵绿 */
  --accent: #FF006E; /* 荧光粉 */
  --background: #0A0E27; /* 深蓝黑 */
  --text: #E0E0E0;
}

/* ✅ 独特 - 蒸汽波 */
:root {
  --primary: #FF71CE; /* 粉色 */
  --accent: #01CDFE; /* 青色 */
  --background: #B967FF; /* 紫色 */
  --text: #FFFB96; /* 黄色 */
}
```

---

### 3. 动效 Motion

**✅ CSS 动画优先（HTML）**
- 性能更好
- 更容易维护

**✅ Motion 库：**
- Framer Motion
- GSAP
- Anime.js

**✅ 聚焦高影响力：**
- 一次精心编排的页面加载 > 散乱的微交互
- 滚动触发
- 悬停惊喜

**示例：**
```css
/* ✅ 精心编排的页面加载 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero h1 {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s backwards;
}

.hero p {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s backwards;
}

/* ✅ 悬停惊喜 */
.card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card:hover {
  transform: scale(1.05) rotate(2deg);
}
```

---

### 4. 空间布局 Spatial

**✅ 打破常规：**
- 非对称
- 重叠
- 对角线流动

**✅ 大胆选择：**
- 打破网格
- 大胆留白 OR 受控密集

**示例：**
```css
/* ❌ 平庸的网格 */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* ✅ 非对称布局 */
.grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  gap: 40px 20px;
}

.grid .featured {
  grid-column: span 2;
  grid-row: span 2;
}

/* ✅ 对角线流动 */
.diagonal-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  transform: rotate(-5deg);
}

.diagonal-layout > * {
  transform: rotate(5deg);
}
```

---

### 5. 背景细节 Backgrounds

**✅ 创造氛围和深度：**
- 渐变网格
- 噪点
- 几何图案

**✅ 分层技巧：**
- 透明叠加
- 戏剧阴影
- 装饰边框

**示例：**
```css
/* ✅ 渐变网格 */
.background {
  background: 
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* ✅ 噪点纹理 */
.background::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url('data:image/svg+xml;base64,...'); /* 噪点 SVG */
  opacity: 0.05;
  mix-blend-mode: overlay;
}

/* ✅ 戏剧阴影 */
.card {
  box-shadow: 
    0 0 0 1px rgba(255,255,255,0.1),
    0 20px 60px rgba(0,0,0,0.5),
    0 0 100px rgba(255,0,110,0.3);
}
```

---

## [Key Principles - 关键原则]

### 1. 每个设计都应不同

**避免重复收敛：**
- 不要每次都用同样的配色
- 不要每次都用同样的布局
- 不要每次都用同样的字体

**追求独特性：**
- 每个项目都应该有自己的个性
- 根据内容和目标选择风格
- 敢于尝试新的组合

---

### 2. 实现复杂度匹配美学愿景

**极繁需精心设计：**
- 高密度信息需要清晰的层次
- 复杂动画需要精心编排
- 多层背景需要协调统一

**极简需克制精确：**
- 每个元素都有存在的理由
- 留白是设计的一部分
- 细节决定成败

---

### 3. 跳出思维定式

**常见陷阱：**
- "这个看起来很专业" → 可能只是很平庸
- "大家都这么做" → 正是要避免的
- "这个很安全" → 安全往往意味着无聊

**突破方法：**
- 参考其他领域（游戏、电影、艺术）
- 尝试极端选择（超大/超小、超亮/超暗）
- 混合不同风格（赛博朋克 + 新野兽派）

---

## [Quick Checklist - 快速检查清单]

在生成任何前端设计前，检查：

- [ ] **字体：** 是否避开 Inter/Roboto？是否有特色搭配？
- [ ] **色彩：** 是否有统一主题？是否避免紫色渐变？
- [ ] **动画：** 是否有精心编排的加载效果？
- [ ] **布局：** 是否突破常规网格？
- [ ] **背景：** 是否创造深度和氛围？

---

## [One-Line Essence - 一行精华版]

```
独特字体 + 大胆配色 + 精心动画 + 突破布局 + 氛围背景 = 令人难忘的前端
```

**拒绝：**
- Inter/Roboto
- 紫色渐变白底
- 千篇一律布局

---

## [Usage Tips - 使用指南]

### 何时启用这个 Meta？

✅ **适用场景：**
- 任何前端设计任务
- 生成 HTML/CSS
- 设计评审
- 风格建议

❌ **不适用场景：**
- 后端代码
- 数据处理
- 非设计相关任务

---

### 如何使用？

**启动方式：**
```
启用 前端美学指南
```

**与其他卡片组合：**
```
加载 波普风格网页生成器
启用 前端美学指南

→ 生成的 HTML 会同时遵循：
  - 波普风格的视觉规范
  - 前端美学的设计原则
  - 避免 AI slop 的陷阱
```

**禁用方式：**
```
禁用 前端美学指南
```

---

## [Examples - 风格示例]

### 赛博朋克风格

**色彩：**
- 主色：矩阵绿 (#00FF41)
- 点缀：荧光粉 (#FF006E)
- 背景：深蓝黑 (#0A0E27)

**字体：**
- 标题：Orbitron, 900
- 正文：JetBrains Mono, 300

**特效：**
- 扫描线动画
- 故障效果（glitch）
- 霓虹发光

---

### 新野兽派风格

**色彩：**
- 主色：纯黑 (#000000)
- 点缀：纯红 (#FF0000)
- 背景：纯白 (#FFFFFF)

**字体：**
- 标题：Helvetica Neue, 900
- 正文：Arial, 400

**特效：**
- 粗边框
- 大胆留白
- 极简动画

---

### 蒸汽波风格

**色彩：**
- 主色：粉色 (#FF71CE)
- 点缀：青色 (#01CDFE)
- 背景：紫色 (#B967FF)

**字体：**
- 标题：VCR OSD Mono, 700
- 正文：Courier New, 400

**特效：**
- 网格背景
- 80 年代图形
- 复古动画

---

## [Meta - 关于这个 Meta]

**设计哲学：**
1. **反 AI slop** - 拒绝平庸和千篇一律
2. **追求独特** - 每个设计都应该令人难忘
3. **系统化思考** - 五大维度全面覆盖
4. **可叠加** - 可以与任何 Role/Workflow 共存

**适用人群：**
- 前端开发者
- UI/UX 设计师
- 需要生成网页的人
- 追求独特视觉风格的人

**核心价值：**
- 把"平庸的 AI 生成"转化为"令人惊喜的独特设计"
- 把"千篇一律的模板"转化为"有个性的作品"
- 把"安全的选择"转化为"大胆的创意"

---

## [Version History]

**V1.0 (2026-03-02)**
- 初始版本
- 五大核心维度
- 快速检清单
- 风格示例
