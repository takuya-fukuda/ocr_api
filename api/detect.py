import os
import shutil
from pathlib import Path
from flask import jsonify
from .preparation import load_image
from .postprocess import result_custom, extract_info_ja, extract_info_ch, draw_pre, draw_info
from .paddleocr_dev import OCRProcessor

basedir = Path(__file__).parent.parent

def detection(request):
    '''
    前処理
    '''
    try:
        dir_image, filename = load_image(request)

        #ファイル名チェック
        if filename == '':
            return jsonify('ファイル名が空です')
        
        #拡張子チェック

    except Exception as e:
        #インプットイメージの削除
        if dir_image and os.path.exists(dir_image):
            os.remove(dir_image)
        print({"message": "拡張子エラーorファイル名もしくはファイルが空orそれ以外の例外エラー"+str(e), "race": "", "date": "", "sum": "", "uid": "", "image": ""})
        return jsonify({ "message": "拡張子のエラーorファイル名もしくはファイルが空orそれ以外の例外エラー。", "race": "", "date": "", "sum": "", "uid": "", "image": ""}), 400

    '''
    推論：PaddleOCRで推論
    '''
    try:
        #使用するモデル定義
        ja_model = './api/ppocr_onnx/model/rec_model/japan_PP-OCRv3_rec_infer.onnx'
        ja_dict = './api/ppocr_onnx/ppocr/utils/dict/japan_dict.txt'
        ch_model = './api/ppocr_onnx/model/rec_model/chinese_cht_PP-OCRv3_rec_infer.onnx'
        ch_dict = './api/ppocr_onnx/ppocr/utils/dict/chinese_cht_dict.txt'
        
        #クラス呼び出し
        predict_ja = OCRProcessor(dir_image, ja_model, ja_dict)
        predict_ch = OCRProcessor(dir_image, ch_model, ch_dict)

        #推論
        ja_boxes, ja_rec, ja_time = predict_ja.process_image()
        ch_boxes, ch_rec, ch_time = predict_ch.process_image()
     
    except Exception as e:
        #インプットイメージの削除
        if dir_image and os.path.exists(dir_image):
            os.remove(dir_image)
        print({ "message": "AIの推論時に想定外のエラーが発生しております。："+str(e), "race": "", "date": "", "sum": "", "uid": "", "image": ""})
        return jsonify({ "message": "AIの推論時に想定外のエラーが発生しております。", "race": "", "date": "", "sum": "", "uid": "", "image": ""}), 400

    '''
    後処理
    '''
    try:
        #抜きだしたい部分の抜き取り
        result_ja = extract_info_ja(ja_boxes, ja_rec)
        result_ch = extract_info_ch(ch_boxes, ch_rec)
        print(result_ja['race'], result_ch['date'], result_ch['sum'], result_ch['uid'])

        #BBOX部分の座標整理
        bbox_list = draw_pre(result_ja['race_bbox'], result_ch['date_bbox'], result_ch['sum_bbox'], result_ch['uid_bbox'])

        #bboxを引く処理
        result_save_path = draw_info(dir_image, bbox_list)

        #結果を返す
        result_data = result_custom(result_save_path, result_ja, result_ch)

        return jsonify(result_data)

    except Exception as e:
        print({ "message": "AI推論後の後処理でエラーが発生しております。："+str(e), "race": "", "date": "", "sum": "", "uid": "", "image": ""})
        return jsonify({ "message": "AI推論後の後処理でエラーが発生しております。", "race": "", "date": "", "sum": "", "uid": "", "image": ""}), 400

    finally:
        #インプットイメージの削除
        if dir_image and os.path.exists(dir_image):
            os.remove(dir_image)

        #OCR結果イメージの削除
        if result_save_path and os.path.exists(result_save_path):
            os.remove(result_save_path)