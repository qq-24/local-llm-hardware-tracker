# 01 模型档案：Qwen3.8-Flash-Next

- 模型：Qwen3.8-Flash-Next（Alibaba，2026-08 发布）
- 仓库：https://huggingface.co/Qwen/Qwen3.8-Flash-Next （HF id：`Qwen/Qwen3.8-Flash-Next`，HF createdAt=2026-08-24，AA 页面注明 released Aug 2026 / 官方 FAQ "August 26, 2026"）
- 取证日期：2026-08-27
- 档案口径（项目统一，不可改）：**权重 Q4、KV Q8**；MoE 内存按**总参数**算；1M 上下文支持按 **YaRN 4 倍扩展**判定；51B n-gram 属 off-accelerator（不占显存）
- 结论速览：Q4+Q8 跑 1M 需 **至少 ~88 GB 显存**（n-gram 一并落未必须与统一内存场景：~113 GB）

---

## 来源清单

| 编号 | 来源 | 用途 |
|---|---|---|
| S1 | https://huggingface.co/api/models/Qwen/Qwen3.8-Flash-Next （HF Model API） | safetensors 分 dtype 参数计数、usedStorage、siblings、license |
| S2 | https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json | 架构字段（text_config/vision_config） |
| S3 | https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/README.md | 官方参数口径、上下文、YaRN、推荐框架 |
| S4 | https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/model.safetensors.index.json | tensor 名确认 n-gram/MTP 是否在分片主体 |
| S5 | generation_config.json | 推理默认参数 |
| S6 | https://artificialanalysis.ai/models/qwen3-8-flash-next | AA Intelligence Index 等 |

---

## 架构事实

来源：S2 `model_type=qwen4_exp`，`architectures=["Qwen4ExpForConditionalGeneration"]`，pipeline_tag=image-text-to-text（多模态，S1）。

| 字段 | 值 | 来源（config.text_config.X） |
|---|---|---|
| 总层数 | `num_hidden_layers` = 48 | config |
| 注意力布局 | 每 4 层 1 层 full attention，其余 3 层 linear attention —— `full_attention_interval`=4；`layer_types`（48 项）为 `[linear×3, full]×12` | config |
| full-attention 层数 | 12 层（QSA，即 Qwen Sparse Attention） | config layer_types 计数 |
| linear-attention 层数 | 36 层（Gated DeltaNet） | config layer_types 计数 |
| 注意力头 | `num_attention_heads`=24，KV 头 `num_key_value_heads`=2，`head_dim`=256 | config |
| n-gram 嵌入 | `ngram_vocab_size_base`=2,000万、`ngram_size`=3、`heads_per_ngram`=8、`split_ngram_parts`=128，挂第 2 层（PLE，README "bigrams/trigrams at layer 2"） | config + S3 |
| MoE | `num_experts`=512，`num_experts_per_tok`=10（激活专家数），`moe_intermediate_size`=640 | config |
| MTP | 1 层 full attention，hybrid | config.mtp |
| hidden_size / vocab | 2560 / `vocab_size`=248,320 | config |
| RoPE | `rope_theta`=1e7，`rope_type`=default，mrope_section=[11,11,10]，`partial_rotary_factor`=0.25 | config.rope_parameters |
| 视觉编码器 | depth=27、hidden=1152、（另有 video） | config.vision_config |
| 原生上下文 | `max_position_embeddings`=262,144（=256K） | config |

---

## 权重体积

### 落地（checkpoint 内）参数

来源：S1 `safetensors.parameters`（API 逐 dtype 上报）：

| dtype | 参数个数 | 来源 |
|---|---|---|
| BF16 | 179,999,981,424 | S1 |
| I64 | 35 | S1 |
| **合计** | **179,999,981,459 ≈ 180.0 B** | S1 `total` |

- BF16 落地体积（全部 180 B × 2 字节）：S1 `usedStorage` = 360,013,002,208 B = **360.0 GB**，与 180B×2B 完全吻合。
- **n-gram 在不在主体里？在。** S4 索引含 128 个 tensor：`model.language_model.layers.1.ple.ple_embedding.ngram_embedding.shard_0.weight … shard_127.weight`（与 `split_ngram_parts`=128 对应），全部落在 131 个 safetensors 分片内。README（S3）口径 125B + 51B + 4B = 180B，与 API total 180B 完全对应（笔记：任务假设"通常不在"在此模型不成立，取证结果 n-gram 已打包进 checkpoint）。

### Q4 体积（0.5 字节/参数，十进制 GB）

| 口径 | 参数数 | Q4 体积 | 来源 |
|---|---|---|---|
| 全部落地参数（含 n-gram） | 180.0 B | **90.0 GB** | S1 合计 ×0.5 |
| └ 加速器上权重（MoE 125 B + MTP 4 B） | 129 B | **64.5 GB** | S3 口径分拆 ×0.5 |
| └ n-gram 嵌入（off-accelerator，不占显存） | 51 B | 25.5 GB | S3 口径分拆 ×0.5 |

备注：本项目口径"MoE 内存按总参数算"→ 加速器按 125 B（MoE）+ 4 B（MTP）= 129 B 扛，**不按 6 B 激活**。

---

## KV 体积（KV=Q8，1 字节/参数）

- 只计存储 KV 的 full-attention 层（QSA），12 层；换算：12 层 × `num_key_value_heads`(2) × `head_dim`(256) × 2（K+V） = **12,288 字节/token**（来源：S2 config + 计数，成本式按任务规定）。
- linear-attention（DeltaNet）36 层为有界隐含状态，不随 seq 长增长，不计入（口径说明）。

