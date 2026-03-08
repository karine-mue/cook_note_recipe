# 0. 「呪文」（Google Driveのマウント）
from google.colab import drive
drive.mount('/content/drive')

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
html_files = glob.glob(os.path.join(extract_path, "**/*.html"), recursive=True)

for html_path in html_files:
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
        title = soup.find('h1').get_text() if soup.find('h1') else "No Title"
        content = soup.find('div', class_='note-common-styles__text-post-content')
        if not content:
             content = soup.find('main')
        
        text = content.get_text(separator='\n').strip() if content else ""
        
        if text:
            corpus.append({"title": title, "body": text})

# 4. JSONLとして保存
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in corpus:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"完了！ 保存先: {output_file}")
print(f"抽出記事数: {len(corpus)} 件")
