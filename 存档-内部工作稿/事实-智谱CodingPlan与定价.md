# 事实记录：智谱 Coding Plan 文档 + Pricing 页面

- 提取时间：2026-08-27
- 提取方式：webfetch（markdown / text / html）
- 约束遵守：只陈述页面原文事实，未出现的字段一律写"页面未出现"，不推测、不补全。

## 读取状态

| 链接 | 格式 | 结果 |
| --- | --- | --- |
| https://docs.bigmodel.cn/cn/coding-plan/overview | markdown | 成功，内容完整读取 |
| https://bigmodel.cn/pricing | markdown | 失败：JS 渲染空白页，页面文字为"We're sorry but 智谱丨BigModel 平台 doesn't work properly without JavaScript enabled. Please enable it to continue." |
| https://bigmodel.cn/pricing | text | 失败：仅返回页面标题"智谱丨BigModel 平台"，无任何内容数据 |
| https://bigmodel.cn/pricing | html | 失败：仅返回 SPA 加载骨架（`<div id="app">` 内只有一个 loading.gif 占位），无定价数据 |

## 提取字段表

### 一、文档页：Coding Plan 概览

来源 URL：https://docs.bigmodel.cn/cn/coding-plan/overview

| 字段 | 值 | 原文出处 URL |
| --- | --- | --- |
| 套餐级别 | Lite 套餐、Pro 套餐、Max 套餐 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Lite 5 小时积分 | 2,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Lite 每周积分 | 10,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Pro 5 小时积分 | 12,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Pro 每周积分 | 60,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Max 5 小时积分 | 28,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| Max 每周积分 | 140,000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 每 5 小时中"每分钟"额度 | 页面未出现 | — |
| 每月积分额度 | 页面未出现（页面为"每 5 小时积分 + 每周积分"两级） | — |
| 套餐价格（元/月） | 页面未出现 | — |
| 可用模型 | 所有套餐均支持 GLM-5.3、GLM-5.3-Flash | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 历史模型切换规则 | 调用历史模型 GLM-5.2、GLM-5.1 都将自动切换至 GLM-5.3；调用 GLM-5-Turbo、GLM-4.7 将自动切换至 GLM-5.3-Flash | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 适用工具 | 套餐仅限在官方支持的"指定工具与产品环境"中使用；在除规定工具外调用 API，不可享用 Coding 套餐的额度；套餐支持 OpenClaw 使用，但采用次级调度与尽力交付策略 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 额度耗尽规则 | 当套餐额度耗尽后，需要等待下一个 5 小时周期恢复额度，系统不会继续消耗您的其他资源包/账户余额 | https://docs.bigmodel.cn/cn/coding-plan/overview |

#### 积分额度与抵扣系数

| 字段 | 值 | 原文出处 URL |
| --- | --- | --- |
| 积分消耗公式（页面原文） | 模型消耗积分数=（输入 Token × Input 抵扣系数 + 缓存命中 Token × Cached Input 抵扣系数 + 输出 Token × Output 抵扣系数） / 10000 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| MCP 积分公式（页面原文） | MCP 消耗积分数=调用次数 × Output 抵扣系数 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3 Input 抵扣系数 | 6.9 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3 Cached Input 抵扣系数 | 1.7 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3 Output 抵扣系数 | 24 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3-Flash（含视觉理解 MCP） Input 抵扣系数 | 2.3 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3-Flash（含视觉理解 MCP） Cached Input 抵扣系数 | 0.56 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| GLM-5.3-Flash（含视觉理解 MCP） Output 抵扣系数 | 8 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| MCP 工具"联网搜索" Output 抵扣系数 | 1.2 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| MCP 工具"网页读取" Output 抵扣系数 | 1.2 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| MCP 工具"开源仓库" Output 抵扣系数 | 1.2 | https://docs.bigmodel.cn/cn/coding-plan/overview |

#### 高峰/非高峰定义与折扣

| 字段 | 值 | 原文出处 URL |
| --- | --- | --- |
| 高峰时段定义（页面原文） | 高峰时段：每周一至周五的 14:00～18:00（UTC+8） | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 非高峰折扣规则（页面原文） | 非高峰时段内，模型调用按基础积分消耗的 50% 抵扣 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 区间说明（页面原文） | 最多 Tokens：全部在非高峰时段，按 0.5 倍积分消耗；最少 Tokens：全部在高峰时段，按 1 倍积分消耗 | https://docs.bigmodel.cn/cn/coding-plan/overview |
| 优惠声明 | 当充分利用非高峰时段优惠时，相较于按量调用 GLM-5.3 标准 API，最高可节省 92% 成本 | https://docs.bigmodel.cn/cn/coding-plan/overview |

#### 可用额度参考表（页面原文数字）

