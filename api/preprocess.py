from pathlib import Path
from os.path import splitext
import os
import pillow_heif
from PIL import Image

class PreProcess:
    def __init__(self, img_path: str):
        self.img_path = img_path
        _, ext = splitext(self.img_path)
        self.ext = ext.lower()

    def heic_convert(self):
        save_path = os.path.splitext(self.img_path)[0] + ".jpg"
        heif_file = pillow_heif.read_heif(str(self.img_path))

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
        os.remove(self.img_path)

        self.img_path = save_path

        return self.img_path

    def preprocess_default(self) -> Path:
        if not os.path.exists(self.img_path):
            raise FileNotFoundError("ファイルが存在しません")

        if self.ext not in [".jpeg", ".jpg", ".png", ".heic"]:
            raise ValueError("AIがファイル拡張子に対応していません")

        if self.ext == ".heic":
            self.img_path = self.heic_convert()

        return self.img_path
