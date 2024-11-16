import ollama
import sys

inputImageFile = sys.argv[1]

response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content':  '''
        なんの画像かを読み込んで、この画像を表すタグ名を5つ選んでJSON形式で書いてください。
        例1 {tag: ["虎", "動物", "公園", "女性","アイス"] }
        のような形で。その他の文言は返さないでください。
        ''',
        'images': [inputImageFile]
    }]
)

print(response)
