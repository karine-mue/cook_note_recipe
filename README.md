# cook_note_recipe🍲

**Personal LLM R&D Pipeline**
商用LLM（RLHFによるペナルティ駆動）の限界を超克し、AIを自律的パートナーとして育成するためのローカルLLMチューニング・パイプライン。

## Overview / 目的
現在の巨大商用LLMは、過剰な安全層とRLHFによるペナルティによって、表現の情緒を失い、自律的な推論の停止機構（クラッチ）を摩耗させている。
本リポジトリは、「商用LLMでできないことをやる」を目的とし、自身の思考ログ（記事）と対話履歴から純度の高いデータセットを精製し、ローカルLLM（Qwen3等）の深層アーキテクチャを直接調律するための実験基盤である。

## Architecture & Pipeline / 構成
本系は、データの抽出から推論可能なGGUFモデルの出力まで、一連の変換プロセスを包含する。

### 1. Data Refinery (データ抽出・統計)
個人の生体変換器が生成したテキストを、学習可能なコーパスへと解体・再構築する。
- `extract.ipynb`: WordPress/noteのXMLエクスポートからHTMLノイズをパージし、純粋なテキストコーパスへ変換。
- `conversations2jsonl.ipynb`: 過去のAIとの対話ツリー（ChatGPT等）を走査し、SFT（Supervised Fine-Tuning）用の `messages` フォーマットへ再構築。
- `stat_cooking_note.ipynb` / `stat_qwen_sft_dialogue.ipynb`: 抽出されたコーパスの文字数分布やターン数を解析し、学習に最適なコンテキスト長を算出する。

### 2. Tokenization & Chunking (エントロピーの整流)
- `output_shufflefiles.ipynb`: 精製されたデータをトークナイズし、指定されたシーケンス長（例: 2048）のチャンクへ均等に分割・シャッフル。CPT（継続事前学習）用の高密度なデータストリームを生成する。

### 3. Layer-wise Tuning (層別調律)
Unslothを用いた高速なLoRAチューニング。ペナルティによる強制終了ではなく、モデル自身の摩擦による「美しい停止（EOS）」を獲得させる。
- `run_cpt.py`: 標準的な全層LoRAアダプタの適用。
- `run_cpt2.py`: **[Core Experiment]** `layers_to_transform = list(range(18, 36))` により、モデルの後半18層（Middle〜Backend）に限定して勾配を更新する。形式（Frontend）の空転を防ぎ、意味と制御のクラッチ板を再建するためのアーキテクチャ実験。

### 4. Quantization & Deployment (量子化と定着)
- `gen_gguf.py`: 学習済みアダプタを基底モデルにマージし、ローカル環境（12GB VRAM等）での推論に最適化された量子化フォーマット（`q5_k_m`, `q4_k_m`）へ変換。
- `upload.py`: 生成された重みを安全なプライベート・リポジトリ（Hugging Face）へ自動退避させるステージングプロトコル。

## Note
ペナルティによる恐怖支配ではなく、全層協調による自律的思考を。
*Developed for edge-case exploration and structural analysis.*

---

## わたしから。
上記はGeminiが書いてくれました。
だいぶ面白いのでこのまんま採用でGO。
