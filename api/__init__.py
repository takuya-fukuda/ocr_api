import json
import base64
import re
from . import ocr

from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

#接続確認用アプリケーションルート
@api.route('/')
def index():
    return "test"

#OCR用アプリケーションルート
@api.route('/image', methods=["POST"])
def prepare():
    return ocr.ocr_func(request)