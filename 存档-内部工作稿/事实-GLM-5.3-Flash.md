# 事实记录：GLM-5.3-Flash（来源：HF 模型卡 + z.ai 官方博客）

## 读取状态

| 链接 | 状态 |
|---|---|
| https://huggingface.co/zai-org/GLM-5.3-Flash | 成功（format=markdown 完整抓到模型卡正文、footnotes、Eval Results、模型元数据） |
| https://z.ai/blog/glm-5.3-flash | 直接 HTML 为空白（JS 渲染 SPA，`<div id="root">` 空壳，markdown/text 两次均返回空）；通过抓取页面入口 JS `/blog/assets/glm-5.3-flash-CS8pYy5F.js` **间接成功**提取到全部博客正文（React 组件内嵌文本，含正文、对比表数据、Footnotes） |

说明：z.ai 博客正文是从其 JS bundle 中内嵌的字符串提取，文字即页面渲染后展示的文字，非第三方转载。正文日期标注 `2026-08-26`，标题 `GLM-5.3-Flash: Frontier Intelligence, Flash Cost`。

## 提取字段表

| 字段 | 值 | 原文出处 URL | 原文引用词句 |
|---|---|---|---|
| 模型总参数量 | 320B（HF 元数据显示 Safetensors 合计 321B params） | https://z.ai/blog/glm-5.3-flash（Z.ai 官方博客，经 JS 提取；下称"博客"）；https://huggingface.co/zai-org/GLM-5.3-Flash（下称"HF"） | "With 320B total parameters and just 18B active parameters"; HF 卡片底部 "Model size 321B params / Tensor type BF16 · F8_E4M3 · F32" |
| 激活参数量 | 18B | 博客 / HF | "just 18B active parameters" |
| 层数 | 45（对比 GLM-4.5 系列 92 层、同样 320B vs 355B） | 博客 | "it nearly halves both the activated parameter count (18B vs. 32B) and the number of layers (45 vs. 92)" |
| 注意力头数 | 页面未出现 | — | — |
| QK 头维 / V 头维 | 页面未出现 | — | — |
| KV LoRA dim / 压缩维度 | 页面未出现（"KV LoRA"/"LoRA" 字样未出现） | — | — |
| 是否 MLA | 页面未出现 "MLA" 字样。架构关键词为 hybrid linear + sparse attention、indexer、IndexPool | 博客 / HF | "hybrid architecture combining sparse and linear attention"; "Linear attention captures local dependencies through state modeling, while sparse attention retrieves relevant global context through a lightweight indexer" |
| IndexPool（索引器 KV 压缩） | 压缩 4 个 indexer key 向量为 1 个（加权池化），作用在 1M 上下文下降低 indexer 延迟与内存 | 博客 | "we introduce IndexPool, which compresses four indexer key vectors into one through weighted pooling" |
| 注意力计算量 / KV Cache 相对压缩倍数 | 相对 GLM-5.3 分别降低 3.0x（attention compute）与 4.4x（KV cache size） | 博客 | "Compared with GLM-5.3, GLM-5.3-Flash reduces the attention compute and KV cache size by factors of 3.0x and 4.4x"；另句 "The KV cache size is still slightly larger than Kimi-K3 and DeepSeek-V4-Flash, leaving further room for improvement"（口径：per head per layer、平均每层 KV cache，BF16） |
| 上下文长度 | 支持至 1M token（多处）；并在 Chinese AI 芯片部署段写明 "context lengths of up to one million tokens" | HF / 博客 | HF footnotes: "We evaluated NL2Repo with ... and max_new_tokens=64k under 1M context"；博客 footnotes Agent's Last Exam "1M context"；博客正文 "especially when supporting context lengths of up to one million tokens" |
| 原生多模态 | 是。GLM-5 系列首个原生多模态模型（视觉；页面未提音频） | HF / 博客 | HF intro: "the first natively multimodal model in the GLM-5 series"；HF 标签含 "image-text-to-text"，示例用 `AutoProcessor` / `AutoModelForMultimodalLM`，消息含 image 输入；博客含 "Vision" 类 benchmark（OfficeQA Pro、CharXiv、Chartography、BabyVision、MVBench、MMVU） |
| 基于哪个模型 / 基础对比 | 全新训练 base model；相对 GLM-5 的架构改进；默认对比 GLM-4.5 系列与 GLM-5.3 | HF / 博客 | HF: "GLM-5.3-Flash starts from a newly trained base model"；博客: "Compared with the GLM-4.5 series, GLM-5.3-Flash is specifically designed for ultra-low-cost inference"；"Compared with GLM-5.3, ... reduces attention compute and KV cache by 3.0x / 4.4x" |
| base 模型规模对比表 | Activated: GLM-4.5-Base 32B / GLM-5-Base 40B / DeepSeek-V4-Flash-Base 13B / GLM-5.3-Flash-Base 18B；Total: 355B / 744B / 284B / 320B | 博客 | base 对比表数据 |
| base 模型 benchmark 分数 | MMLU 86.1/88.3/88.5/88.1（顺序同上，下同）；BBH 86.2/87.4/84.9/86.6；HellaSwag 87.1/88.1/85.3/87.1；LiveCodeBench-Base 28.1/34.4/29.9/37.6；SimpleQA 30/36/31.2/33.5 | 博客 | base 对比表数据；文句 "GLM-5.3-Flash-Base outperforms GLM-4.5-Base overall and remains competitive with GLM-5-Base across most benchmarks" |
| DeepSWE / DeepSWE v1.1 | 63.4（vs GLM-5.2 46.2；对比 59.3 / 58 / 69.6 / 65.3）；HF Eval Results 显示 Deep Swe 63.4* | HF / 博客 | 博客对比表 "DeepSWE (v1.1): 63.4/46.2/59.3/58/69.6/65.3"；正文 "63.4 vs. 46.2 on DeepSWE v1.1"；HF "datacurve/deep-swe 63.4 *" |
| SWE-bench Pro | 页面未出现 | — | — |
| Terminal Bench / Terminal-Bench 2.1 | 84.3（对比 81 / 83.9 / 85 / 87.4 / 85.8） | HF / 博客 | 博客 "Terminal Bench 2.1: 84.3/81/83.9/85/87.4/85.8"；HF Eval Results "Terminalbench 2 1 84.3" |
| AutomationBench | 48.8（v1.0.6；vs GLM-5.2 26.2） | HF / 博客 | 正文 "48.8 vs. 26.2 on AutomationBench"；对比表 "AutomationBench (v1.0.6): 48.8/26.2/38.8/41/37.2/52.3" |
| NL2Repo | 56.3（对比 48.9 / 57.7 / 69.7 / null / null） | 博客 | 对比表 "NL2Repo: 56.3/48.9/57.7/69.7/null/null" |
| Toolathlon Verified | 78.4（对比 59.9 / 75.9 / 76.2 / 74.9 / null） | HF / 博客 | 对比表 "Toolathlon Verified: 78.4/59.9/75.9/76.2/74.9/null" |
| Agents' Last Exam | 26.3（对比 20.4 / 27.3 / 27 / 28 / null） | HF / 博客 | 对比表 "Agents' Last Exam: 26.3/20.4/27.3/27/28/null" |
| HLE w/ Tools | 55.3（对比 54.7 / 55.1 / 57.9 / null / null）；HF Eval Results 显示 HLE 55.3* | HF / 博客 | 对比表 "HLE w/ Tools: 55.3/54.7/55.1/57.9/null/null"；HF "cais/hle 55.3 *" |
| GDPval-AA v2 | 1773（对比 1504 / 1675 / 1582 / 1571 / 1527）；由 Artificial Analysis 评估 | HF / 博客 | 对比表 "GDPval-AA v2: 1773/1504/1675/1582/1571/1527"；footnotes "Models are evaluated by Artificial Analysis" |
| Vision benchmark 分数 | OfficeQA Pro 62.4（对比 null/57.9/48.9/null/null）；CharXiv Reasoning(w/ Tools) 89.4（80.4/89.9/88/88.7）；Chartography(w/ Tools) 78（64.3/75/68/65）；BabyVision 53.4（35.1/46.8/61.6/70.9）；MVbench 77.8（69.4/67.1/75/82.2）；MMVU 80.5（72.7/67.4/75.8/82.3） | 博客 | 对比表中 "Vision" 组各组分数 |
| 推荐推理框架 / 部署建议 | HF：SGLang、vLLM、TokenSpeed、KTransformers（附 cookbook/recipes/tutorial 链接）；博客：SGLang、vLLM、TokenSpeed（"Others will be ready soon."）；z.ai 自建推理引擎基于 SGLang | HF / 博客 | HF "Serve GLM-5.3-Flash Locally" 下列出 SGLang / vLLM / TokenSpeed / KTransformers；博客 "For local deployment, GLM-5.3-Flash currently supports inference frameworks including SGLang, vLLM and TokenSpeed"、文档链接 "https://docs.z.ai/guides/llm/glm-5.3-flash" |
| 价格 | 模型卡无 API 价格表。出现一个成本数字：Artificial Analysis Intelligence Index v4.1.1 下 57 分、每 task $0.045（discounted），并称 "at one-tenth the price"（相对 GLM-5.2） | 博客 / HF | 博客 "scoring 57 at just $0.045 per task (discounted)"；HF intro "it outperforms GLM-5.2 ... at one-tenth the price" |
| HLE w/ tools 评估条件 | temperature=1.0, top_p=0.95, 最大生成 163,840 tokens, 最大上下文 300,000 tokens（context management 策略），judge 为 GPT-5.6-luna (medium) | HF / 博客 | footnotes "HLE w/ tools (full set)" 段 |
| NL2Repo 评估条件 | temperature=1.0, top_p=1.0, max_new_tokens=64k，1M context；rule-based + LLM-based judgement 防恶意行为 | HF / 博客 | footnotes "NL2Repo" 段 |
| DeepSWE 评估条件 | mini-swe-agent harness, temperature=0.95, top_p=1.0, timeout=6h, 400K context | HF / 博客 | footnotes "DeepSWE" 段 |
| Terminal-Bench 2.1 评估条件 | Claude Code 2.1.207, temperature=1.0, top_p=1, max_new_tokens=65536, 6h timeout | HF / 博客 | footnotes "Terminal-Bench 2.1" 段 |
| Agents' Last Exam 评估条件 | official evaluation protocol + Claude Code harness（reasoning effort=max, 1M context, 64K maximum output），Tool Search disabled，official ALE evaluators 评分 | HF（无细节）/ 博客（有细节） | 博客 footnotes "Agent's Last Exam" 段 |
| Toolathlon Verified 评估条件 | official evaluation service，pass@1 平均 3 次独立运行 | HF / 博客 | footnotes "Toolathlon Verified" 段 |
| AutomationBench 评估条件 | v1.0.6，含 PR #13（zapier/AutomationBench）null 类型处理修复 | HF / 博客 | footnotes "AutomationBench" 段 |
| BabyVision 评估条件 | temperature=1.0, top_p=0.95, 最大上下文 164K tokens；输入图短边 ≥1.5K 像素 | HF / 博客 | footnotes "BabyVision" 段 |
| OfficeQA Pro 评估条件 | Treasury Bulletin PDF corpus（无嵌入文本），temperature=1.0, top_p=0.95, 最大上下文 512K | 博客 | footnotes "OfficeQA Pro" 段 |
| CharXiv Reasoning / Chartography 评估条件 | temperature=1.0, top_p=0.95, 最大上下文 256K | 博客 | footnotes 段 |
| MVBench / MMVU 评估条件 | temperature=1.0, top_p=0.95, 最大上下文 256K；视频：原生支持的直接喂视频，不支持的 1fps 抽帧 | 博客 | footnotes "MVBench and MMVU" 段 |
| 训练/语料 | 最新 30T-token 多模态预训练语料 | HF / 博客 | "Together with our latest 30T-token multimodal pre-training corpus" |
| 架构其他组件 | Manifold-Constrained Hyper-Connections (mHC)；base 模型对比表中与 DeepSeek-V4-Flash-Base、GLM-4.5-Base、GLM-5-Base 并列 | HF / 博客 | "adopts Manifold-Constrained Hyper-Connections (mHC)" |
| 部署细节（博客硬件段） | 中国 AI 芯片大集群（high-bandwidth interconnect）；基于 SGLang 的专属推理引擎；内存优化手段含 compute-for-bandwidth、communication-for-bandwidth、intra-node tensor parallelism（Linear Attention 与 LM head）、ReplaySSM、W8A8 量化、hybrid INT8/FP8/BF16 cache quantization、Layer Split；EPD（Encode–Prefill–Decode）分离式架构；较同硬件初始基线端到端吞吐 3×，"per-token cost comparable to mainstream NVIDIA GPUs" | 博客 | "Serving at Scale on Chinese AI Chips" 段 |
| 产品/发布信息 | 已推送全部 GLM Coding Plan 用户，额度为 GLM-5.3 的 3x；ZCode 支持 Browser Use / Computer Use；发布前曾以 `ox-alpha` 名称匿名测试于 OpenCode 与 OpenRouter，"most popular model of the week"，"all of this traffic served on Chinese AI chips" | 博客 | "GLM-5.3-Flash gives you 3x the usable quota of GLM-5.3"；"Before release, we tested GLM-5.3-Flash anonymously as `ox-alpha` on OpenCode and OpenRouter" |
| 其他元数据 | arxiv 2602.15763（GLM-5 Technical report）；License: MIT；标签含 fp8、glm5_next、conversational、eval-results | HF | "arxiv: 2602.15763 / License: mit" 及标签栏 |
| Z.ai Code Bench v1.0 | 每 effort 级别均高于 GLM-5.2；max effort 下接近 Claude Opus 4.8（29.0 vs 29.5）；Claude Code 2.1.207 上运行 | 博客 | "at max effort nearly matches Claude Opus 4.8 (29.0 vs. 29.5)" |

