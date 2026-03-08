import os
import glob
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

# すでに解凍済みのパスを指定
extract_path = "/content/extracted_note/"
output_file = "/content/note_corpus.jsonl"

def clean_html(html_content):
    if not html_content:
        return ""
    # HTMLタグを除去し、プレーンテキストを抽出
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")
    # 余分な連続改行を圧縮（3行以上続く空行を2行に）
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

corpus = []
# XMLファイルを捕捉
xml_files = glob.glob(os.path.join(extract_path, "**/*.xml"), recursive=True)
print(f"発見されたXMLファイル: {len(xml_files)}件")

# WordPress互換XMLの名前空間定義
ns = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/'
}

for xml_file in xml_files:
    print(f"XML解析中: {xml_file}")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 全ての記事ノードを走査
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else "No Title"
            
            # content:encoded から本文（HTML埋め込みテキスト）を取得
            content_elem = item.find('content:encoded', ns)
            content_raw = content_elem.text if content_elem is not None else ""
            
            text = clean_html(content_raw)
            if text:
                corpus.append({"title": title, "body": text})
                
    except Exception as e:
        print(f"パースエラー ({xml_file}): {e}")

# JSONLとして保存
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in corpus:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"完了！ 保存先: {output_file}")
print(f"抽出記事数: {len(corpus)} 件")
