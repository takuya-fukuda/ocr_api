import argparse
import os
from pathlib import Path

import cv2
import time

from yomitoku.constants import SUPPORT_OUTPUT_FORMAT
from yomitoku.data.functions import load_image, load_pdf
from yomitoku.document_analyzer import DocumentAnalyzer

# Analyzerの設定を定義
def get_analyzer():
    configs = {
        "ocr": {
            "text_detector": {
                "path_cfg": None,
            },
            "text_recognizer": {
                "path_cfg": None,
            },
        },
        "layout_analyzer": {
            "layout_parser": {
                "path_cfg": None,
            },
            "table_structure_recognizer": {
                "path_cfg": None,
            },
        },
    }

    return DocumentAnalyzer(
        configs=configs,
        visualize="store_true",
        device="cuda",
    )

def test_ocr(path, analyzer):
    # Ensure path is a Path object
    path = Path(path)

    if path.suffix[1:].lower() in ["pdf"]:
        imgs = load_pdf(path)
        return "pdfには対応していません"
    else:
        imgs = [load_image(path)]

    ocr_word=[]

    for page, img in enumerate(imgs):
        results, ocr, layout = analyzer(img)
        
        for word in results.paragraphs:
            ocr_dict={}
            ocr_dict['word']=word.contents
            ocr_dict['bbox']=word.box
            ocr_word.append(ocr_dict)
    
    return ocr_word


if __name__ == "__main__":
    img_path = "./img/IMG_3078.jpg"

    # Analyzerの初期化
    analyzer = get_analyzer()

    # OCR実行
    ocr_result = test_ocr(img_path, analyzer)

    # 結果の表示
    print(ocr_result)