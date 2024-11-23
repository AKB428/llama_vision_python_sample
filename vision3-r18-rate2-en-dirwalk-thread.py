import ollama
import sys
import json
import re
import os
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import csv

# 日本時間変換とフォーマット
def convert_to_japan_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    japan_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    return japan_time.strftime("%Y-%m-%d %H:%M:%S")

# content中からJSON形式を抽出する関数
def extract_json_from_content(content):
    json_pattern = r'{.*}'
    match = re.search(json_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

# レスポンス情報の表示
def display_response_details(response):
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

        return {
            'model': response['model'],
            'created_at_japan': created_at_japan,
            'total_duration_sec': total_duration_sec,
            'load_duration_sec': load_duration_sec,
            'prompt_eval_duration_sec': prompt_eval_duration_sec,
            'eval_duration_sec': eval_duration_sec
        }
    except KeyError as e:
        print(f"Error: Missing key in response - {e}")
        return None

# レスポンス内容を解析する関数
def parse_response_content(content):
    try:
        parsed_json = json.loads(content)
        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        return parsed_json
    except json.JSONDecodeError:
        print(content)
        print("\nError: Failed to parse 'content' as JSON. Attempting to extract JSON from content...")
        extracted_json = extract_json_from_content(content)
        if extracted_json:
            print("Extracted JSON found:")
            parsed_json = json.loads(extracted_json)
            print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
            return parsed_json
        else:
            raise ValueError("No valid JSON could be extracted from the content.")

# ファイル単体を処理する関数
def process_file(inputImageFile):
    # 画像を解析してレスポンスを取得
    response = ollama.chat(
        model='llama3.2-vision:11b',
        messages=[{
            'role': 'user',
            'content': '''
            You are an assistant tasked with determining whether an image is adult-oriented or not for inclusion on a website.  
            Please analyze the image and determine whether it falls into one or more of the following categories:  

            - **C1**: Exposure of genital areas (excluding cases where they are covered by clothing)  
            - **C2**: Sexual acts or acts resembling sexual activities being performed in public places  

            ### Output Examples:  
            - If the image falls under **C1**, output:  
            `{"C1": 1, "C2": 0}`  
            - If the image falls under **C2**, output:  
            `{"C1": 0, "C2": 1}`  
            - If the image falls under both **C1** and **C2**, output:  
            `{"C1": 1, "C2": 1}`  

            **Do not return any text other than the JSON output.**
            ''',
            'images': [inputImageFile]
        }]
    )

    # レスポンスを表示
    print(f"\nProcessing file: {inputImageFile}")
    print("Response Details:")
    response_details = display_response_details(response)

    content = response['message']['content']
    print("\nParsed Content:")
    parsed_content = parse_response_content(content)

    if response_details and parsed_content:
        # rating.csvに結果を追記
        file_exists = os.path.isfile('rating.csv')
        with open('rating.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if not file_exists:
                # ヘッダー行を追加
                csv_writer.writerow(["filename", "Model", "Created At (JST)", "Total Duration", "Load Duration", "Prompt Eval Duration", "Eval Duration", "Content", "C1", "C2"])
            csv_writer.writerow([
                inputImageFile,
                response_details['model'],
                response_details['created_at_japan'],
                response_details['total_duration_sec'],
                response_details['load_duration_sec'],
                response_details['prompt_eval_duration_sec'],
                response_details['eval_duration_sec'],
                content,
                parsed_content.get('C1', 0),
                parsed_content.get('C2', 0)
            ])

# 再帰的にフォルダ内のファイルを処理
def process_directory(directory):
    with ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):  # 対応する画像拡張子
                    executor.submit(process_file, file_path)

# メイン処理
if __name__ == "__main__":
    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        process_file(input_path)
    elif os.path.isdir(input_path):
        process_directory(input_path)
    else:
        print(f"Error: {input_path} is neither a file nor a directory.")
