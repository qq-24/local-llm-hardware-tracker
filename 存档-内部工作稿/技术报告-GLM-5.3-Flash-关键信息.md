# 关键信息总结：glm-5.3-Flash=tech_report.pdf（实际内容为 GLM-5 技术报告）

## ⚠️ 文件身份核验（最重要发现）

| 项目 | 事实 | 出处 |
|---|---|---|
| 文件名暗示 | glm-5.3-Flash=tech_report.pdf | 下载文件名 |
| 报告实际标题 | **GLM-5: from Vibe Coding to Agentic Engineering** | 第 1 页 |
| 作者 | GLM-5 Team, Zhipu AI & Tsinghua University | 第 1 页 |
| arXiv 编号 | arXiv:2602.15763v2 [cs.LG]，24 Feb 2026 | 第 1 页扉页、第 32-35 页参考文献 |
| 与 GLM-5.3-Flash HF 卡关系 | HF 卡 GLM-5.3-Flash 的 arxiv 元数据就是 2602.15763（见已存档 `事实-GLM-5.3-Flash.md` 第 57 行）→ **GLM-5.3-Flash 引用的 "Technical report" 就是这份 GLM-5 报告**，该模型无独立架构报告 | 现有存档文档 |
| 结论 | 本报告通篇讲 **GLM-5（总参 744B / 激活 40B）**，**不是** GLM-5.3-Flash（320B/18B）。任务描述的"KV 4.4x 倍数、IndexPool、1M 上下文、KV 量化、吞吐数字"等 GLM-5.3-Flash 独有内容大多**报告未提及**，需查博客/HF 卡（已有 `事实-GLM-5.3-Flash.md` 存档） | — |

提炼：任务六大目标中，"与 HF 卡核对"实际是把 GLM-5 报告的架构/分数与 GLM-5.3-Flash 的 HF 卡数字做比对，二者是**两个不同模型**，数字差异属正常，不算冲突。

---

## 1. KV Cache 事实

| 字段 | 报告事实 | 出处 |
|---|---|---|
| KV 每 token 字节数（bytes/token） | **报告未提及**（无任何每 token 字节数） | 全文无 |
| 相对 GLM-5.3 的 KV 降低 4.4x | **报告未提及**（4.4x 在 z.ai 博客，见已有存档） | 全文无 |
| 与 Kimi-K3 / DeepSeek-V4-Flash 的 KV 对比 | **报告未提及** | 全文无 |
| KV 量化方案（FP8/INT8/BF16 cache quantization） | **报告未提及**。报告出现的精度名词仅限：训练 RL rollout 用 FP8（第 14 页 3.6.2）、SFT 阶段 INT4 QAT（第 10 页 2.4.3）、Ascend 部署 W4A8/W8A8（第 21 页第 5 节）——均为训练或芯片部署场景，非 KV cache 量化 | 全文无 cache 量化表述 |
| MLA latent KV 压缩维度 | **576-dimension latent KV-cache**（原文："MLA with a 576-dimension latent KV-cache cannot match the performance of GQA-8"）；推理方向计划改 MQA 模式（第 14 页 3.5："uniformly adopt the Multi-Query Attention (MQA) mode of MLA for inference"） | 第 4-5 页 2.1；第 14 页 3.5 |
| KV LoRA Dim（用户重点要的数字） | **KV LoRA Dim = 512，Q LoRA Dim = 2048**（表 10 原文值；GLM-4.5 无此两项，标 –） | 附录 A 表 10，第 36 页 |
| 576 与 512 的关系 | 报告未明确说明构成关系（不推测，两数字并列记录） | 表 10 + 第 5 页正文 |
| IndexPool | **报告未提及**（IndexPool 只出现在 GLM-5.3-Flash 博客/HF 卡） | 全文无 |
| DSA indexer 相关 KV 事实 | indexer 的 top-k **k=2048**（原文 "k = 2048 used by the indexer"）；DSA 中文语境称"lightning indexer 达到 token 级稀疏，不丢弃任何长程依赖" | 第 12 页 3.2；第 7 页 2.1.2 |
| 1M 上下文下 KV 总大小 | **报告未提及**（GLM-5 报告最大上下文为 SFT 202,752，见第 4 节，无 1M 表述） | 全文无 |