| 上下文 | token 数 | Q8 KV 字节 | 体积 |
|---|---|---|---|
| 128K | 131,072 | 1,610,612,736 B | **1.61 GB** |
| 262K（原生上限） | 262,144 | 3,221,225,472 B | **3.22 GB** |
| 1M | 1,048,576 | 12,884,901,888 B | **12.88 GB** |

---

## 显存门槛结论

以 1M 上下文（需 YaRN 4×）、权重 Q4、KV Q8：

| 项 | 计算 | 体积 |
|---|---|---|
| 权重（加速器部分 Q4，129 B） | 129 B × 0.5 字节 | 64.5 GB |
| KV Q8 @ 1M | 12,884,901,888 B | 12.9 GB |
| 激活/框架余量 | 项目口径约值 | 约 10 GB |
| **合计（显存）** | 64.5 + 12.9 + 10 | **约 88 GB（取整）** |
| 若 n-gram 一并占统一内存 | 90.0 + 12.9 + 10 | 约 113 GB |

**结论一句话：Qwen3.8-Flash-Next 权重 Q4 + KV Q8 跑 1M 上下文，至少需要 ~88 GB 显存（n-gram 51B off-accelerator 走内存不计显存；若严格统一内存全量落地需 ~113 GB，另加 n-gram 约 26 GB 内存）。**

- C1 判定（1M 装得下）：需 ≥ 88 GB 级显存设备；一般单卡 80 GB 档放不下 1M，96 GB / 128 GB 档统一内存可过。最终是否过 C1 以项目阈值表为准，本档案只供数字。

---

## AA 智力（来源 S6）

| 指标 | 值 | 说明 |
|---|---|---|
| **Artificial Analysis Intelligence Index** | **56**，排名 **#4 / 1105**（开放权重同档更靠前的相对位） | S6 页头 Intelligence 区块（"scores 56", rank 4 of 1105） |
| 参数量 | **total 180 B / active 6 B** | S6 Technical specifications |
| 上下文窗口 | 256k（页头 summary）；FAQ 处写 "260k" — **页面内部口径不一致**；config 原生为 262,144=256K | S6 + S2 |
| 输出速度 | **73.5 t/s**（跨 provider 中位数；页头显示 74） | S6 FAQ；Speed 排名 #22/1105 |
| TTFT | 2.72 s | S6 FAQ |
| Verbosity | Intelligence Index 评测消耗 **200M** 输出 tokens（同类中位 110M） | S6 |
| Reasoning | 是（reasoning 版，thinking effort xhigh/medium/low） | S6 + S1 chat_template |
| 输入/输出模态 | 文本/图像/视频输入，文本输出 | S6 |
| 许可证 | Qwen Community License 1.0（open weights，商用受限） | S6 + S1 cardData |

**AA 参数量与本档案对比**：AA 报 total 180 B，与 S1 `safetensors.total` 180 B 一致——即 AA 的 total **已含** 51 B n-gram 与 4 B MTP（= README 125 B + 51 B + 4 B 的合计）。差异只在本档案按项目口径把 n-gram 单独拆出作 off-accelerator、并按 MoE 总参数（125 B，非 6 B active）计加速器内存。两处数字所指向的 180 B 总量相同。

---

## 其他事实

| 项目 | 事实 | 来源 |
|---|---|---|
| 原生上下文 | 262,144 token | S2 `max_position_embeddings` |
| 是否支持 1M | **原生不支持**；需 **YaRN 4× 扩展**（`factor: 4.0`、`original_max_position_embeddings: 262144`、`max-model-len 1000000`） | S3 README（L598、L626 vLLM/SGLang/TokenSpeed 三框架示例） |
| YaRN 注意 | 静态 YaRN 缩放因子恒定，处理短文本可能有损；README 建议仅在长上下文所需时改约 2× 用于 524,288 | S3 L640-642 |
| MoE 专家数/激活 | 512 专家 / 每 token 激活 10 个 | S2 |
| 推荐推理框架 | HF Transformers、vLLM、SGLang、TokenSpeed（原生支持，含 YaRN 覆盖） | S3 L14 / L600 |
| MTP | 1 层 full attention（hybrid），默认推理参数见 S5（do_sample、temp 1.0、top_k 20） | S2/S5 |
| n-gram 嵌入 | 2,000万 词目、tri-gram、置第 2 层，checkpoint 内分 128 块 | S2/S3/S4 |
| 多模态 | image-text-to-text，含视觉编码器（depth 27），另有 Qwen3.8-Flash 为官方生产版默认 1M | S1/S3 |

---

## 与官方一致性

| README（S3）官方声明 | 本档案取证 | 一致？ |
|---|---|---|
| 参数 125B（6B 激活）+ 51B n-gram + 4B MTP = 180B | S1 safetensors total 179,999,981,459 ≈ 180.0 B；索引含 128 块 n-gram tensor | ✅ 完全对应 |
| Context 262,144 原生，可扩 1,000,000 | S2 `max_position_embeddings`=262,144；YaRN factor≈4.0 示例直达 1M | ✅ |
| N-gram embedding 参数 51B | S1 总量 - (125+4)B ≈ 51B | ✅ |
| 每次激活 6B、MoE 512 专家 | S2 `num_experts=512`、`num_experts_per_tok=10`；AA active 6B 一致 | ✅ |
| AA total 180B / active 6B | 与 S1/S2 一致（AA total 含 n-gram） | ✅ |

**取证发现的两处口径差异（非错误，需记录）**：① n-gram 虽属 off-accelerator，但**已包含在下载的 safetensors checkpoint 内**（131 个分片、BF16 360 GB、Q4 90 GB），并非需单独另下；② AA 页面上下文窗口 summary 写 256k、FAQ 写 260k，两者与 config 原生 262,144（=256K）在"k"取整口径上不同。