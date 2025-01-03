import ollama
import sys
import json
from datetime import datetime, timedelta, timezone

inputImageFile = sys.argv[1]

# 画像を解析してレスポンスを取得
response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[{
        'role': 'user',
        'content': '''
        この画像の麻雀のコマに書いてある文字や模様を読み取り、文字に起こしてください。
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

    content = response['message']['content']
    print(content)

except json.JSONDecodeError:
    print("\nError: Failed to parse 'content' as JSON.")
    print(f"Raw Content: {response['message']['content']}")
except KeyError as e:
    print(f"\nError: Missing key in response: {e}")
except Exception as e:
    print(f"\nUnexpected Error: {e}")