---

## 2. 显存 / 硬件需求

| 字段 | 报告事实 | 出处 |
|---|---|---|
| 运行所需显存/内存数字（GB） | **报告未提及**任何通用运行显存数字 | 全文无 |
| 推荐硬件（80G 卡 ×N、CUDA 12） | **报告未提及** | 全文无 |
| 中国 AI 芯片适配（唯一硬件数字类事实） | 用 **W4A8 混合精度量化把 750B 参数 GLM-5 装入单台 Atlas 800T A3 机器**：Attention/MLP 用 W8A8(INT8)，MoE experts 压缩为 W4A8(INT4)；工具 msModelSlim；结合 QuaRot 与 Flex_AWQ_SSZ | 第 21 页第 5 节 |
| 单节点性能/成本对比 | "GLM-5 on a single Chinese node achieves performance comparable to dual-GPU international clusters, **reducing deployment costs in long-sequence scenarios by 50%**"（原文） | 第 22 页第 5 节 |
| 适配的国产芯片平台 | 七个：Huawei Ascend、Moore Threads、Hygon、Cambricon、Kunlunxin、MetaX、Enflame | 第 4 页；第 21 页 |
| 定制算子上核 | Lightning Indexer（score/ReLU/TopK 合一核）、Sparse Flash Attention、MLAPO（融合 13 个预处理算子） | 第 21-22 页 |
| 推理引擎适配 | vLLM-Ascend（异步调度、RadixCache、Prefix Cache、DP+EP、FlashComm、MTP）、SGLang | 第 22 页 |
| 部署成本/每 token 成本对比表 | **报告未提及**（无 NVIDIA GPU vs 中国芯片成本表） | 全文无 |

---

## 3. 推理速度 / 吞吐

| 字段 | 报告事实 | 出处 |
|---|---|---|
| Prefill / Decode tokens/s、吞吐数字 | **报告未提及**任何 tokens/s 数值 | 全文无 |
| 相对 GLM-5.3 的吞吐提升倍数 | **报告未提及** | 全文无 |
| SGLang / vLLM / TokenSpeed 推荐与性能 | 报告只把 vLLM-Ascend 与 SGLang 列为"已适配的推理引擎"（无性能对比数字）；**TokenSpeed 报告未提及** | 第 22 页第 5 节 |
| 注意力计算降幅（性能相关定性数字） | DSA 将长序列 attention 计算量降低**约 1.5-2×**，"128K contexts at half the GPU cost"（原文）；90% 长上下文 attention 条目冗余（引 DeepSeek-V3.2 结论） | 第 6 页 2.1.1 |
| MTP（投机解码）速度事实 | GLM-5 共享 3 层 MTP 参数，接受长度 **2.76** vs DeepSeek-V3.2 的 2.55（相同 speculate steps=4，私有 prompt 集） | 第 5 页表 2 |
| RL 训练侧提速手段（非部署） | FP8 rollout、MTP、PD(prefill-decode) 分离、DP-attention 防跨 rank 复制 KV、"EP64 and DP64 over 8 nodes"部署 | 第 14 页 3.6.2 |
| DSA-RL 训练稳定性事实 | 用确定性 torch.topk 取代 SGLang DSA Indexer 的非确定性 CUDA top-k（训练引擎内）；RL 期间默认冻结 indexer | 第 12 页 3.2 |

---

## 4. 长上下文实现事实