| 缓存命中率 | 模型 | Lite（亿 Tokens/周） | Pro（亿 Tokens/周） | Max（亿 Tokens/周） |
| --- | --- | --- | --- | --- |
| 95% | GLM-5.3 | 0.48～0.97 | 2.90～5.80 | 6.76～13.52 |
| 95% | GLM-5.3-Flash | 1.46～2.92 | 8.77～17.55 | 20.47～40.95 |
| 96% | GLM-5.3 | 0.50～0.99 | 2.97～5.95 | 6.94～13.87 |
| 96% | GLM-5.3-Flash | 1.50～3.00 | 9.00～18.01 | 21.01～42.02 |
| 98% | GLM-5.3 | 0.52～1.04 | 3.13～6.27 | 7.31～14.63 |
| 98% | GLM-5.3-Flash | 1.58～3.17 | 9.50～19.00 | 22.17～44.33 |

### 二、定价页：bigmodel.cn/pricing

| 字段 | 值 | 原文出处 URL |
| --- | --- | --- |
| GLM-5.3 输入单价 | 页面未出现（JS 渲染，抓取失败） | — |
| GLM-5.3 输出单价 | 页面未出现（JS 渲染，抓取失败） | — |
| GLM-5.3 缓存命中单价 | 页面未出现（JS 渲染，抓取失败） | — |
| GLM-5.3-Flash 输入单价 | 页面未出现（JS 渲染，抓取失败） | — |
| GLM-5.3-Flash 输出单价 | 页面未出现（JS 渲染，抓取失败） | — |
| GLM-5.3-Flash 缓存命中单价 | 页面未出现（JS 渲染，抓取失败） | — |
| 优惠/价格活动说明 | 页面未出现（JS 渲染，抓取失败） | — |
| Coding Plan / 套餐价格 | 页面未出现（JS 渲染，抓取失败） | — |

## 我查到的事实

以下逐条均来自页面 https://docs.bigmodel.cn/cn/coding-plan/overview 的原文。

1. GLM Coding Plan 套餐共三档：Lite 套餐、Pro 套餐、Max 套餐。
2. 积分额度为"每 5 小时 + 每周"两级：Lite 2,000/10,000；Pro 12,000/60,000；Max 28,000/140,000。
3. 5 小时积分采用动态刷新机制，积分额度在请求消耗 5 小时后刷新重置；周积分自套餐下单时起以 7 天为一个周期刷新。
4. 模型消耗积分数 =（输入 Token × Input 抵扣系数 + 缓存命中 Token × Cached Input 抵扣系数 + 输出 Token × Output 抵扣系数）/ 10000；MCP 消耗积分数 = 调用次数 × Output 抵扣系数。
5. 抵扣系数：GLM-5.3 为 Input 6.9 / Cached 1.7 / Output 24；GLM-5.3-Flash（含视觉理解 MCP）为 Input 2.3 / Cached 0.56 / Output 8；MCP 工具（联网搜索、网页读取、开源仓库）Output 均为 1.2。
6. 高峰时段：每周一至周五 14:00～18:00（UTC+8）。
7. 非高峰时段内，模型调用按基础积分消耗的 50% 抵扣。
8. 区间说明：最多 Tokens = 全部在非高峰时段，按 0.5 倍积分消耗；最少 Tokens = 全部在高峰时段，按 1 倍积分消耗。
9. 页面声明：当充分利用非高峰时段优惠时，相较于按量调用 GLM-5.3 标准 API，最高可节省 92% 成本。
10. 所有套餐均支持 GLM-5.3、GLM-5.3-Flash；调用 GLM-5.2、GLM-5.1 自动切换至 GLM-5.3，调用 GLM-5-Turbo、GLM-4.7 自动切换至 GLM-5.3-Flash。
11. 套餐仅限在官方支持的"指定工具与产品环境"中使用，规定工具外调用 API 不可享用 Coding 套餐额度；套餐支持 OpenClaw 但采用次级调度与尽力交付策略。
12. 额度耗尽后需等待下一个 5 小时周期恢复，系统不会继续消耗其他资源包/账户余额。
13. 页面提供"可用额度参考表"（缓存命中率 95%/96%/98% 下的每周 Token 区间），详见上方字段表，数字为页面原文。

## 无法确认项

- bigmodel.cn/pricing 全部字段（各模型输入/输出/缓存命中单价、优惠活动、Coding Plan 套餐价格）：该页为纯 JS 渲染 SPA，webfetch 的 markdown/text/html 三种格式均只能拿到加载骨架与标题，拿不到任何定价数据。
- 每月积分额度、每分钟额度："每 5 小时 + 每周"两级之外未出现月度字段。
- 套餐具体售价（元/月或元/年）：不在 overview 文档页原文中。