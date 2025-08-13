import os
import shutil
from pathlib import Path
from flask import jsonify
from .preprocess import PreProcess
from .postprocess import result_custom, extract_info_ja, draw_pre, draw_info
from paddleocr import PaddleOCR
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
        file = request.files['file'] #画像の受け取り
        filename = file.filename
        img_path = str(basedir / "data" / "input" /filename)
        file.save(img_path)

        #前処理
        pre_process = PreProcess(img_path)
        img_path = pre_process.preprocess_default()
    except Exception as e:
        print(e)
        return handle_error("前処理部分での想定外のエラー" + str(e), img_path, result_save_path), 400

    '''
    推論：PaddleOCRで推論
    '''
    try:
        #使用するモデル定義
        det_model = './api/model/det/ch_PP-OCRv3_det_infer.onnx'
        rec_model = './api/model/rec/japan_PP-OCRv3_rec_infer.onnx'
        cls_model = './api/model/cls/ch_ppocr_mobile_v2.0_cls_infer.onnx'
        cpu_threads = 6
        
        #クラス定義
        ocr = PaddleOCR(use_angle_cls=True, lang='japan', use_gpu=False, enable_mkldnn=True, cpu_threads=cpu_threads, use_onnx=True, det_model_dir=det_model, rec_model_dir=rec_model, cls_model_dir=cls_model)  # 日本語OCR

        #推論
        ocr_result = ocr.ocr(img_path)
     
    except Exception as e:
        print(e)
        return handle_error("AI推論時の想定外のエラー", img_path, result_save_path), 400

    '''
    後処理
    '''
    try:
        #抜きだしたい部分の抜き取り
        result_ja = extract_info_ja(ocr_result)
        print(result_ja['sum'])

        #BBOX部分の座標整理
        bbox_list = draw_pre(result_ja['total_amount_bbox'])

        #bboxを引く処理
        result_save_path = draw_info(img_path, bbox_list)

        #結果を返す
        result_data = result_custom(result_save_path, result_ja)

        return jsonify(result_data)

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