| 字段 | 报告事实 | 出处 |
|---|---|---|
| 如何实现长上下文 | **DSA（DeepSeek Sparse Attention）**：以内容动态细粒度 token 选择取代 dense O(L²) attention；由 dense base 模型 **continued pre-training** 引入（免从头训练成本），两阶段"dense warm-up + sparse training adaptation" | 第 5-6 页 2.1.1 |
| DSA 训练细节 | warm-up 1000 步 × 每步 14 条 202,752 token 序列、LR 5e-3；sparse adaptation 20B tokens（对比 DeepSeek-V3.2 的 943.7B，少得多即可对齐 MLA 性能） | 第 6 页 2.1.1 |
| 中等训练上下文（mid-training） | 三阶段延伸：**32K(1T tokens) → 128K(500B) → 200K(50B)** | 第 8 页 2.3 |
| SFT 阶段最大上下文 | **202,752 tokens** | 第 11 页 3.1 |
| 1M 上下文 | **报告未提及**（本报告无 1M 表述；1M 属 GLM-5.3-Flash 博客/HF 卡内容） | 全文无 |
| linear+sparse hybrid 表述 | 报告未用"hybrid attention"表述。采用 MLA + DSA；linear 变体 GDN / SimpleGDN（gated linear recurrence）仅在消融实验评估，**未采用**（SimpleGDN 在 RULER@128K 仍掉 3.59-8.25 分；DSA 被称"lossless by construction"） | 第 6-7 页 2.1.2 |
| SWA 对比 | 搜索式 SWA Pattern 在 RULER@128K 掉 5.69 分（vs interleave 掉 30.35） | 第 7 页表 5 |

---

## 5. 架构事实速查（对照任务目标逐项）

报告对象 = GLM-5（表 10 + 正文）。与任务预期 "GLM-5.3-Flash 320B/18B/45 层" 全部对不上，因模型不同；与现有存档中 GLM-5 相关数据核对一致处标 ✅。

| 字段 | 报告值（GLM-5） | 出处 | 与 HF 卡/博客存档核对 |
|---|---|---|---|
| 总参数 | **744B**（含 MTP 层、不含 embedding/output；GLM-4.5 为 355B） | 表 10；第 4 页 | ✅ 与存档中 GLM-5-Base Total 744B 一致 |
| 激活参数 | **40B**（GLM-4.5 为 32B） | 表 10；第 4 页 | ✅ 与存档 GLM-5-Base Active 40B 一致 |
| 层数 | **80**（正文："reduces its layer count to 80"；表 10 拆分：3 dense + 75 MoE = 78，另 1 MTP 层） | 第 4 页；表 10 | GLM-5.3-Flash 是 45 层，模型不同不构成冲突 |
| Hidden Dim / Dense Inter / MoE Inter | 6144 / 12288 / 2048 | 表 10 | — |
| QK Head Dim / V Head Dim | **192 / 256**（正文："increase the head dimension from 192 to 256 and decrease the number of attention heads by 1/3"） | 表 10；第 5 页 | — |
| 注意力头数 | **64**（GLM-4.5 为 96；即减 1/3） | 表 10 | — |
| **Q LoRA Dim / KV LoRA Dim** | **2048 / 512**（GLM-4.5 无；这是报告给的压缩维度具体数字） | 表 10 | 存档注明 HF/博客 GLM-5.3-Flash 无 LoRA 数值 |
| # Indexer Attn Heads / Indexer Head Dim | 32 / 128 | 表 10 | — |
| # Experts（total / routed / shared） | 256 / 8 / 1 | 表 10 | — |
| Vocabulary | 154880 | 表 10 | — |
| 注意力类型 | MLA（576-dim latent KV）+ DSA（top-k=2048 sparse）；RL rollout 用 FP8、计划 MQA 推理 | 第 4-5, 12, 14 页 | — |
| mHC（Manifold-Constrained Hyper-Connections） | **报告未提及**（mHC 是 GLM-5.3-Flash 博客/HF 卡内容） | 全文无 | — |
| IndexPool | **报告未提及** | 全文无 | — |
| 权重精度 BF16/F8_E4M3/F32 | **报告未提及**（该三元组在 HF 卡元数据。报告仅提 INT4 QAT、FP8 rollout、W4A8/W8A8 芯片量化） | 全文无 | 存档：HF 卡 "BF16 · F8_E4M3 · F32" |
| 训练数据规模 | 摘要 27T、正文 28.5T tokens（两处口径，分别在第 3 页与第 4、24 页） | 封面摘要；2 节 | — |

