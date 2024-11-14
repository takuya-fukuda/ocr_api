from pathlib import Path
from flask import jsonify
import PIL
import json
import os
import base64
import re 
import cv2

basedir = Path(__file__).parent.parent

'''
正規表現で目的のものを抜き出す処理（日本語用）
'''
# 全角数字を半角数字に変換する関数
def zenkaku_to_hankaku(text):
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    translation_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(translation_table)

# "O"（アルファベットのオー）を "0"（半角のゼロ）に変換する関数
def replace_word(text):
    text = text.replace('О', '0')
    text = text.replace('O', '0')
    text = text.replace('Ｏ', '0')
    text = text.replace('s', '5')
    text = text.replace('Ｓ', '5')
    text = text.replace('S', '5')
    text = text.replace ('ó', '6')
    text = text.replace ('ィ', '7')
    text = text.replace ('イ', '1')
    text = text.replace ('o', '0')
    text = text.replace(',', '')
    return text

def extract_info_ja(dt_boxes, rec_res):
    total_amount = None
    total_amount_bbox = None
    found_total_keyword = False
    found_partial_total_keyword = False

    for item, bbox in zip(rec_res, dt_boxes):
        item = replace_word(item[0])
        item = zenkaku_to_hankaku(item)
        bbox = bbox

        # 総合計の次の行の金額を抽出
        if found_total_keyword:
            total_match = re.search(r'(\d+)', item)
            if total_match:
                total_amount = total_match.group(1)
                total_amount_bbox = bbox
                found_total_keyword = False  # 抽出が完了したらフラグをリセット
                break

        # 「合計」の次の行の金額を抽出
        if found_partial_total_keyword and total_amount is None:
            total_match = re.search(r'(\d+)', item)
            if total_match:
                total_amount = total_match.group(1)
                total_amount_bbox = bbox
                found_partial_total_keyword = False  # 抽出が完了したらフラグをリセット
                break

        # 「総合計」という単語が見つかったら、次の行を金額としてマーク
        if '総合計' in item:
            found_total_keyword = True

        # 「合計」が見つかり、まだ「総合計」がなかった場合にマーク
        elif re.search(r'(合計|合言士)', item) and total_amount is None:
            found_partial_total_keyword = True

    return {
        'sum': total_amount,
        'total_amount_bbox': total_amount_bbox,
    }

'''
正規表現で目的のものを抜き出す処理終了（日本語用）
'''

def draw_pre(total_amount_bbox):
    bbox_list = []
    if total_amount_bbox is not None:
        bbox_list.append(total_amount_bbox)

    return bbox_list

def draw_info(image_path, dt_boxes):
    result_filename = os.path.basename(image_path)
    image = cv2.imread(image_path)
    for bbox in dt_boxes:
        cv2.line(image, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[1][0]), int(bbox[1][1])), (0, 0, 255), 3)
        cv2.line(image, (int(bbox[1][0]), int(bbox[1][1])), (int(bbox[2][0]), int(bbox[2][1])), (0, 0, 255), 3)
        cv2.line(image, (int(bbox[2][0]), int(bbox[2][1])), (int(bbox[3][0]), int(bbox[3][1])), (0, 0, 255), 3)
        cv2.line(image, (int(bbox[3][0]), int(bbox[3][1])), (int(bbox[0][0]), int(bbox[0][1])), (0, 0, 255), 3)

    result_dir = str(basedir / "data" / "result" )
    os.makedirs(result_dir, exist_ok=True)
    output_path = os.path.join(result_dir, result_filename)
    cv2.imwrite(output_path, image)
    return output_path

def result_custom(result_save_path, result_ja):
    data = {}
    data['sum'] = result_ja['sum']

    # 画像をBase64にエンコードしてdataに追加する
    with open(result_save_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    data['image'] = encoded_string
    
    return data

