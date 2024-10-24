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
def zenkaku_to_hankaku_ja(text):
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    translation_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(translation_table)

# "O"（アルファベットのオー）を "0"（半角のゼロ）に変換する関数
def replace_O_with_zero_ja(text):
    text = text.replace('О', '0')
    text = text.replace('O', '0')
    text = text.replace('Ｏ', '0')
    text = text.replace('s', '5')
    text = text.replace('Ｓ', '5')
    text = text.replace('S', '5')
    text = text.replace ('ó', '6')
    text = text.replace ('T', '7')
    text = text.replace ('ィ', '7')
    text = text.replace ('イ', '1')
    text = text.replace ('o', '0')
    return text

def extract_info_ja(dt_boxes, rec_res):
    race_number = None
    race_number_bbox = None

    for item, bbox in zip(rec_res, dt_boxes):
        item = replace_O_with_zero_ja(item[0])
        item = zenkaku_to_hankaku_ja(item)
        bbox = bbox

        if re.search(r'(レース|レ.ス|レー7|レス)', item):
            race_match = re.search(r'(\d+)', item)
            if race_match:
                race_number = race_match.group(1)
                race_number_bbox = bbox

    return {
        'race': race_number,
        'race_bbox': race_number_bbox,
    }

'''
正規表現で目的のものを抜き出す処理終了（日本語用）
'''

'''
正規表現で目的のものを抜き出す処理(中国語用)
'''
def zenkaku_to_hankaku_ch(text):
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    translation_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(translation_table)

def replace_O_with_zero_ch(text):
    text = text.replace('О', '0').replace('O', '0').replace('Ｏ', '0')
    text = text.replace('s', '5').replace('Ｓ', '5').replace('S', '5')
    text = text.replace('ó', '6').replace('T', '7').replace('L', '1')
    text = text.replace('.', '').replace(';', '').replace(':', '')
    return text

def extract_info_ch(dt_boxes, rec_res):
    date = ""
    date_bbox = None
    total_amount = ""
    total_amount_bbox = None
    uid = ""
    uid_bbox = None

    for item, bbox in zip(rec_res, dt_boxes):
        item = replace_O_with_zero_ch(item[0])
        item = zenkaku_to_hankaku_ch(item)
        bbox = bbox

        if re.search(r'\d{4}年\d{2}月\d{2}日', item):
            date = item.replace('年', '-').replace('月', '-').replace('日', '')
            date_bbox = bbox

        yen_matches = re.findall(r'(\d+)(?=円|門)', item)
        if yen_matches:
            total_amount = str(yen_matches[-1])
            total_amount_bbox = bbox

        if re.search(r'.{31,}', item):
            uid = item[:33]
            uid_bbox = bbox

    return {
        'date': date,
        'date_bbox': date_bbox,
        'sum': total_amount,
        'sum_bbox': total_amount_bbox,
        'uid': uid,
        'uid_bbox': uid_bbox
    }
'''
正規表現で目的のものを抜き出す処理終了(中国語用)
'''

def draw_pre(race_bbox, date_bbox, sum_bbox, uid_bbox):
    bbox_list = []
    if race_bbox is not None:
        bbox_list.append(race_bbox)
    if date_bbox is not None:
        bbox_list.append(date_bbox)
    if sum_bbox is not None:
        bbox_list.append(sum_bbox)
    if uid_bbox is not None:
        bbox_list.append(uid_bbox)

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

def result_custom(result_save_path, result_ja, result_ch):
    data = {}
    data['race'] = result_ja['race']
    data['date'] = result_ch['date']
    data['sum'] = result_ch['sum']
    data['uid'] = result_ch['uid']

    # 画像をBase64にエンコードしてdataに追加する
    with open(result_save_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    data['image'] = encoded_string
    
    return data

