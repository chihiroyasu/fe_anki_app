from flask import Flask, render_template, jsonify
import json
import os

# --- アプリケーションのインスタンス化（1回のみ） ---
app = Flask(__name__)

# JSONファイルのパス
# Vercel環境では、このファイルはapi/index.pyと同じディレクトリ階層にある必要があります
JSON_FILE_PATH = 'fe_keywords_data.json' 
# カードのデータ格納用
FLASHCARDS_DATA = []

def load_flashcards_data():
    """JSONファイルを読み込み、カード形式のフラットリストに変換する"""
    global FLASHCARDS_DATA
    
    # Vercelの環境では、カレントディレクトリが異なる場合があるため、
    # 実行中のファイルのディレクトリからファイルを読み込むのが安全です。
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, JSON_FILE_PATH)

    if not os.path.exists(file_path):
        # ログメッセージを返す
        FLASHCARDS_DATA = [{"term": "データが見つかりません", "definition": f"ファイルパス: {file_path}", "category": "エラー", "sub_category": "エラー"}]
        print(f"エラー: {file_path} が見つかりません。")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        nested_data = json.load(f)
        
    flat_list = []
    # 大分類（例: "1 基礎理論"）をループ
    for major_cat, sub_categories in nested_data.items():
        # 中分類（例: "離散数学"）をループ
        for sub_cat, keywords in sub_categories.items():
            # キーワード（用語と説明）をループ
            for item in keywords:
                flat_list.append({
                    "term": item['用語'],
                    "definition": item['説明'],
                    "category": major_cat,
                    "sub_category": sub_cat
                })
                
    FLASHCARDS_DATA = flat_list
    print(f"✅ {len(FLASHCARDS_DATA)} 件のカードをロードしました。")

# アプリケーション起動時にデータをロード（1回のみ実行）
load_flashcards_data()


@app.route('/')
def index():
    """トップページ（暗記カード画面）を表示する"""
    # HTMLテンプレートをレンダリング
    return render_template('index.html', total_cards=len(FLASHCARDS_DATA))


@app.route('/api/cards', methods=['GET'])
def get_cards():
    """全カードデータをJSON形式で返すAPIエンドポイント"""
    # データをそのまま返す
    return jsonify(FLASHCARDS_DATA)


# --- Vercel Serverless Functionとして公開するために必須 ---
# Flaskアプリケーションのインスタンスを'application'という名前で公開します。
application = app