# GLM-5.3-Flash 显存与最低硬件估算

> 编制日期：2026-08-27
> 来源分层标注约定：
> - 【事实】= 从 HuggingFace 仓库 API 拉取到的原始数据（文件 size 字节数 / 分片头 dtype）
> - 【config】= 仓库 config.json 字段取值
> - 【公式】= 基于 config 字段的透明公式演算
> - 【官方】= 官方博客/模型卡原文口径
> - 【经验】= 行业通用经验系数（激活/框架开销余量），非该模型实测
>
> 所有单位注意区分：GiB = 1024³ 字节（显存/内存硬件容量习惯单位）；GB = 10^9 字节。

---

## 第 1 步：仓库真实文件清单与体积【事实】

抓取来源：`https://huggingface.co/api/models/zai-org/GLM-5.3-Flash/tree/main?recursive=true`（分页拉全，共 2 页 72 项）。

### 1.1 全部 .safetensors 分片（62 个，逐条列出 size）

| # | 文件 | size（字节）【事实】 | 体积 |
|---|---|---|---|
| 01 | model-00001-of-00062.safetensors | 5,365,306,704 | 5.00 GiB |
| 02 | model-00002-of-00062.safetensors | 5,320,647,824 | 4.96 GiB |
| 03 | model-00003-of-00062.safetensors | 5,363,467,432 | 5.00 GiB |
| 04 | model-00004-of-00062.safetensors | 5,364,342,296 | 5.00 GiB |
| 05 | model-00005-of-00062.safetensors | 5,363,915,920 | 5.00 GiB |
| 06 | model-00006-of-00062.safetensors | 5,361,809,384 | 4.99 GiB |
| 07 | model-00007-of-00062.safetensors | 5,364,342,528 | 5.00 GiB |
| 08 | model-00008-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 09 | model-00009-of-00062.safetensors | 5,364,169,856 | 5.00 GiB |
| 10 | model-00010-of-00062.safetensors | 5,361,982,080 | 4.99 GiB |
| 11 | model-00011-of-00062.safetensors | 5,363,915,912 | 5.00 GiB |
| 12 | model-00012-of-00062.safetensors | 5,364,342,288 | 5.00 GiB |
| 13 | model-00013-of-00062.safetensors | 5,361,809,408 | 4.99 GiB |
| 14 | model-00014-of-00062.safetensors | 5,364,342,504 | 5.00 GiB |
| 15 | model-00015-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 16 | model-00016-of-00062.safetensors | 5,361,809,176 | 4.99 GiB |
| 17 | model-00017-of-00062.safetensors | 5,364,084,560 | 5.00 GiB |
| 18 | model-00018-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 19 | model-00019-of-00062.safetensors | 5,364,342,272 | 5.00 GiB |
| 20 | model-00020-of-00062.safetensors | 5,361,809,528 | 4.99 GiB |
| 21 | model-00021-of-00062.safetensors | 5,364,342,376 | 5.00 GiB |
| 22 | model-00022-of-00062.safetensors | 5,363,915,936 | 5.00 GiB |
| 23 | model-00023-of-00062.safetensors | 5,361,809,264 | 4.99 GiB |
| 24 | model-00024-of-00062.safetensors | 5,364,342,640 | 5.00 GiB |
| 25 | model-00025-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 26 | model-00026-of-00062.safetensors | 5,364,342,272 | 5.00 GiB |
| 27 | model-00027-of-00062.safetensors | 5,361,809,560 | 4.99 GiB |
| 28 | model-00028-of-00062.safetensors | 5,363,915,976 | 5.00 GiB |
| 29 | model-00029-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 30 | model-00030-of-00062.safetensors | 5,361,809,296 | 4.99 GiB |
| 31 | model-00031-of-00062.safetensors | 5,364,341,544 | 5.00 GiB |
| 32 | model-00032-of-00062.safetensors | 5,363,915,232 | 5.00 GiB |
| 33 | model-00033-of-00062.safetensors | 5,364,342,272 | 5.00 GiB |
| 34 | model-00034-of-00062.safetensors | 5,361,809,552 | 4.99 GiB |
| 35 | model-00035-of-00062.safetensors | 5,363,915,984 | 5.00 GiB |
| 36 | model-00036-of-00062.safetensors | 5,364,342,304 | 5.00 GiB |
| 37 | model-00037-of-00062.safetensors | 5,361,809,288 | 4.99 GiB |
| 38 | model-00038-of-00062.safetensors | 5,364,342,624 | 5.00 GiB |
| 39 | model-00039-of-00062.safetensors | 5,364,342,296 | 5.00 GiB |
| 40 | model-00040-of-00062.safetensors | 5,363,915,912 | 5.00 GiB |
| 41 | model-00041-of-00062.safetensors | 5,361,809,552 | 4.99 GiB |
| 42 | model-00042-of-00062.safetensors | 5,364,342,368 | 5.00 GiB |
| 43 | model-00043-of-00062.safetensors | 5,364,342,296 | 5.00 GiB |
| 44 | model-00044-of-00062.safetensors | 5,361,809,312 | 4.99 GiB |
| 45 | model-00045-of-00062.safetensors | 5,364,342,600 | 5.00 GiB |
| 46 | model-00046-of-00062.safetensors | 5,363,915,368 | 5.00 GiB |
| 47 | model-00047-of-00062.safetensors | 5,364,341,072 | 5.00 GiB |
| 48 | model-00048-of-00062.safetensors | 5,361,809,576 | 4.99 GiB |
| 49 | model-00049-of-00062.safetensors | 5,364,342,344 | 5.00 GiB |
| 50 | model-00050-of-00062.safetensors | 5,364,342,312 | 5.00 GiB |
| 51 | model-00051-of-00062.safetensors | 5,361,809,336 | 4.99 GiB |
| 52 | model-00052-of-00062.safetensors | 5,364,342,576 | 5.00 GiB |
| 53 | model-00053-of-00062.safetensors | 5,363,915,936 | 5.00 GiB |
| 54 | model-00054-of-00062.safetensors | 5,364,342,272 | 5.00 GiB |
| 55 | model-00055-of-00062.safetensors | 5,361,808,304 | 4.99 GiB |
| 56 | model-00056-of-00062.safetensors | 5,364,341,080 | 5.00 GiB |
| 57 | model-00057-of-00062.safetensors | 5,364,341,048 | 5.00 GiB |
| 58 | model-00058-of-00062.safetensors | 5,361,808,088 | 4.99 GiB |
| 59 | model-00059-of-00062.safetensors | 5,363,914,912 | 5.00 GiB |
| 60 | model-00060-of-00062.safetensors | 5,364,341,064 | 5.00 GiB |
| 61 | model-00061-of-00062.safetensors | 5,303,993,768 | 4.94 GiB |
| 62 | model-00062-of-00062.safetensors | 1,261,584,968 | 1.17 GiB |

