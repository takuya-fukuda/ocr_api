import cv2
import os
from api.ppocr_onnx.ppocr_onnx import PaddleOcrONNX
import time

class OCRProcessor:
    def __init__(self, image_path, rec_model, rec_dict):
        self.image_path = image_path
        self.rec_model = rec_model
        self.rec_dict = rec_dict
        self.paddleocr_parameter = self.get_paddleocr_parameter()
        self.paddle_ocr_onnx = PaddleOcrONNX(self.paddleocr_parameter)

    class DictDotNotation(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__dict__ = self

    def get_paddleocr_parameter(self):
        paddleocr_parameter = self.DictDotNotation()

        # params for prediction engine
        paddleocr_parameter.use_gpu = False

        # params for text detector
        paddleocr_parameter.det_algorithm = 'DB'
        paddleocr_parameter.det_model_dir = './api/ppocr_onnx/model/det_model/ch_PP-OCRv3_det_infer.onnx'
        paddleocr_parameter.det_limit_side_len = 960
        paddleocr_parameter.det_limit_type = 'max'
        paddleocr_parameter.det_box_type = 'quad'

        # DB params
        paddleocr_parameter.det_db_thresh = 0.3
        paddleocr_parameter.det_db_box_thresh = 0.6
        paddleocr_parameter.det_db_unclip_ratio = 1.5
        paddleocr_parameter.max_batch_size = 10
        paddleocr_parameter.use_dilation = False
        paddleocr_parameter.det_db_score_mode = 'fast'

        # params for text recognizer
        paddleocr_parameter.rec_algorithm = 'SVTR_LCNet'
        paddleocr_parameter.rec_model_dir = self.rec_model
        paddleocr_parameter.rec_image_shape = '3, 48, 320'
        paddleocr_parameter.rec_batch_num = 6
        paddleocr_parameter.rec_char_dict_path = self.rec_dict
        paddleocr_parameter.use_space_char = True
        paddleocr_parameter.drop_score = 0.5

        # params for text classifier
        paddleocr_parameter.use_angle_cls = False
        paddleocr_parameter.cls_model_dir = './api/ppocr_onnx/model/cls_model/ch_ppocr_mobile_v2.0_cls_infer.onnx'
        paddleocr_parameter.cls_image_shape = '3, 48, 192'
        paddleocr_parameter.label_list = ['0', '180']
        paddleocr_parameter.cls_batch_num = 6
        paddleocr_parameter.cls_thresh = 0.9

        paddleocr_parameter.save_crop_res = False

        return paddleocr_parameter

    def process_image(self):
        if self.image_path is not None:
            image = cv2.imread(self.image_path)
            dt_boxes, rec_res, time_dict = self.paddle_ocr_onnx(image)

            return dt_boxes, rec_res, time_dict
