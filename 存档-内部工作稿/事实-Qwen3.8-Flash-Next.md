# 事实记录：Qwen3.8-Flash-Next（来源：HF 模型卡 + Qwen 官方博客）

> 本子代理任务产出。截止 2026-08-27 读取，只记录页面实际写着的文字，禁止推测/补全。技术术语与模型名保留原文。

## 读取状态

| 链接 | 状态 | 说明 |
| --- | --- | --- |
| https://huggingface.co/Qwen/Qwen3.8-Flash-Next | 成功 | webfetch format=markdown，返回完整模型卡正文 |
| https://qwen.ai/blog?id=qwen3.8-flash-next | 失败（JS 空页） | 两次请求均只返回 "Qwen" 二字，未见任何正文内容，判定为客户端渲染（SPA）页面，webfetch 无法取到内容 |

## 提取字段表

字段 | 值 | 原文出处 URL | 原文引用
--- | --- | --- | ---
模型全名 | Qwen3.8-Flash-Next | HF 模型卡 | 标题已返回就是这个
模型类型 | Causal Language Model with Vision Encoder | HF 模型卡 | `Type: Causal Language Model with Vision Encoder`
训练阶段 | Pre-training & Post-training | HF 模型卡 | `Training Stage: Pre-training & Post-training`
总参数量 | 125B | HF 模型卡 | `Number of Parameters: 125B with 6B activated, plus 51B n-gram embedding and 4B MTP`
激活参数量 | 6B | HF 模型卡 | 同上
附带的 n-gram 嵌入参数 | 51B | HF 模型卡 | `plus 51B n-gram embedding and 4B MTP`
附带的 MTP 参数 | 4B | HF 模型卡 | 同上
n-gram 嵌入规模明细 | 20,000,000（bigrams/trigrams at layer 2） | HF 模型卡 | `N-gram Embedding: 20,000,000 (bigrams/trigrams at layer 2)`
FFn 维度（原文写 Hidden Dimension） | 2560 | HF 模型卡 | `Hidden Dimension: 2560`
Token Embedding | 248320（Padded） | HF 模型卡 | `Token Embedding: 248320 (Padded)`
层数 | 48 | HF 模型卡 | `Number of Layers: 48`
每层结构（Hidden Layout，Gated DeltaNet/MoE 保留原词） | 12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE)) | HF 模型卡 | `Hidden Layout: 12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE))`
Gated DeltaNet 线性注意力头数 | V 用 48、QK 用 16 | HF 模型卡 | `Gated DeltaNet: Number of Linear Attention Heads: 48 for V and 16 for QK`
Gated DeltaNet 头维 | 128 | HF 模型卡 | `Head Dimension: 128`
QSA 注意力头数 | Q 用 24、KV 用 2 | HF 模型卡 | `Qwen Sparse Attention: Number of Attention Heads: 24 for Q and 2 for KV`
QSA 头维 | 256 | HF 模型卡 | `Head Dimension: 256`
QSA RoPE 维度 | Rotary Position Embedding Dimension: 64 | HF 模型卡 | `Rotary Position Embedding Dimension: 64`
QSA Indexer 结构 | MQA with 4 Query Heads and 1 Shared Key Head | HF 模型卡 | `Indexer Structure: MQA with 4 Query Heads and 1 Shared Key Head`
QSA Indexer 头维 | 128 | HF 模型卡 | `Indexer Head Dimension: 128`
QSA Budget | 512 blocks or 2048 tokens | HF 模型卡 | `Budget: 512 blocks or 2048 tokens`
MoE 专家数 | 512 | HF 模型卡 | `Mixture Of Experts: Number of Experts: 512`
MoE 激活专家数 | 10 Routed + 1 Shared | HF 模型卡 | `Number of Activated Experts: 10 Routed + 1 Shared`
MoE 专家中间维度 | 640 | HF 模型卡 | `Expert Intermediate Dimension: 640`
Gated Residual 分支 | 4 branches，bottleneck rank 320 | HF 模型卡 | `Gated Residual: Number of Branches: 4, Bottleneck Rank: 320`
LM Output | 248320（Padded） | HF 模型卡 | `LM Output: 248320 (Padded)`
MTP 结构 | 1 layer, trained with multi-steps | HF 模型卡 | `MTP: 1 layer, trained with multi-steps`
原生上下文长度 | 262,144 原生，可扩展到 1,000,000 tokens | HF 模型卡 | `Context Length: 262,144 natively and extensible up to 1,000,000 tokens.`
1M token 的实现附加信息（静态 YaRN、factor=4.0） | 提到 `rope_type: "yarn"`、`factor: 4.0`、`original_max_position_embeddings: 262144`、多框架示例命令均传 `--max-model-len 1000000` / `--context-length 1000000` | HF 模型卡 | "Qwen3.8-Flash-Next natively supports context lengths of up to 262,144 tokens. For long-horizon tasks where the total length (including both input and output) exceeds this limit, we recommend using RoPE scaling techniques to handle long texts effectively, e.g., YaRN."；同时注明 "All the notable open-source frameworks implement static YaRN, which means the scaling factor remains constant regardless of input length, potentially impacting performance on shorter texts."
KV Cache 压缩/省内存相关 | 原文没有出现 KV 大小/压缩率数字；只出现两处间接表述：(1) preserved thinking "It also improves KV cache utilization, optimizing inference efficiency in both thinking and non-thinking modes."；(2) n-gram 嵌入说明 "makes parameter scaling highly efficient for memory-constrained accelerators without sacrificing quality" | HF 模型卡 | 见邻列引用
推荐推理框架 | Transformers、vLLM、SGLang、TokenSpeed、KTransformers、Docker Model Runner；下载页另有 llama.cpp/Ollama/LM Studio 量化可用 | HF 模型卡 | "we recommend using the latest framework versions"；"dedicated serving engines such as SGLang, KTransformers or vLLM are strongly recommended"；Quickstart 下列出 SGLang / vLLM / TokenSpeed 三个 cookbook/recipe 链接
部署/内存/硬件建议 | (1) 生产/高吞吐场景强烈推荐 SGLang、KTransformers、vLLM；(2) 视频超长理解建议把 video_preprocessor 的 longest_edge 设为 469,762,048（对应 224k video tokens）以支持小时级视频更高帧率；(3) 只建议确实需要长上下文才改 rope_parameters，且建议按典型长度调 factor（如 524,288 时 factor 取 2.0） | HF 模型卡 | "For production workloads or high-throughput scenarios, dedicated serving engines such as SGLang, KTransformers or vLLM are strongly recommended."
HF 页面标注的模型大小 | 180B params | HF 模型卡 | HF 侧边栏 "Model size: 180B params"；Tensor type: BF16 · I64
推荐采样参数（thinking / non-thinking） | Thinking: temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0；Instruct: temperature=0.7, top_p=0.80, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0 | HF 模型卡 | 见 "Best Practices" 第 1 节
输出长度建议 | Reasoning Content 上限 262,144 tokens；Final Response 上限 131,072 tokens（均在 1M 上下文内） | HF 模型卡 | "Reasoning Content: Set the maximum output length to 262,144 tokens. Final Response: Set the maximum output length to 131,072 tokens."
思考模式细节 | 默认 thinking mode，通过 enable_thinking / preserve_thinking / reasoning_effort 控制；reasoning_effort 支持 xhigh（默认）、medium、low | HF 模型卡 | "Qwen3.8-Flash-Next models operate in thinking mode by default"；"reasoning_effort=xhigh,  # xhigh by default; supported levels are xhigh, medium, and low"
浏览器侧看到的社区信息 | HF 页显示 this model isn't deployed by any Inference Provider；另有 64 quantized models、14 finetunes、3 Spaces | HF 模型卡 | HF UI 侧栏

