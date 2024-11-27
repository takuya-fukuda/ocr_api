import requests
import base64
import json
import os
from dotenv import load_dotenv
load_dotenv()

def save_response_to_file(response_data, file_name="response.json"):
    """
    レスポンスデータをJSONファイルとして保存する

    Args:
        response_data (dict): APIレスポンスデータ
        file_name (str): 保存するファイル名
    """
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)
    print(f"JSON response saved to {file_path}")

def get_description_from_response(response):
    """
    レスポンスから最初のdescriptionを取得する

    Args:
        response (dict): APIレスポンスデータ

    Returns:
        str: 最初のdescriptionテキスト、または空文字
    """
    annotations = response.get("responses", [])[0].get("textAnnotations", [])
    if annotations:
        return annotations[0]["description"]
    return ""

def description_to_list(description):
    """
    descriptionを改行で分割してリストにする

    Args:
        description (str): descriptionテキスト

    Returns:
        list: 改行で分割されたリスト
    """
    return description.split("\n")

def detect_text_with_api_key(api_key, img_path):
    # Cloud Vision APIのエンドポイント
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    # 画像ファイルをBase64エンコード
    with open(img_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    
    # リクエストペイロード
    payload = {
        "requests": [
            {
                "image": {
                    "content": encoded_image
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }
    
    # POSTリクエストを送信
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # レスポンスを解析
    if response.status_code == 200:
        response_data = response.json()

        # 最初のdescriptionを取得
        description = get_description_from_response(response_data)

        if description:
            print("Extracted Description:")
            print(description)

            # 改行で分割したリストを返す
            return description_to_list(description)
        else:
            print("No text detected in the response.")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []