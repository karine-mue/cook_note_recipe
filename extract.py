import os
import zipfile
import glob
from bs4 import BeautifulSoup
import json

# 1. パスの設定
drive_path = "/content/drive/MyDrive/note_export_temp/"
extract_path = "/content/extracted_note/"
output_file = "/content/note_corpus.jsonl"

# 2. 解凍処理 (3つのzipを一括処理)
os.makedirs(extract_path, exist_ok=True)
zip_files = glob.glob(os.path.join(drive_path, "a1*.zip"))

print(f"解凍開始: {len(zip_files)}個のファイルを処理中...")
for z in zip_files:
    with zipfile.ZipFile(z, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# 3. テキスト抽出プロセス
print("テキスト抽出中...")
corpus = []
# noteのエクスポート構造に合わせてパスを調整（通常は /html/ フォルダ内）
html_files = glob.glob(os.path.join(extract_path, "**/*.html"), recursive=True)

for html_path in html_files:
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
        # タイトルと本文の取得（noteの構造に依存）
        title = soup.find('h1').get_text() if soup.find('h1') else "No Title"
        # 本文領域を指定（クラス名はnoteの仕様により変動の可能性あり）
        content = soup.find('div', class_='note-common-styles__text-post-content')
        if not content:
             content = soup.find('main') # フォールバック
        
        text = content.get_text(separator='\n').strip() if content else ""
        
        if text:
            corpus.append({"title": title, "body": text})

# 4. JSONLとして保存
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in corpus:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"完了！ 保存先: {output_file}")
print(f"抽出記事数: {len(corpus)} 件")
