# 技术报告关键信息：Qwen3.8-Flash-Next

> 本文件由 PDF 阅读子代理产出。唯一信息来源：Qwen3.8-Flash-Next 官方技术报告 PDF（28 页，pypdf 全文提取，共 10.6 万字符，已逐行通读）与已有 HF 模型卡核对文档 `存档-内部工作稿\事实-Qwen3.8-Flash-Next.md`。
> 规则：每一句都是报告原文能找到的事实；报告没有的数字一律写"报告未提及"，不做推测。页码=P 数字（对应 PDF 页）。核对列中的"HF 模型卡"指上述事实文档记录的 HF 页面原文。

---

## 0. 报告概况

| 项 | 值 | 出处 |
| --- | --- | --- |
| 标题 | On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability | P1 |
| 团队 | Qwen Team（Alibaba Group），页脚日期 2026-08-26 | P1 / P28 |
| 页数 | 28 页（前 23 页正文，P24–P28 为参考文献） | P1–P28 |
| 一句话定位 | 125B 总参 / 6B 激活 / 额外 51B n-gram 嵌入（off-accelerator）的稀疏 MoE，在 14 项预训练基准上对比 397B-A17B 前辈：8 项领先、6 项最多落后 2.6 分，激活参数约 1/3、训练 token 约 1/3、训练 FLOPs 约 1/9 | P1（Abstract） |
| 四大架构组件 | ① Token mixing：GDN（Gated DeltaNet）循环层 + 每 4 层 1 层全注意力，CPT 时替换为 QSA；② Gated Residual（GR）残差加宽；③ n-gram 嵌入层（host memory 预取）；④ Muon 优化器 | P1–P3 |
| 报告未提（但 HF 卡有）的部署类信息 | 推荐硬件/显存/内存数字、KV 大小数字、内生上下文 262144、YaRN/静态缩放、MTP 4B 参数、权重精度、专家数、hidden size、层数、QSA/GDN 头数头维 | 见各节 |

---

## 1. KV Cache 事实（最优先）

**核心结论：报告全文没有给出任何 KV 缓存的 bytes/token、1M 上下文下 KV 总大小、KV 量化或 KV 压缩倍数数字。** 报告只在"机制层面"描述了 KV 的替代与压缩手段，全部列在下方。

### 1.1 GDN 的"固定大小状态"（KV 的替代机制）

| 事实 | 内容 | 出处 |
| --- | --- | --- |
| 状态形式 | GDN 把前缀压缩进固定大小的循环状态（fixed-size recurrent state），以线性成本更新，而非线性增长的 KV | P2 动机、P4 |
| 状态张量 | 每头状态 St∈R^(dk×dv)（依据式(1)–(5)，状态是 dk×dv 矩阵；报告未给实际的 dk/dv 数值） | P4 式(1)–(5) |
| head 数与头维 | 报告未提及 GDN 的 head 数/头维（HF 卡：V 用 48 头、QK 用 16 头、头维 128） | 报告未提及 |
| 状态是否翻倍 | 报告未提及状态量化；但在 GR 一节提到"residual state 支持 FP8 存储"（见 1.5） | P2 / P14 |

### 1.2 QSA 的稀疏注意力预算（每层每个 query 的 KV/计算上限）

| 事实 | 内容 | 出处 |
| --- | --- | --- |
| token 预算 K | K=2048：每个 query 最多选 2048 个 token 参与稀疏核心注意力 | P7 Implementation |
| 压缩比 r | r=4：key 按 r 个 token 组成一个微块（micro-block）做平均池化压缩 | P6–P7 |
| 可选块数 | 最多 512 个完整块（KB=ceil(K/r)=512），另加末尾不完整块的尾 token 总是包含 | P7 |
| indexer 结构 | MQA：4 个 query head + 1 个共享 key head；partial RoPE 用在每个 indexer head 的 128 维中的 64 维（与核心注意力模块的旋转维度匹配） | P6–P7 |
| 压缩后复杂度 | 索引器复杂度从 O(n²) 降至 O(n²/r)，加速比接近压缩比 r | P9 Efficiency |
| QSA 的 KV 预算定性 | 即每个 QSA 层的注意力只对固定 2048 token（512 块）做计算——**这是注意力计算的 token 预算，报告未直接把它表述为 KV 缓存大小** | P7 |

### 1.3 KV 量化 / KV 每 token 大小 / 1M 下 KV 总大小

