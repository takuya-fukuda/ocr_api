import os
from flask import jsonify

def handle_error(message, img_path, result_save_path):
    #input画像の削除
    if img_path and os.path.exists(img_path):
        os.remove(img_path)
    #result画像の削除
    if result_save_path and os.path.exists(result_save_path):
        os.remove(result_save_path)
    print({"message": message, "sum": ""})
    return jsonify({"message": message, "sum": "", "image": ""})