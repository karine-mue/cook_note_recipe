import torch
from datasets import load_dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. ハードウェア境界制約の設定
max_seq_length = 2048
dtype = None
load_in_4bit = True

# 2. 基底モデルと復号器のロード
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Qwen/Qwen3-4B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
    trust_remote_code = True,
)

# 3. 勾配更新領域（LoRAアダプタ）の定義
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 42,
    use_rslora = False,
    loftq_config = None,
    layers_to_transform = list(range(18, 36)),  # 後半18層のみ
)

# 4. 高エントロピー流の接続
dataset = load_dataset("json", data_files="data/qwen3_4b_cpt_dataset_2048.jsonl", split="train")

# 5. 損失関数の最適化器（Trainer）の構築
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        # 【OOM発生時のフォールバック設定】
        # OOMが出た場合は以下のように変更し、実効バッチサイズ8を維持する:
        # per_device_train_batch_size = 1,
        # gradient_accumulation_steps = 8,
        per_device_train_batch_size = 1, 
        gradient_accumulation_steps = 8, 
        
        warmup_steps = 50,
        num_train_epochs = 1,
        learning_rate = 1e-5, # 保守的学習率（既存知識の保護）
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "cosine", # 学習終盤の安定化
        seed = 42,
        output_dir = "outputs_cpt",
        save_steps = 500,
    ),
)

# 6. 物理演算の開始
print("System: CPT Sequence Initiated. (LR: 1e-5, Scheduler: Cosine, Apply: latter 18 layers)")
trainer_stats = trainer.train()

# 7. 残滓の定着
model.save_pretrained("lora_qwen3_4b_cpt")
tokenizer.save_pretrained("lora_qwen3_4b_cpt")
print("System: Phase 1 Complete. Weights saved.")

# log保存 run_cpt.py末尾に追加
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/cpt_{timestamp}_lr{learning_rate}.log"

# あるいはteeコマンドで実行時にログ保存
# python run_cpt.py 2>&1 | tee logs/cpt_$(date +%Y%m%d_%H%M%S).log