| 项 | 报告状态 |
| --- | --- |
| QSA 或 GDN 的 KV 缓存每 token 字节数（bytes/token） | 报告未提及 |
| 1M 上下文下 KV 缓存总大小（GB 或公式） | 报告未提及 |
| KV 相对全注意力/上一代的压缩倍数（数字） | 报告未提及（见 1.4，只有 kernel 级速度倍数，不是大小倍数） |
| KV 量化（Q8 / FP8 等针对 KV 的） | 报告未提及针对 KV 的量化；报告提到的是"residual 状态"用 FP8（见 1.5） |

### 1.4 与全注意力的"压缩倍数"类数字（报告唯一给出的相关数字全是速度，非大小）

| 数字 | 含义 | 出处 |
| --- | --- | --- |
| 7.6× | 1M 上下文下 QSA 相对 dense attention（FlashInfer paged GQA）的 prefill 模块级加速 | P2、P9 Fig.6(c) |
| 4.9× | 1M 上下文下 QSA 相对 dense attention 的 decode 模块级加速（含 indexer + 稀疏核心注意力） | P2、P9 Fig.6(d) |
| 3.8× / 4.4× | 索引器 r=4 相对 r=1：prefill / decode 加速 | P9 Fig.6(a)(b) |
| 5 | 上述加速从 64K 上下文起才开始出现，随序列变长加速增大 | P9 |

**需要明示：7.6×/4.9× 是"QSA vs 同结构里的 dense full-attention 层"的 kernel 级对比，不是 QSA 模型的 KV 内存比 dense 模型小 XX 倍。** 报告没有提供 KV 内存压缩倍数的任何数字。

### 1.5 省 KV / 省内存相关机制清单

| 机制 | 事实 | 出处 |
| --- | --- | --- |
| GDN 固定状态 | 3/4 的 token-mixing 层用固定大小循环状态，没有线性 KV；每 4 层保留 1 层注意力 | P4 §2.1.1 |
| QSA 稀疏预算 | 全部注意力层（含 MTP 内的）在 CPT 后换成 QSA，每 query 注意力 token 上限固定 2048 | P7 §2.1.2 |
| indexer 压缩 | 微块级（r=4）平均池化压缩 key，索引器复杂度 O(n²)→O(n²/r) | P6、P9 |
| MTP 复用 QSA 索引 | 多步 MTP 在推测解码各步间复用 top-k 索引，省 draft 模型推理开销 | P2、P8 |
| GR residual FP8 | 残差分支状态用 FP8 存储，比 BF16 省一半字节搬运（几乎无损质量）；门控把写入值控制在窄范围 | P14 §2.2 Inference Efficiency |
| StreamLambda | **报告未提及 StreamLambda**（GDN 固定状态在机制上类似，但报告未用该名） | 报告未提及 |

---

## 2. 显存 / 硬件需求事实

**核心结论：报告全文没有任何推荐的/最低的硬件配置、显存 GB、内存 GB、内存带宽数字，也没有任何"32K/128K/256K/1M 上下文下峰值显存"的表或数字。** 与部署内存相关的唯一机制事实如下。

| 项 | 报告状态 |
| --- | --- |
| 运行本模型的推荐/最低硬件（显存 GB / 内存 GB / 带宽） | 报告未提及 |
| 32K / 128K / 256K / 1M 各上下文长度下的峰值显存 | 报告未提及 |
| n-gram 嵌入门（51B）对内存摆放的要求 | 报告只说：51B 表 held off the accelerator / prefetched from host memory，host-memory 预取与第一层计算重叠（放在 Layer 2）。**未给所需内存 GB、带宽或加载延迟数字** | P1、P2 Fig.1、P15 §2.3.1 |
| MTP 模块（HF 卡 4B）内存摆放 | 报告只描述 MTP 存在、多步推测、与 QSA 索引复用；**未给参数或内存数字** | P2、P7–P8 |
| 可 off-accel 的理由 | 嵌入表是稀疏访问 + 确定性寻址，可用可忽略的 per-token 额外 FLOP 扩容并放 off-accelerator 存储（自然延伸，正文引述 2025/2026 文献） | P15 对 Table 9 的说明 |
| 推理成本定性 | 报告只说：推理中 prefill 被"对整个上下文的注意力"主导（QSA 处理），decode 被"内存搬运"主导（GDN 固定状态 + GR 去掉 Hres + residual FP8） | P2 Efficiency |
| 训练显存相关 | 报告只提到 fused QSA kernel 不再物化中间结果、"substantially reduces memory consumption"（训练侧，未给数字） | P7 |
| HF 卡补充（非报告） | HF 模型卡亦无显存/内存建议数字；HF 侧栏标 "Model size: 180B params / BF16 · I64"（125B+51B+4B 之和的近似标签，页面未解释） | HF 模型卡 |

---

## 3. 推理速度事实

