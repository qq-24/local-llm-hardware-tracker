# 事实记录：Qwen3.5-122B-A10B 架构与 KV 计算（来源：官方 config.json + safetensors）

> 编制：2026-08-27。来源 = HF 仓库 `Qwen/Qwen3.5-122B-A10B` 的 `config.json` 字段 + `model.safetensors` 分片元数据（API 返回），均为一级来源，非对话推算。
> 本项目标准：权重 Q4（0.5 字节/参数）、KV Q8（1 字节/元素）。

## 1. 仓库元数据【事实】

| 项 | 值 |
| --- | --- |
| 模型 ID | Qwen/Qwen3.5-122B-A10B |
| architectures | Qwen3_5MoeForConditionalGeneration |
| 权重分量 | 39 个 safetensors 分片 |
| 总参数（safetensors 实测） | **125,086,490,096 ≈ 125.09B**（BF16）；另有 F32 6912 个 |
| 原始权重体积 | ≈ **250 GB**（BF16，125.09B×2B） |
| 命名差异 | 型号名"122B"与实际总参 125.09B 有出入，以 safetensors 实测为准 |
| 是否多模态 | 是（image-text-to-text，vision config 27 层 1152 dim） |

## 2. 文本架构关键字段【config】

| 字段 | 值 | 含义 |
| --- | --- | --- |
| hidden_size | 3072 | 隐藏维 |
| num_hidden_layers | **48** | 总层数 |
| layer_types | 48 项 | **36 × linear_attention + 12 × full_attention**，全注意力层在第 3,7,11,…,47 层 |
| full_attention_interval | 4 | 每 4 层 1 层全注意力 |
| num_attention_heads | 32 | 全注意力 Q 头 |
| num_key_value_heads | **2** | KV 头（GQA） |
| head_dim | **256** | 全注意力头维 |
| linear_num_key_heads | 16 | 线性注意 K 头 |
| linear_key_head_dim | 128 | 线性注意 K 头维 |
| linear_num_value_heads | 64, linear_value_head_dim 128 | 线性注意 V 头 |
| linear_conv_kernel_dim | 4 | 线性注意卷积核 |
| num_experts / per_tok | **256 / 8** | MoE 专家与激活 |
| moe_intermediate_size | 1024 | 专家中间维（hidden 1/3） |
| max_position_embeddings | **262144** | **原生上下文 262K** |
| rope_parameters | rope_type "default"，partial_rotary_factor 0.25，theta 1e7 | 原生无长上下扩展配置；1M 按项目标准走 **YaRN 4 倍扩展**（通用做法） |
| mtp_num_hidden_layers | 1 | MTP 1 层 |

## 3. 按本项目标准（Q4 权重 + Q8 KV）的需求计算【公式】

**权重**：
- Q4 = 125.09B 参数 × 0.5 字节 = **≈ 62.5 GB**

**KV Cache（只计 12 层 full attention；36 层 linear_attention 为固定状态，不随上下文线性增长）**：
- 每层每 token = KV 头 2 × KV 各 256 维 × 2（K+V 两份）× Q8 1 字节 = 1024 B = 1 KB
- 12 层 = **12 KB / token**
- @1M = 12 KB × 1,000,000 = **≈ 12 GB**

> 关键结论：**该模型 1M 上下文 KV(Q8) 只有约 12GB**，与 Qwen3.8-Flash-Next（12.29GB）同量级——都是"每 4 层 1 层存 KV"的稀疏注意力家族设计。
> 此前追踪表中"若 Qwen3.5-122B-A10B 原生 1M KV=265GB 则全部方案出局"的担忧（该数字源自旧对话对 0.265MB/token 的反推，对应全注意力 Dense 架构），**与官方 config 不符，予以排除（✗ 已排除）**。

**合计（Q4 + Q8 KV @ 1M）**：62.5 + 12 ≈ **75 GB**（未含激活/框架开销；加 ~15% 经验余量 ≈ 86GB）
- → C1 判定：**单卡 80G 边缘/紧张，双卡 80G（160G）与 96~128G 组合稳妥可行**；与追踪表原 88~100GB 估算口径一致，**C1 结论保持不变**。
- 上下文扩展：原生 `max_position_embeddings=262144`（262K），1M 按项目标准用 **YaRN 4 倍扩展**（262K×4=1,048,576），与 Qwen3.8-Flash-Next 官方推荐静态 YaRN factor 4.0 同一口径，扩展不作为 C1 否决理由。

## 4. 与旧对话里"122B 需要 70-75GB / M5 Max 64K=17GB"的矛盾

| 说法 | 来源 | 结论 |
| --- | --- | --- |
| Q4 权重 70~80GB（Mac_Studio 对话） | 对话 AI 推算 | 与 config 实测 62.5GB 同量级（差值=余量/区间），不冲突 |
| 0.265MB/token → 1M=265GB | 旧对话反推（全注意力口径） | **与官方 config 矛盾，予以排除** |
| 64K=17GB KV（oMLX 实测） | 对话引用实测 | 若按 Q8 每 token 12KB × 64K ≈ 786MB，与 17GB 差距大 → 疑为该实测含更大精度(BF16)或含线性层状态等，**待验证**，但不影响"只 12 层存 KV"的结构事实 |

## 5. 结论速览
- 权重 Q4：≈62.5 GB；KV@1M Q8：≈12 GB；合计 ≈75 GB（+余量 ≈86GB）→ **追踪表 C1 的 88~100GB 口径成立，无需修改**
- 原生上下文 262K；1M 需扩展，官方未内置配置（新待验证项）