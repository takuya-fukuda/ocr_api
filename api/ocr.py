import os
import shutil
from pathlib import Path
from flask import jsonify
from .preparation import load_image, extension_split, heic_convert
from .postprocess import result_custom, search_word
#from paddleocr import PaddleOCR
from .yomitoku_ocr import get_analyzer, test_ocr
from .error import handle_error

basedir = Path(__file__).parent.parent

def ocr_func(request):
    #初期化
    img_path=None #Except部分でエラーが出るので初期化
    result_save_path=None #Except部分でエラーが出るので初期化

    '''
    前処理
    '''
    try:
        img_path, filename = load_image(request)

        #ファイル名チェック
        if filename == '':
            return jsonify('ファイル名が空です')
        
        # ファイルのロードに失敗した場合の処理
        if img_path is None:
            return jsonify({"message": 'ファイルが空です', "sum": "", "image": ""}), 400

        # ファイル名チェック
        if filename == '' or filename is None:
            return jsonify({"message": 'ファイル名が空です', "sum": "", "image": ""}), 400
   
        #拡張子チェック
        ext = extension_split(img_path)
        if ext.lower() not in [".jpeg", ".jpg", ".png", ".heic"]:
            return jsonify({"message": 'AIがファイル拡張子に対応していません', "sum": "", "image": ""}), 400

        #HEICのJPEG変換
        if ext == ".HEIC":
            img_path = heic_convert(img_path)
            

    except Exception as e:
        print(e)
        return handle_error("前処理部分での想定外のエラー", img_path, result_save_path), 400

    '''
    推論：yomitokuで推論
    '''
    try:
        # Analyzerの初期化
        analyzer = get_analyzer()
        ocr_result = test_ocr(img_path, analyzer)

    except Exception as e:
        print(e)
        return handle_error("AI推論時の想定外のエラー", img_path, result_save_path), 400

    '''
    後処理
    '''
    try:
        #抜きだしたい部分の抜き取り
        result = search_word(ocr_result)
        print(result['sum'])

        return jsonify(result)

    except Exception as e:
        print(e)
        return handle_error("AI推論後の後処理で想定外のエラー：", img_path, result_save_path), 400

    finally:
        #インプットイメージの削除
        if img_path and os.path.exists(img_path):
            os.remove(img_path)

        #OCR結果イメージの削除
        if result_save_path and os.path.exists(result_save_path):
            os.remove(result_save_path)