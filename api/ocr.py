import os
import shutil
from pathlib import Path
from flask import jsonify
from .preparation import load_image, extension_split, heic_convert
from .postprocess import result_custom, extract_info_ja, draw_pre, draw_info, search_total
#from paddleocr import PaddleOCR
from .visionapi_ocr import detect_text_with_api_key
from .error import handle_error
from dotenv import load_dotenv
load_dotenv()

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
    推論：PaddleOCRで推論
    '''
    try:
        #使用するモデル定義
        # det_model = './api/model/det/ch_PP-OCRv3_det_infer.onnx'
        # rec_model = './api/model/rec/japan_PP-OCRv3_rec_infer.onnx'
        # cls_model = './api/model/cls/ch_ppocr_mobile_v2.0_cls_infer.onnx'
        # cpu_threads = 6
        
        #クラス定義
        #ocr = PaddleOCR(use_angle_cls=True, lang='japan', use_gpu=False, enable_mkldnn=True, cpu_threads=cpu_threads, use_onnx=True, det_model_dir=det_model, rec_model_dir=rec_model, cls_model_dir=cls_model)  # 日本語OCR

        api_key=os.getenv("API_KEY")

        #推論
        #ocr_result = ocr.ocr(img_path)
        ocr_result = detect_text_with_api_key(api_key, img_path)

    except Exception as e:
        print(e)
        return handle_error("AI推論時の想定外のエラー", img_path, result_save_path), 400

    '''
    後処理
    '''
    try:
        #抜きだしたい部分の抜き取り
        #result_ja = extract_info_ja(ocr_result)
        result = search_total(ocr_result)
        print(result['sum'])

        #BBOX部分の座標整理
        #bbox_list = draw_pre(result_ja['total_amount_bbox'])

        #bboxを引く処理
        #result_save_path = draw_info(img_path, bbox_list)

        #結果を返す
        # result_data = result_custom(result)

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