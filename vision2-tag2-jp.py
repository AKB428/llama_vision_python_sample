import ollama
import sys

inputImageFile = sys.argv[1]

response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[{
        'role': 'user',
        'content':  '''
        あなたは画像を読み込んで内容のタグを出力する役割をもったプログラムです。
        なんの画像かを読み込んで、この画像を表すタグ名を5つ選んでJSON形式で書いてください。
        例1 {"tag": ["虎", "動物", "公園", "女性","アイス"] }
        のような形で。
        タグ名は日本語にしてください。
        その他の文言は返さないでください。
        ''',
        'images': [inputImageFile]
    }]
)

print(response)
