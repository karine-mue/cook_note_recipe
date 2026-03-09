# 0. Googleドライブのマウント
from google.colab import drive
drive.mount('/content/drive')

import json
import numpy as np

file_path = '/content/drive/MyDrive/qwen_sft_dialogues.jsonl'

total_threads = 0
turn_counts = []
user_chars_total = 0
assistant_chars_total = 0

print("Phase 0.5: SFTコーパスの統計解析を開始します...")

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        messages = data.get("messages", [])
        
        total_threads += 1
        turn_counts.append(len(messages))
        
        for msg in messages:
            role = msg.get("role")
            content_len = len(msg.get("content", ""))
            
            if role == "user":
                user_chars_total += content_len
            elif role == "assistant":
                assistant_chars_total += content_len

# 統計量の計算
avg_turns = np.mean(turn_counts)
max_turns = np.max(turn_counts)
min_turns = np.min(turn_counts)

print("="*40)
print(f"【コーパス統計情報】")
print(f"総スレッド数 (Total Threads): {total_threads}")
print(f"総ターン数 (Total Turns)    : {sum(turn_counts)}")
print(f"平均ターン/スレッド         : {avg_turns:.2f}")
print(f"最大ターン/スレッド         : {max_turns}")
print(f"最小ターン/スレッド         : {min_turns}")
print("-" * 40)
print(f"User総文字数                : {user_chars_total:,}")
print(f"Assistant総文字数           : {assistant_chars_total:,}")
if user_chars_total > 0:
    print(f"A/U 文字数比率              : {assistant_chars_total / user_chars_total:.2f}")
print("="*40)
