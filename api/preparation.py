from pathlib import Path
from flask import jsonify
import PIL

basedir = Path(__file__).parent.parent

def load_image(request):
    """画像の読み込み"""
    file = request.files['file'] #画像の受け取り
    filename = file.filename
    dir_image = str(basedir / "data" / "input" /filename)
    print(dir_image)
    file.save(dir_image)
    
    return dir_image, filename