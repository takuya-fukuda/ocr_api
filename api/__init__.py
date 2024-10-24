import json
import base64
import re
from . import detect

from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

#接続確認用アプリケーションルート
@api.route('/')
def index():
    return "test"

#YOLO実行関数
@api.route('/image', methods=["POST"])
def prepare():
    return detect.detection(request)