**核心结论：报告全文没有任何绝对速度单位（tokens/s、token/s、throughput），只有相对加速倍数（kernel/模块级）。**

| 数字 | 含义与评测条件 | 出处 |
| --- | --- | --- |
| Prefill 7.6× | 1M 上下文，QSA 相对 dense GQA（FlashInfer paged）；
条件：Chunked prefill，最后 16K chunk，batch size 1 | P2、P9 Fig.6(c) 说明 |
| Decode 4.9× | 1M 上下文，QSA 相对 dense GQA（FlashInfer paged）；
条件：batch size 4，next_n=4（含 3 步 MTP 预测） | P2、P9 Fig.6(d) 说明 |
| Indexer prefill 3.8× / decode 4.4× | 索引器 r=4 相对 r=1，1M 上下文（同 Fig.6 条件） | P9 Fig.6(a)(b) |
| 加速起始点 | 从 64K 上下文开始 QSA 出现加速，越长越快 | P9 |
| FlashQLA 2–3× forward / ~2× backward | GDN 训练 kernel（TileLang）相对 FLA Triton kernel，NVIDIA GPU，框架无关 | P2、P5 §2.1.1 |
| 与"不含 GDN/QSA 的纯全注意力整模型"的端到端加速比 | **报告未给出**（只有 kernel/注意力模块级数字，见上两行） | 报告未提及 |

注：Fig.6 的 indexer prefill 图量纲如 1M 处约 200→20ms 级别（图内刻度，文字仅给出倍数，未给绝对延迟 ms 值，报告正文未引用具体 ms）。图内刻度为 OCR 噪声风险，本总结只采用正文与图注中文字。

---

## 4. 长上下文实现事实

**核心结论：报告没有出现"262144 / YaRN / rope/trailer-factor / 静态/动态缩放"等任何长上下文扩展实现字样。报告对 1M 的做法是：(a) 训练阶段在 256K 长度上做 CPT，(b) 在 1M 评测，(c) 用 QSA 稀疏注意力覆盖长序列。** 报告明确给出的相关事实：

| 事实 | 内容 | 出处 |
| --- | --- | --- |
| QSA 引入时机 | 在 CPT（继续预训练）阶段引入，sequence length 256K；两阶段 | P6 §2.1.2 Training Details |
| 阶段 1（dense distillation） | 仅训 indexer 1000 步，lr 1×10⁻³；每步 8 条 256K 序列，合计约 2B tokens | P7 |
| 阶段 2（sparse training） | 全体 backbone + indexer 联合 8000 步，lr 2.5×10⁻⁵；每步 96 条 256K 序列，合计约 200B tokens | P7 |
| 训练时替换范围 | backbone 与 MTP 模块里所有全注意力层都替换为 QSA | P7 |
| 评测覆盖长度 | RULER 从 4K 到 1000K；MRCR（8-needle）从 128K 到 1M | P8 |
| 1M 长上下文表现 | QSA 在 >512K 的 RULER 93.00（全注意力 90.08）；MRCR 1M 26.44（全注意力 20.71） | P8 表 3 |
| 1M 推理效率 | 1M 时 QSA kernel 级 prefill 7.6× / decode 4.9×（见 §3） | P9 |
| 短文本性能影响（报告表述） | 报告只说 QSA"preserves general capabilities on short-context tasks while enabling more efficient long-context inference"（表 2：QSA 8 项 benchmark 中 7 项持平或更高，Avg 76.8 vs 75.9）；**报告未讨论 RoPE 缩放对短文本的负面影响** | P8 §2.1.2 |
| 原生上下文长度 / YaRN / factor / 静态与否 | 报告全文未提及（这些只在 HF 模型卡：原生 262,144、建议 YaRN、factor 4.0 达 1M、多框架实现为静态 YaRN 可能影响短文本） | 报告未提及 / HF 卡 |

---

## 5. 架构事实速查（与 HF 模型卡核对）

核对源：HF 卡事实文档（`事实-Qwen3.8-Flash-Next.md`）。判定规则：报告原文 vs HF 卡都有的→比对；报告没有而 HF 卡有的→标"报告未提及"；数值冲突才标冲突。

