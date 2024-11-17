import ollama
import sys
import json
import re
import csv
from datetime import datetime, timedelta, timezone
import os  # ファイルの存在確認に使用

inputImageFile = sys.argv[1]
csv_file = "output.csv"

# 画像を解析してレスポンスを取得
response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[{
        'role': 'user',
        'content': '''
        あなたは画像を読み込んで内容のタグを出力する役割をもったプログラムです。
        なんの画像かを読み込んで、この画像を表すタグ名を5つ選んでJSON形式で書いてください。
        またこの画像が成人向けなら "rating": "R18", そうでないなら "rating": "general" の値を加えてください
        例1 {"tag": ["虎", "動物", "公園", "女性","アイス"], "rating": "general" }
        のような形で。
        タグ名は日本語にしてください。
        JSON以外の文字列は返答しないでください。
        ''',
        'images': [inputImageFile]
    }]
)

# 日本時間変換とフォーマット
def convert_to_japan_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    japan_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    return japan_time.strftime("%Y-%m-%d %H:%M:%S")

# content中からJSON形式を抽出する関数
def extract_json_from_content(content):
    json_pattern = r'{.*"tag".*}'
    match = re.search(json_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

# CSV追記書き込み
def append_to_csv(filename, model, created_at, total_duration, load_duration, prompt_eval_count,
                  prompt_eval_duration, eval_count, eval_duration, content, tags, rating):
    # ヘッダー行を定義
    headers = [
        "filename", "Model", "Created At (JST)", "Total Duration", "Load Duration", 
        "Prompt Eval Count", "Prompt Eval Duration", "Eval Count", "Eval Duration", 
        "content", "tag1", "tag2", "tag3", "tag4", "tag5", "rating"
    ]
    # ファイルが存在しない場合はヘッダーを追加
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)  # ヘッダー行の書き込み
        # データ行の書き込み
        row = [
            filename, model, created_at, f"{total_duration:.2f}s", f"{load_duration:.2f}s",
            prompt_eval_count, f"{prompt_eval_duration:.2f}s", eval_count, f"{eval_duration:.2f}s",
            content
        ] + tags + [""] * (5 - len(tags)) + [rating]  # タグが5つ未満の場合は空文字を追加
        writer.writerow(row)

# レスポンスをきれいに表示
print("Response Details:")
try:
    created_at_japan = convert_to_japan_time(response['created_at'])
    total_duration_sec = response['total_duration'] / 1_000_000_000
    load_duration_sec = response['load_duration'] / 1_000_000_000
    prompt_eval_duration_sec = response['prompt_eval_duration'] / 1_000_000_000
    eval_duration_sec = response['eval_duration'] / 1_000_000_000

    print(f"  Model: {response['model']}")
    print(f"  Created At (JST): {created_at_japan}")
    print(f"  Total Duration: {total_duration_sec:.2f}s")
    print(f"  Load Duration: {load_duration_sec:.2f}s")
    print(f"  Prompt Eval Count: {response['prompt_eval_count']}")
    print(f"  Prompt Eval Duration: {prompt_eval_duration_sec:.2f}s")
    print(f"  Eval Count: {response['eval_count']}")
    print(f"  Eval Duration: {eval_duration_sec:.2f}s")

    content = response['message']['content']
    print("\nParsed Content:")
    tags = []
    rating = ""
    try:
        parsed_json = json.loads(content)
        tags = parsed_json.get("tag", [])
        rating = parsed_json.get("rating", "")
    except json.JSONDecodeError:
        print(content)
        print("\nError: Failed to parse 'content' as JSON. Attempting to extract JSON from content...")
        extracted_json = extract_json_from_content(content)
        if extracted_json:
            print("Extracted JSON found:")
            parsed_json = json.loads(extracted_json)
            tags = parsed_json.get("tag", [])
            rating = parsed_json.get("rating", "")
        else:
            print("No valid JSON could be extracted from the content.")
    finally:
        # CSV書き込み
        append_to_csv(
            filename=inputImageFile,
            model=response['model'],
            created_at=created_at_japan,
            total_duration=total_duration_sec,
            load_duration=load_duration_sec,
            prompt_eval_count=response['prompt_eval_count'],
            prompt_eval_duration=prompt_eval_duration_sec,
            eval_count=response['eval_count'],
            eval_duration=eval_duration_sec,
            content=content,
            tags=tags,
            rating=rating
        )
        print("Data appended to CSV.")

    print(json.dumps({"tag": tags, "rating": rating}, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\nUnexpected Error: {e}")