## Benchmark 分数（来自 HF 模型卡 Language / Vision Language 两表，全部为页面实际给出）

### 语言 benchmark 表（列：Qwen3.8-Flash-Next 自身分数）

| 分类 | Benchmark | 分数 |
| --- | --- | --- |
| Agentic coding | DeepSWE 1.1 | 58.7 |
| Agentic coding | SWE-bench Pro | 62.5 |
| Multilingual software engineering | SWE-bench Multilingual | 81.0 |
| Repo-level code generation | NL2Repo-Bench | 48.1 |
| Long-horizon office work | CoWorkBench | 73.9 |
| Professional job tasks | JobBench | 55.7 |
| Frontier agentic tasks | Agents' Last Exam | Pass@1 24.3 / Score 51.2 |
| Real-world tool use | Toolathlon Verified (Pass@1) | 73.5 |
| Instruction following | IFBench | 81.3 |
| Scientific reasoning | GPQA Diamond | 91.7 |
| Multidisciplinary reasoning | HLE | 35.9 |
| Competitive coding | LiveCodeBench v6 | 91.9 |

footnote 关键信息：DeepSWE 1.1 用 Claude Code 和 mini-SWE-agent 两种 harness、temp=1.0、top_p=0.95、256K context window 评测，报告两者较高分，Qwen3.8-Flash-Next 在 mini-SWE-agent 上表现最好；HLE 由 GPT-4o 判分；每行最优加粗。

### 视觉语言 benchmark 表

| 分类 | Benchmark | 分数 |
| --- | --- | --- |
| Multimodal tool use | ClawEval-MM | Pass@3: 64.4 / Average: 60.4 |
| Application recreation | RecreationBench | 49.9 |
| Mobile use | AndroidWorld | 84.5 |
| Computer use | OSWorld 2.0 | Binary: 19.4 / Partial: 52.3 |
| Visual web development | Vision2Web | 64.0 |
| Embodied intelligence | ERQA | 72.3 |
| Long video understanding | LVBench | 76.6 |
| Real-world perception | RealWorldQA | 88.5 |
| Visual math problem solving | MathVision | Without CI: 90.6 / With CI: 95.7 |
| Scientific chart analysis | CharXiv (RQ) | Without CI: 84.6 / With CI: 90.6 |