| 字段 | 报告原文 | HF 模型卡 | 核对结论 |
| --- | --- | --- | --- |
| 总参数量 | 125B total parameters | 125B | ✅ 一致 |
| 激活参数量 | 6B activated per token | 6B | ✅ 一致 |
| n-gram 嵌入参数 | additional 51B parameters ... held off the accelerator | plus 51B n-gram embedding | ✅ 一致 |
| MTP 参数 | 报告只提 MTP module / multi-step / four-step speculative decoding，未给参数 | 4B（plus 4B MTP） | 报告未提及参数数 |
| 层数 | 报告未明确主模型层数；正文仅两处涉及"48 layers"且都是实验模型（48 层下 GR vs Block AttnRes 消融；48-layer 156B-A7B 的学习率实验），均非主模型规格 | 48 | 报告未提及（无冲突） |
| Hidden 维度（正文转述 hidden size） | 报告未出现 2560（GDN 公式只用符号 d） | Hidden Dimension: 2560 | 报告未提及 |
| QSA：Q/KV 头数 | 报告未给 QSA 核心注意力头数 | Q 24 / KV 2 | 报告未提及 |
| QSA 头维 | 报告未给头维；仅暗示"indexer head 128 维中的 64 维做 RoPE，与核心注意力旋转维度匹配" | Head Dimension 256 / RoPE dim 64 | 报告未提及头维（RoPE 64 与报告"部分 RoPE 64/128"一致 ✅） |
| QSA Indexer | MQA：4 query heads + 1 shared key head；partial RoPE 64/128；r=4；K=2048；512 块 | Indexer: MQA 4Q+1K，head dim 128，Budget 512 blocks or 2048 tokens | ✅ 一致（头维 128 报告未给，其余一致） |
| GR 分支数 | nr=4 branches；bottleneck rank = d/8（式(31) 的 r） | 4 branches，Bottleneck Rank 320 | 分支数 ✅；报告未给 320（若 d=2560 则 d/8=320，该等号属算术推论非报告原文：不确定） |
| MoE 专家数 | 报告只提 "routed and shared experts"，未给数量 | 512 experts，10 Routed + 1 Shared，intermediate 640 | 报告未提及 |
| GDN head 数 / 头维 | 报告未给 GDN 头数/头维（状态矩阵 dk×dv 符号） | V 48 / QK 16 / head 128 | 报告未提及 |
| 权重精度 | 报告未明确权重精度；只提 GR 残差状态存 FP8（相对 BF16 省一半字节） | BF16 · I64（HF 侧栏 Tensor type） | 报告未提及 |
| 原生上下文 / 可扩 1M | 报告无 262144；1M 仅以 RULER/MRCR 评测上限与 QSA 加速出现 | 262,144 natively，extensible to 1,000,000 | 报告未提及（无冲突） |
| 层排列（token mixing 周期） | 每 4 层 1 层注意力，其余 3 层 GDN；Fig.1 为 12×(...)+MTP 3× 图 | 12 × (3 × (GDN→MoE) → 1 × (QSA→MoE)) | ✅ 一致 |

补充交叉核对：报告 §2.1.1 表 1 与表 5/6 的消融模型是 25B-A3B / 28 层 / 156B-A7B 48 层等小模型，不是最终 125B 模型规格，本表按"报告对最终模型的描述"核对。

---

## 6. Benchmark 分数（报告正文，与 HF 卡核对）

### 6.1 报告正文 Tab.11（Qwen3.8-Flash-Next-Base，14 项预训练基准）

评测条件（§4 Evaluation 所列）：MMLU 5-shot；MMLU-Redux 5-shot；MMLU-Pro 5-shot+CoT；SuperGPQA 5-shot+CoT；BBH 3-shot+CoT；GPQA 5-shot+CoT；GSM8K 4-shot+CoT；MATH 4-shot+CoT；EvalPlus 0-shot（HumanEval/MBPP/HumanEval+/MBPP+ 平均）；MultiPL-E 0-shot；SWEBench-Pretrain（SWE-bench 的预训练变体）；MGSM 8-shot+CoT；MMMU 5-shot；INCLUDE 5-shot。【P22】

| Benchmark | Flash-Next-Base | Qwen3.7-Plus-Base(397B) | 对前辈胜负有记录的 |
| --- | --- | --- | --- |
| MMLU | 90.36 | 90.43 | 输 0.07 |
| MMLU-Redux | 90.68 | 91.47 | 输 0.79 |
| MMLU-Pro | 73.23 | 70.90 | 赢 |
| SuperGPQA | 51.36 | 48.42 | 赢 |
| BBH | 90.87 | 89.41 | 赢 |
| GPQA | 51.42 | 51.52 | 输 0.10 |
| GSM8K | 93.29 | 92.95 | 赢 |
| MATH | 72.78 | 74.38 | 输 1.60 |
| EvalPlus | 78.76 | 78.06 | 赢 |
| MultiPL-E | 79.09 | 81.68 | 输 2.59 |
| SWEBench-Pretrain | 50.99 | 49.24 | 赢 |
| MGSM | 89.33 | 85.42 | 赢 |
| MMMLU | 84.86 | 84.53 | 赢 |
| INCLUDE | 78.40 | 78.90 | 输 0.50 |