---

## 6. Benchmark 分数（GLM-5 报告正文表 7，第 23 页）

| Benchmark | GLM-5 | GLM-4.7 | DeepSeek-V3.2 | Kimi-K2.5 | Claude Opus 4.5 | Gemini 3 Pro | GPT-5.2(xhigh) |
|---|---|---|---|---|---|---|---|
| HLE | 30.5 | 24.8 | 25.1 | 31.5 | 28.4 | 37.2 | 35.4 |
| HLE (w/ Tools) | 50.4 | 42.8 | 40.8 | 51.8 | 43.4* | 45.8* | 45.5* |
| AIME 2026 I | 92.7 | 92.9 | 92.7 | 92.5 | 93.3 | 90.6 | – |
| HMMT Feb 2025 | 97.9 | 97.1 | 92.5 | 95.4 | 92.9 | 97.3 | 99.4 |
| HMMT Nov 2025 | 96.9 | 93.5 | 90.2 | 91.1 | 91.7 | 93.0 | 97.1 |
| IMO-AnswerBench | 82.5 | 82.0 | 78.3 | 81.8 | 78.5 | 83.3 | 86.3 |
| GPQA-Diamond | 86.0 | 85.7 | 82.4 | 87.6 | 87.0 | 91.9 | 92.4 |
| LongBench v2 | 64.5 | 59.1 | 59.8 | 61.0 | 64.4 | 68.2 | 59.8 |
| SWE-bench Verified | 77.8 | 73.8 | 73.1 | 76.8 | 80.9 | 76.2 | 80.0 |
| SWE-bench Multilingual | 73.3 | 66.7 | 70.2 | 73.0 | 77.5 | 65.0 | 72.0 |
| Terminal-Bench 2.0 (Terminus-2) | 56.2 / 60.7† | 41.0 | 39.3 | 50.8 | 59.3 | 54.2 | 54.0 |
| Terminal-Bench 2.0 (Claude Code) | 56.2 / 61.1† | 32.8 | 46.4 | – | 57.9 | – | – |
| CyberGym | 43.2 | 23.5 | 17.3 | 41.3 | 50.6 | 39.9 | – |
| BrowseComp | 62.0 | 52.0 | 51.4 | 60.6 | 37.0 | 37.8 | – |
| BrowseComp (w/ Context Manage) | 75.9 | 67.5 | 67.6 | 74.9 | 57.8 | 59.2 | 65.8 |
| BrowseComp-ZH | 72.7 | 66.6 | 65.0 | 62.3 | 62.4 | 66.8 | 76.1 |
| τ²-Bench | 89.7 | 87.4 | 85.3 | 80.2 | 91.6 | 90.7 | 85.5 |
| MCP-Atlas (Public Set) | 67.8 | 52.0 | 62.2 | 63.8 | 65.2 | 66.6 | 68.0 |
| Tool-Decathlon | 39.2 | 23.8 | 35.2 | 27.8 | 43.5 | 36.4 | 46.3 |
| Vending-Bench 2 | $4,432 | $2,377 | $1,034 | $1,198 | $4,967 | $5,478 | $3,591 |
| GDPval-AA Elo | 1,409 | 1,198 | 1,195 | 1,288 | 1,400 | 1,201 | 1,462 |

标注：* = HLE 全量；† = verified 版 Terminal-Bench 2.0（修复歧义指令，Terminus-2/Claude Code 两框架平均 5 次）。GDPval-AA Elo 记录于 2026-02-15。
任务问的 Terminal Bench 2.1、DeepSWE v1.1、AutomationBench、NL2Repo、Toolathlon、Vision 类：**本报告未提及**（这些是 GLM-5.3-Flash 的 HF 卡/博客分数：84.3 / 63.4 / 48.8 / 56.3 / 78.4 / 视觉 62.4-89.4，见已有存档）。