**合计：328,337,455,672 字节 = 305.79 GiB = 328.34 GB**【事实】

### 1.2 小文件清单【事实】

| 文件 | size（字节） | 说明 |
|---|---|---|
| config.json | 69,416 | 模型配置 |
| model.safetensors.index.json | 8,406,613 | 张量↔分片映射索引 |
| tokenizer.json | 20,217,442 | 分词器 |
| README.md | 7,238 | 模型卡 |
| chat_template.jinja | 10,644 | 对话模板 |
| generation_config.json | 194 | 生成配置 |
| tokenizer_config.json | 761 | 分词器配置 |
| processor_config.json | 909 | 多模态处理器配置 |
| LICENSE | 1,070 | 协议 |
| .gitattributes | 1,570 | Git 属性 |

### 1.3 权重精度观察：分片头 dtype 实读结果【事实，非臆断】

分片文件名（`model-00001-of-00062`…）**不含** `-bf16` / `-fp8` 后缀，只能读取分片头确定精度。用 HTTP Range 下载分片 safetensors 头（前 8 字节 = header 长度，随后是 JSON 头）解析每个张量的 dtype，抽查 3 个分片：

| 分片 | tensor 总数 | dtype 分布（实例数） | 字节大头 |
|---|---|---|---|
| model-00001 | 664 | F32×329、BF16×6、F8_E4M3×329 | BF16≈2.60 GB、F8≈2.76 GB |
| model-00032 | 1,270 | F32×630、BF16×15、F8_E4M3×625 | 主体 F8 |
| model-00062 | 351 | **全部 BF16**（351 个） | 全 BF16（含尾部 embed/lm_head 等） |

**观察到的事实**：发布权重是 **混合精度** —— 主体为 FP8（F8_E4M3 动态量化），存在部分保持 BF16 的张量（与 config 的 `quantization_config.modules_to_not_convert`（含 embed、lm_head、indexer、attn 等）一致），以及少量 F32 张量（约百 KB 级，应为 scale 等辅助量）。【事实】；与【官方】模型卡 `Tensor: BF16·F8_E4M3·F32` 符合。

---

## 第 2 步：权重内存估算

### 方法 A（事实优先）

发布权重全部 62 个 safetensors 直接加载进显存的最小占用 = **328,337,455,672 字节 ≈ 305.79 GiB ≈ 328.34 GB**。【事实】

### 方法 B（参考核对）

官方口径总参数 320B【官方】：