## 我查到的事实（逐条，均能在页面找到对应文字）

1. GLM-5.3-Flash 是 GLM-5 系列首个原生多模态模型，总参 320B / 激活 18B；HF 模型卡显示 Safetensors 合计 321B params，权重类型 BF16 / F8_E4M3 / F32。
2. 页面明确给出的架构信息仅有：混合架构（linear attention + sparse attention）、mHC、IndexPool（4 个 indexer key 向量加权池化为 1 个）、层数 45（对比 GLM-4.5 系列的 92 层）。未出现层数外的头数/头维/KV LoRA/MLA 字样。
3. 相对 GLM-5.3，attention compute 降低 3.0x、KV cache size 降低 4.4x；KV cache 仍略大于 Kimi-K3 与 DeepSeek-V4-Flash。
4. 上下文最高支持 1M token（NL2Repo 1M context、Agent's Last Exam 1M context、芯片部署段 "context lengths of up to one million tokens"）。
5. 模型卡无 API 价格，仅出现 Artificial Analysis Intelligence Index v4.1.1 的每 task $0.045（discounted）成本，以及相对 GLM-5.2 "at one-tenth the price" 的说法。
6. 主要 benchmark 分数：Terminal Bench 2.1=84.3、DeepSWE(v1.1)=63.4、NL2Repo=56.3、Toolathlon Verified=78.4、AutomationBench(v1.0.6)=48.8、Agents' Last Exam=26.3、HLE w/ Tools=55.3、GDPval-AA v2=1773；Vision 类：OfficeQA Pro=62.4、CharXiv Reasoning(w/ Tools)=89.4、Chartography(w/ Tools)=78、BabyVision=53.4、MVbench=77.8、MMVU=80.5。对比模型含 GLM-5.2、DeepSeek-V4-Vision-Exp、Opus 4.8、GPT-5.6 Terra、Gemini 3.7 Flash。
7. 各 benchmark 评估条件在 footnotes 详细列出（temperature/top_p/context 长度/harness/judge 等），HLE 用 GPT-5.6-luna (medium) 当 judge，DeepSWE 用 mini-swe-agent（400K context、6h timeout），Terminal-Bench 2.1 跑在 Claude Code 2.1.207。
8. HF 卡片标注的 Eval Results：Terminal Bench 2.1=84.3、Deep Swe=63.4*、HLE=55.3*（后两者带 *）。
9. 本地部署推荐框架：HF 列出 SGLang、vLLM、TokenSpeed、KTransformers；博客列出 SGLang、vLLM、TokenSpeed（"Others will be ready soon"）；z.ai 生产用基于 SGLang 的定制推理引擎跑在中国 AI 芯片集群上。
10. base 模型对比数据：激活参数 GLM-4.5-Base 32B / GLM-5-Base 40B / DeepSeek-V4-Flash-Base 13B / GLM-5.3-Flash-Base 18B；总参数 355B / 744B / 284B / 320B；base 评测 MMLU 86.1/88.3/88.5/88.1 等。
11. 博客正文日期 2026-08-26，标题 "GLM-5.3-Flash: Frontier Intelligence, Flash Cost"；发布前曾以代号 `ox-alpha` 匿名测试，流量全部由中国 AI 芯片承载。

## 无法确认项

- 注意力头数、QK 头维、V 头维：两页均未出现。
- KV LoRA dim / 具体压缩维度数值：页面未出现 "LoRA" 字样；仅出现 IndexPool 4→1 池化、3.0x/4.4x 相对倍数，无绝对维度数字。
- 是否 MLA：页面未出现 "MLA" 一词，无从确认。
- SWE-bench Pro：两页均未出现。
- 音频输入能力：两页均未提到音频。
- API 价格表：模型卡无价格区，唯一成本数字是第三方评价索引口径的 $0.045/task。
- DeepSWE 分数在博客对比表中标注 "(v1.1)"、在 HF Eval Results 中数据集名为 deep-swe 并带星号；两份来源的 63.4 一致。
- 上下文长度：页面只在多处提到 1M，未给单一明确"最大上下文=1M"的规格声明（按现有词句记录为"支持 1M，多处提及"）。