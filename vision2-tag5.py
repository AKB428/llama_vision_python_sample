import ollama
import sys
import json
import re
from datetime import datetime, timedelta, timezone

inputImageFile = sys.argv[1]

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
    # 余分な小数点以下をトリム
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    # UTC形式をdatetimeオブジェクトに変換し、タイムゾーンを明示
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    # 日本時間（UTC+9）に変換
    japan_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    # 日本時間をフォーマット
    return japan_time.strftime("%Y-%m-%d %H:%M:%S")

# content中からJSON形式を抽出する関数
def extract_json_from_content(content):
    json_pattern = r'{.*"tag".*}'
    match = re.search(json_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

# レスポンスをきれいに表示
print("Response Details:")
try:
    # 時間の変換
    created_at_japan = convert_to_japan_time(response['created_at'])

    # 秒に変換して表示
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

    # JSONパースを試行
    content = response['message']['content']
    print("\nParsed Content:")
    try:
        parsed_json = json.loads(content)  # JSONパース
    except json.JSONDecodeError:
        # JSONパースエラーが発生した場合、contentからJSON部分を抽出
        print("\nError: Failed to parse 'content' as JSON. Attempting to extract JSON from content...")
        extracted_json = extract_json_from_content(content)
        if extracted_json:
            print("Extracted JSON found:")
            parsed_json = json.loads(extracted_json)
        else:
            raise ValueError("No valid JSON could be extracted from the content.")

    # 抽出・パースしたJSONをきれいに整形して表示
    print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

except json.JSONDecodeError:
    print("\nError: Unable to parse content into JSON and no valid JSON could be extracted.")
    print(f"Raw Content: {response['message']['content']}")
except KeyError as e:
    print(f"\nError: Missing key in response: {e}")
except Exception as e:
    print(f"\nUnexpected Error: {e}")