| 假设精度 | 公式 | 理论值 |
|---|---|---|
| 全部 1 字节/参数（FP8） | 320e9 × 1 B | 320 GB |
| 全部 2 字节/参数（BF16） | 320e9 × 2 B | 640 GB |

**对照结论**：方法 A（328.34 GB）≈ 320B 参数×1B 的理论值（320 GB），差值约 8 GB（≈2.5%）。差异来源：【事实】dtype 抽样显示存在 BF16 分量（embed/lm_head/attn/indexer 等保精度张量按 2 字节存）+ F32 辅助张量 + safetensors 分片对齐填充/头部；这些高精度分量贡献约数 GB 级，恰好解释差值。**因此这批发布权重本质就是「FP8 为主、BF16 保精度」的已量化权重，而不是 BF16 原始权重**。【公式，基于 config + 事实抽样】

### 权重本身结论

- 按发布精度直接部署（推荐，与官方分片一致）：**约 306 GiB（328 GB）**。【事实】
- 若手动反量化成纯 BF16 部署：理论约 640 GB，约为发布体积 2 倍。【公式】

---

## 第 3 步：KV Cache 估算

### 3.1 MLA 主体 KV 缓存【公式，基于 config 字段】

依据 config 字段：
- MLA 低秩压缩 `kv_lora_rank = 512`【config】
- `qk_rope_head_dim = 0` → **无旋转 KV 分量**，缓存只存压缩后 latent【config】
- 假设：K 与 V 共用同一份 latent（MLA 的 K/V joint compression），**不乘 2**（若实现拆成两份，以下数值 ×2，标注为假设）【假设】
- 层数：45 层全部计（34 层 linear_attention + 11 层 deepseek_sparse_attention 都走 MLA latent 缓存）【config】

每层每 token = 512 维 latent × 字节数；45 层合计每 token：

| KV 精度 | 每层每 token | 45 层合计（每 token） |
|---|---|---|
| BF16（2 B/元素） | 1,024 B | 46,080 B = 45.0 KiB |
| 量化后（1 B/元素） | 512 B | 23,040 B = 22.5 KiB |

四档上下文结果（1M 按 1,000,000 token 计）【公式】：

| 上下文 | KV BF16 | KV BF16 | KV 1B/elem | KV 1B/elem |
|---|---|---|---|---|
| | **GiB** | **GB** | **GiB** | **GB** |
| 128K | 5.49 | 5.9 | 2.75 | 2.9 |
| 256K | 10.99 | 11.8 | 5.49 | 5.9 |
| 512K | 21.97 | 23.6 | 10.99 | 11.8 |
| 1M | 42.92 | 46.1 | 21.46 | 23.0 |

> 说明：若按 config 实际 `max_position_embeddings = 1,048,576`（精确 1M）计，上述 1M 行数值再 ×1.0486（约 <5% 差距）。【config → 公式】

*以上每行均为「基于 config 公式的推算」，非官方原文。*

### 3.2 DSA 层与 indexer 是否计入上述缓存

- **11 层 DSA（deepseek_sparse_attention）+ 34 层 linear_attention 全部计入**了上面 45 层主体 latent KV 缓存——即 DSA 层的 KV latent 已被上面公式覆盖（Sparse Attention 选中的 key 也是从这份 latent 展开）。【config → 公式；这是推算】
- **indexer 索引缓存（单独项）**：config 含 `index_head_dim=128, index_n_heads=32, index_topk=2048, index_kpool=4, index_types=[full]×45`【config】。是否在大上下文下长期驻留、驻留哪些层，**config 无法唯一确定，取决于实现**。若按「每 token 每层缓存 index key 全量、BF16」的最朴素假设推算一个量级：

| 假设 | 每 token 字节 | @1M（BF16） | @1M（1B/elem） | /kpool=4 量级 |
|---|---|---|---|---|
| 45 层全配 indexer | 32×128×2×45 = 368,640 B | ≈ 343 GiB | ≈ 172 GiB | ≈ 86 / 43 GiB |
| 仅 11 层 DSA 配 indexer | 32×128×2×11 = 90,112 B | ≈ 84 GiB | ≈ 42 GiB | ≈ 21 / 10 GiB |

> 【公式，纯假设推演】实际实现通常会做稀疏/分块（`index_topk=2048` 提示按 top-k 截断而非全量驻留），真实占用大概率远低于上表，**此量级仅作边界上限参考，需以官方实现为准**。

---

## 第 4 步：总显存/内存需求与硬件建议

### 4.1 组合表（权重 + KV，GiB）【公式】

单位 GiB；KV 取 BF16 与 1B/elem 两档。括号为含余量。