补充分数（报告其他表）：
- SWE-rebench（2026-01，表 9）：GLM-5 Resolved **42.1%**（SEM 1.21%，Pass@5 50.0%）；榜首 Claude Opus 4.6=52.9%、GPT-5.2 xhigh=51.7%
- CC-Bench-V2（表 8）：Frontend HTML ISR 38.9/CSR 76.3、React ISR 34.6/71.0、Vue 32.7/77.1；Build 成功率 React/Vue/Svelte 100%、Next.js 95.0%（GLM-4.7 仅 60-70%）；Backend Pass@1=25.8；Repo Exploration Pass@1=65.6；Chained Tasks Pass@1=52.3
- Base 模型（表 11）：GLM-5-Base MMLU 88.3、BBH 87.4、HellaSwag 88.1、EvalPlus 87.0、LiveCodeBench 34.4、SimpleQA 36.0、GSM8K 68.8、MATH 56.4、C-Eval 88.8 → 与博客存档 GLM-5-Base 列一致 ✅（MMLU/BBH/HellaSwag/LiveCodeBench/SimpleQA 均同值）

---

## 7. 与 GLM-5.3-Flash HF 模型卡核对结论

| 任务预期字段（GLM-5.3-Flash HF 卡） | 本报告（GLM-5） | 判定 |
|---|---|---|
| 320B 总参 / 18B 激活 | 744B / 40B | 模型不同，属正常差异 |
| 45 层 | 80 层（3+75+1） | 同上 |
| mHC | 未提及 | — |
| hybrid linear+sparse attention | 报告用 MLA+DSA（linear 变体仅消融未用） | — |
| indexer / IndexPool | indexer=有（DSA，k=2048）；IndexPool=无 | — |
| KV 相对倍数 4.4x、比 Kimi-K3/DeepSeek-V4-Flash 略大 | 未提及 | — |
| 1M 上下文 | 报告最大 202,752（SFT） | — |
| 权重 BF16/F8_E4M3/F32 | 未提及 | — |
| KV LoRA dim / 压缩维度 | **KV LoRA Dim=512、Q LoRA Dim=2048（报告表 10）** | 报告有具体数字 |
| Terminal Bench 2.1=84.3 等新 benchmark 分数 | 报告只有 Terminal-Bench 2.0=56.2/60.7† 等旧分数 | 模型不同 |
| arXiv 引用 | 2602.15763 = 本报告 ✅ | **身份确认：HF 卡引用的报告即此文件** |

---

## 附：本报告可作为 GLM-5.3-Flash 事实补充的合理内容

1. GLM-5 的 KV LoRA Dim=512 / Q LoRA Dim=2048（表 10）——GLM-5.3-Flash 的 HF 卡/博客未给该数字，若部署规划需要参考 GLM 同族压缩维度口径，这是目前唯一书面数字（但严格说是 GLM-5 的，不是 GLM-5.3-Flash 的，报告未提 Flash 的对应值）。
2. DSA indexer top-k=2048、MLA latent 576 维——GLM-5.3-Flash 的博客同样未给这些细化数字。
3. 中国芯片部署定性结论："single Chinese node ≈ dual-GPU international cluster，long-sequence 部署成本降 50%"。
4. 报告与 GLM-5.3-Flash 的 base 对比表（存档已含）中 GLM-5-Base 一行全部数值本报告殊途同源、一致。

## 报告未提及清单（部署规划仍需从博客/HF 卡取值）

KV cache 每 token 字节数、KV cache 相对 4.4x/3.0x、Kimi-K3 与 DeepSeek-V4-Flash KV 对比、IndexPool、1M 上下文、KV cache 量化方案、byte/token 成本、prefill/decode tokens/s、吞吐数字、显存 GB、推荐 GPU 数与型号、GLM-5.3-Flash 独有 benchmark 分数（Terminal Bench 2.1 / DeepSWE v1.1 / AutomationBench / NL2Repo / Toolathlon / Vision）。