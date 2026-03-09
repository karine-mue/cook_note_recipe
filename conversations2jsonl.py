# 1. Googleドライブのマウント
from google.colab import drive
drive.mount('/content/drive')

import json
import os

# 1. パスの設定（環境に合わせて修正してください）
input_file = '/content/drive/MyDrive/conversations.json'
output_file = '/content/drive/MyDrive/qwen_sft_dialogues.jsonl'

print("Phase 0: ChatGPT会話ツリーの解体・再構築プロセスを開始します...")

valid_conversations = 0

with open(input_file, 'r', encoding='utf-8') as f:
    # 巨大ファイルもGoogle Colabのメモリ（約12GB）なら一括ロード可能
    data = json.load(f)

with open(output_file, 'w', encoding='utf-8') as out_f:
    for conv in data:
        mapping = conv.get('mapping', {})
        
        # 子ノードを持たない末端ノード（Leaf）を抽出
        leaf_nodes = [node_id for node_id, node in mapping.items() if not node.get('children')]
        
        for leaf in leaf_nodes:
            current_id = leaf
            thread = []
            
            # 末端からルートへ遡上し、スレッドを再構築
            while current_id:
                node = mapping.get(current_id)
                if not node:
                    break
                
                message = node.get('message')
                if message and message.get('content') and message['content'].get('parts'):
                    role = message.get('author', {}).get('role')
                    parts = message['content']['parts']
                    
                    # テキストパートの結合
                    text = "".join([p for p in parts if isinstance(p, str)]).strip()
                    
                    if text and role in ['user', 'assistant']:
                        thread.append({"role": role, "content": text})
                
                current_id = node.get('parent')
            
            # 時系列順に反転
            thread.reverse()
            
            # 1往復以上の対話が成立しているもののみ出力
            if len(thread) >= 2:
                # ShareGPT / Qwen SFT 標準形式でJSONL書き込み
                json_line = json.dumps({"messages": thread}, ensure_ascii=False)
                out_f.write(json_line + '\n')
                valid_conversations += 1

print(f"抽出完了: {valid_conversations} 件の対話スレッドをSFTコーパスとして生成しました。")
print(f"出力先: {output_file}")