| 方案 | 上下文 | 权重 | KV | 总和 | +15% 余量【经验】 | +30% 余量【经验】 |
|---|---|---|---|---|---|---|
| W8（发布 FP8）+ KV 量化 | 128K | 305.8 | 2.9 | 308.7 | ≈ 355 | ≈ 401 |
| W8 + KV 量化 | 256K | 305.8 | 5.9 | 311.5 | ≈ 358 | ≈ 405 |
| W8 + KV 量化 | **1M** | 305.8 | 23.0 | **328.8** | ≈ 378 | ≈ 427 |
| W8 + KV BF16 | 128K | 305.8 | 5.9 | 311.5 | ≈ 358 | ≈ 405 |
| W8 + KV BF16 | 256K | 305.8 | 11.8 | 317.3 | ≈ 365 | ≈ 413 |
| W8 + KV BF16 | **1M** | 305.8 | 46.1 | **351.9** | ≈ 405 | ≈ 457 |
| W16（全 BF16，反量化） | 128K | 640 | 5.9 | 645.8 | ≈ 743 | ≈ 839 |
| W16 | 256K | 640 | 11.8 | 651.5 | ≈ 749 | ≈ 847 |
| W16 | **1M** | 640 | 46.1 | **686.1** | ≈ 789 | ≈ 892 |

> 余量（激活、CUDA context、框架/调度开销、分片对齐）为**行业经验系数**，非该模型实测；15% 为紧张档，30% 为宽松档。【经验】

### 4.2 关键洞察

1. 权重是绝对大头（305.8 GiB），196K 以下上下文改变 KV 的量级远小于权重；**换上下文几乎不改变显存门槛**。因此「只跑短上下文」只能减掉 <20 GB KV。【公式】
2. 官方发布即 FP8，**没有「640 GB BF16 部署」的常规必要性**；除非用户明确要反量化推理。【事实 + 公式】

### 4.3 最低硬件要求分档【公式 + 经验】

> 以下以发布精度部署（W8）为基准，按「可用显存 ≈ 标称×0.94」经验估算。N 卡 FP8 需 Hopper/Blackwell 系（H100/H200/B200）、A100/MI 系无原生 FP8 需回退；4090 无 FP8 加速但有 FP16，可布 W16 方案。

| 档位 | 需求（含余量） | 最低硬件组合建议【经验推估】 |
|---|---|---|
| ① 短上下文 32K–128K | 权重主导 ≈ 306–400 GiB（W8） | **4×H200(141G)/H20(96G)×4 起步**；或 5×80G H100；Mac M 系列需 ≥512 GB 统一内存（且依赖对 FP8 的框架支持） |
| ② 常见 256K | ≈ 311–405 GiB（W8） | 5×80G（H100/H20）+ NVLink/UMA；或 4×H200；或 M 系列 512–768 GB 统一内存（W8 或 W16） |
| ③ 目标 1M | ≈ 329–427 GiB（W8+KV量化）；W8+KV16 ≈ 405–457 GiB；W16 则 ≥789 GiB | **6–8×80G（H100/H200 系，8×80=640 GiB 裸卡余量充足）**；或 4×H200（564 GiB 裸卡）；或 M 系列 **≥768 GB** 统一内存（W16 下 1M 需要 800 GB 级） |

> 提示：以上「最低硬件组合」多用 80G 卡与统一内存的显存容量口径做判断；**未含卡间带宽/算力/推理速度评估**，仅回答「装得下」问题。【经验，范围限定】

### 4.4 来源性质汇总

| 类别 | 内容 |
|---|---|
| 官方/一级事实 | 分片数、分片字节大小、dtype 实测结果；官方总参 320B 口径；模型卡 Tensor 精度标注 |
| config 字段 | 全部架构数值（kv_lora_rank、层数、indexer 参数、max_position 等） |
| 公式推算 | KV 缓存系列数值、权重 × 精度核对、组合表 |
| 行业经验系数 | 激活/框架开销余量 15%/30%、可用显存系数 0.94、硬件组合建议 |
| 明确假设 | K/V 共享一份 latent（乘 2 备选）；indexer 驻留量级为上限假设，以官方实现为准 |

---

## 一句话结论

- **权重总字节**：328,337,455,672 B（≈305.79 GiB ≈ 328.34 GB，发布即 FP8+BF16 混合精度）【事实】
- **KV@1M 推算**：BF16 档约 42.9–46.1 GB、量化档约 21.5–23.0 GB（45 层 × 512 latent × 1M token，K/V 共享 latent）【公式】
- **推荐最低硬件**：1M 档建议 **6–8×80G H100/H200（或 ≥768 GB 统一内存）**；256K 档建议 **5×80G 或 4×H200（或 512–768 GB 统一内存）**【经验推估】