报告结论文字：Flash-Next-Base 在 14 项中 8 项超 Qwen3.7-Plus-Base，其余最多落后 2.6 分；全部 14 项超 Qwen3.8-27B-Base（27B-Base 分数见表）。【P22-P23】

### 6.2 报告正文 QSA vs 全注意力（连续训练后上层 post-train 前的消融，表 2）

| Benchmark | Full Attn | w/ QSA |
| --- | --- | --- |
| MMLU-Pro | 72.9 | 73.7 |
| SuperGPQA | 51.7 | 52.1 |
| MATH | 69.8 | 71.6 |
| GSM8K | 91.0 | 92.2 |
| BBH | 90.4 | 91.6 |
| MMMLU | 81.8 | 81.1 |
| EvalPlus | 70.8 | 72.3 |
| MultiPL-E | 78.4 | 79.8 |
| Avg | 75.9 | 76.8 |

### 6.3 长上下文（RULER + 8-needle MRCR，表 3）

| 评测 | ≤128K | 128–256K | 256–512K | 512K–1M | MRCR 128K | 256K | 512K | 1M | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full Attn | 99.84 | 99.81 | 97.65 | 90.08 | 97.14 | 94.20 | 30.66 | 20.71 | 78.76 |
| w/ QSA | 99.89 | 99.62 | 98.95 | 93.00 | 95.98 | 93.00 | 40.53 | 26.44 | 80.93 |

评测条件：RULER 4K–1000K；MRCR 8-needle 128K–1M。【P8】

### 6.4 MTP 四步推测接受长度（表 4）

| 方法 | MT-Bench | GSM8K | MATH | HumanEval | MBPP | Avg |
| --- | --- | --- | --- | --- | --- | --- |
| Full Attn | 3.44 | 4.19 | 4.29 | 4.24 | 4.12 | 4.06 |
| w/ QSA（复用 top-k 索引） | 3.47 | 4.20 | 4.30 | 4.26 | 4.13 | 4.07 |

### 6.5 与 HF 模型卡 benchmark 对照

HF 模型卡列的分数字段（DeepSWE 1.1=58.7、SWE-bench Pro=62.5、SWE-bench Multilingual=81.0、GPQA Diamond=91.7、HLE=35.9、LiveCodeBench v6=91.9、Agents' Last Exam Pass@1 24.3/Score 51.2、Toolathlon 73.5、IFBench 81.3、NL2Repo-Bench 48.1、CoWorkBench 73.9、JobBench 55.7、NL2Repo-Bench 等）**全部未出现在报告正文**——报告没有 DeepSWE、SWE-bench（非委岗预训练变体）、GPQA Diamond、HLE、LiveCodeBench 分数。【报告未提及；HF 卡有】

无冲突：报告 MMLU 90.36 等与 HF 卡的 Agentic/前沿分数无重叠可比项；报告的 SWEBench-Pretrain 50.99 与 HF 卡的 SWE-bench Pro/Multilingual 不是同一评测。评测条件差异已注明。

---

## 7. 报告的量化数字总清单（便于抓取）

- 规模：125B + 6B 激活 + 51B n-gram off-accel；相对 397B-A17B 为 1/3 激活、1/3 token、1/9 FLOPs【P1】
- 相对加速：FlashQLA 2–3× fwd / ~2× bwd【P2/P5】；QSA 1M prefill 7.6× / decode 4.9×（自 64K 起加速，越远越快）【P2/P9】；indexer r=4 prefill 3.8× / decode 4.4×【P9】；索引复杂度 O(n²)/r【P9】
- QSA 参数：K=2048、r=4、512 块、MQA 4Q+1K、partial RoPE 64/128【P6–P7】
- GDN：固定状态 dk×dv、数据相关 decay α 与 write β 门【P4】
- GR：nr=4 分支、bottleneck d/8、sigmoid 门、group RMSNorm、残差状态 FP8（省一半字节）【P11/P14】
- 训练：Muon 8 步 NS、lr/batch 比 Qwen3.5 配方上移、batch-size warmup 不用（+18.8% 步数收益为负）、4× 最优 lr 下 0 loss spike【P17–P20】
- 长上下文：CPT 256K 训练、阶段 1 约 2B token、阶段 2 约 200B token；RULER 测到 1000K【P6–P8】
- 稳定性：2×/4× 最优 lr 压力测试，Muon+GR 4× 下零 spike、零裁剪触发；生产中 276B token 无 spike【P19–P21】