from unsloth import FastLanguageModel

# 1. 保存したアダプタのロード（既にメモリ上にある場合はスキップ可）
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "outputs_cpt/checkpoint-3762", # 学習直後のパス
    max_seq_length = 2048,
    load_in_4bit = True,
)

# 2. GGUF変換（Merge込み）
# 推奨: q5_k_m (12GB VRAMで推論するのに最適)
model.save_pretrained_gguf(
    "model_gguf_q5_3e5", 
    tokenizer, 
    quantization_method = "q5_k_m"
)

# 2. GGUF変換（Merge込み）
# 推奨: q4_k_m (12GB VRAMで推論するのに最適)
model.save_pretrained_gguf(
    "model_gguf_q4_3e5", 
    tokenizer, 
    quantization_method = "q4_k_m"
)

# 3. 必要ならHFへ直接GGUFを投げる（これもPrivateなら1ファイルのみで済む）
# model.push_to_hub_gguf(
#     "karine_tln/your-model-name-gguf", 
#     tokenizer, 
#     quantization_method = "q5_k_m",
#     private = True
# )