footnote 关键信息：ClawEval-MM 报告格式 "pass@3 / average score"；OSWorld 2.0 报告二进制/部分奖励；MathVision、CharXiv 报告 "without CI / with CI"。

## 我查到的事实（逐条，均能在 HF 模型卡正文找到对应文字）

1. Qwen3.8-Flash-Next 是 Qwen 团队第一个开放权重发布的 "experimental preview of the architecture that will underpin Qwen4"。
2. 总参数量 125B，激活参数量 6B，另有 51B n-gram embedding 参数和 4B MTP 参数。
3. 层数 48；hidden layout 是 `12 × (3 × (Gated DeltaNet → MoE) → 1 × (Qwen Sparse Attention → MoE))`——Gated DeltaNet 和 MoE 出现频率高于 Qwen Sparse Attention。
4. 注意力结构：Gated DeltaNet 线性注意力 V 头 48、QK 头 16、头维 128；QSA 的 Q 头 24、KV 头 2、头维 256、RoPE dim 64、indexer 为 MQA（4 Q 头 + 1 共享 K 头，头维 128）、预算 512 blocks or 2048 tokens。
5. 上下文：原生 262,144 tokens，可扩展到 1,000,000 tokens（原文 "Context Length: 262,144 natively and extensible up to 1,000,000 tokens."）。
6. 1M 需借助 RoPE scaling（推荐 YaRN，多框架示例：vLLM/SGLang/TokenSpeed 分别用 `--max-model-len 1000000` / `--context-length 1000000` 启动，config 涉及 `rope_type: "yarn"`、`factor: 4.0`、`original_max_position_embeddings: 262144`）；页面明确提醒 open-source 框架实现的都是静态 YaRN，缩放因子恒定，可能影响短文本性能，且建议按实际典型长度调 factor。
7. MoE：512 专家，激活 10 Routed + 1 Shared，专家中间维度 640。
8. Gated Residual：4 branches，bottleneck rank 320。
9. KV Cache 相关：页面没有给出任何 KV 大小数字或压缩率；仅两处间接提到——preserved thinking 功能说明 "It also improves KV cache utilization, optimizing inference efficiency in both thinking and non-thinking modes."，以及 n-gram 嵌入描述 "makes parameter scaling highly efficient for memory-constrained accelerators without sacrificing quality"（这句是针对参数扩展/可 offload，原文未直接写"KV 省内存"）。
10. 推荐推理框架：SGLang、vLLM、TokenSpeed 各有官方 cookbook/recipe 链接；生产/高吞吐场景原文点名 "SGLang, KTransformers or vLLM are strongly recommended"；兼容列表还提到 Transformers、Docker Model Runner，以及 llama.cpp/Ollama/LM Studio 等量化生态。
11. 模型卡明确说明存在一个官方衍生版本：Qwen3.8-Flash（基于 Qwen3.8-Flash-Next，默认 1M context length、内置官方工具，由 Qwen Cloud 提供）。
12. Benchmark：语言侧含 DeepSWE 1.1（58.7）、SWE-bench Pro（62.5）、SWE-bench Multilingual（81.0）、GPQA Diamond（91.7）、HLE（35.9）、LiveCodeBench v6（91.9）等；视觉侧含 ClawEval-MM（Pass@3 64.4 / Avg 60.4）、AndroidWorld（84.5）、MathVision（With CI 95.7）等（详见上表）。
13. 采样与输出建议：thinking 模式 temp=1.0/top_p=0.95/top_k=20；非 thinking 模式 temp=0.7/top_p=0.80/presence_penalty=1.5；reasoning content 上限 262,144 tokens、最终输出上限 131,072 tokens（在 1M 上下文内）。
14. 引用信息（citation 区块）：technical report 标题 "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"，发布时间标注 2026 年 8 月，Alibaba Group；博客标题 "Qwen3.8-Flash-Next: A New Architecture, Towards Ultimate Cost-Efficiency"，2026 年 8 月。技术报告 PDF 链接在 https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf（模型卡页面给出，未实际打开验证内容）。
15. HF 接口页显示的模型文件元数据："Model size 180B params"、Tensor type "BF16 · I64"（这两个数字页面与 125B+51B+4B 并存，页面未做解释）。

## 无法确认项（链接打不开或页面没有的字段）

- Qwen 官方博客 https://qwen.ai/blog?id=qwen3.8-flash-next 完全打不开（JS 空页，正文无法提取）。博客正文里的任何额外事实（若与模型卡不重复）均无法确认。
- KV Cache 是否"小/压缩/省内存"的任何具体数字：两个来源均未出现量化表述，只有上述两处间接文字，无法进一步确认。
- 部署所需的显存/内存具体数字：页面未出现任何显存占用建议数字。
- 页面没有给出参数明细与 180B params 标签之间差异的官方解释。
- DeepSWE、HLE 等分数以外的评测 harness 细节：footnote 有标注，但仅限模型卡列出的信息；博客若另有信息不可得。