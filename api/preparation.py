from pathlib import Path
from flask import jsonify
import os
from os.path import splitext
import pillow_heif
from PIL import Image

basedir = Path(__file__).parent.parent

def load_image(request):
    """画像の読み込み"""
    file = request.files['file'] #画像の受け取り
    filename = file.filename
    img_path = str(basedir / "data" / "input" /filename)
    print(img_path)
    file.save(img_path)
    
    return img_path, filename

def extension_split(img_path):
    ext = splitext(img_path)[1]
    return ext

def heic_convert(img_path):
    save_path = splitext(img_path)[0] + ".jpg"
    heif_file = pillow_heif.read_heif(img_path)
    for img in heif_file: 
        image = Image.frombytes(
            img.mode,
            img.size,
            img.data,
            'raw',
            img.mode,
            img.stride,
        )
    image.save(save_path, "JPEG")
    os.remove(img_path)

    return save_path