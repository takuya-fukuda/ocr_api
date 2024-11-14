## API の概要

レシートの合計金額 OCR

## 使用している AI モデル

PaddleOCR の ONNX 変換モデル

## 環境

python3.10.15
Ubuntu20.04.06 LTS

## アプリケーションルート

| パス                         | 概要             |
| ---------------------------- | ---------------- |
| http://localhost:5000/       | ヘルスチェック用 |
| http://localhost:5000/image/ | 券面 OCR 用      |

## POST リクエスト

| body               | 型  |
| ------------------ | --- |
| 画像データ(base64) | ?   |

## レスポンス

| キー  | 型  | サンプル                      |
| ----- | --- | ----------------------------- |
| race  | str | 01                            |
| date  | str | 2021-07-08                    |
| sum   | str | 800                           |
| uid   | str | 12-345-3333333334455          |
| image | str | fa;jgiegjaj;alse**\*\***acdfe |

## 起動方法

1.Window 上に WSL 経由で Ubuntu アプリをインストール
以下 Ubuntu アプリ内で実行

2.Python のインストール
sudo apt update

sudo apt install software-properties-common

sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt update

sudo apt install python3.10

python3.10 --version

3.仮想環境の作成
python3.10 -m venv [your_env_name]

cd [your_env_name]

source bin/activate

4.git のクローンとライブラリインストール
mkdir work

cd work

git clone https://github.com/takuya-fukuda/ocr_api.git

cd backend

pip install -r requirements.txt

python run.py

## Flask フォルダ構成

| filename                 | description                                                                     |
| ------------------------ | ------------------------------------------------------------------------------- |
| run.py                   | API 起動用ファイル                                                              |
| api/config\*             | DB などの設定ファイルが格納される                                               |
| api/cvdrawtext\*         | PaddleOCR の設定ファイルなどが格納される今回は必要ない                          |
| api/ppocr_onnx\*         | PaddleOCR のモデルファイルや推論スクリプトが格納される                          |
| api/**init**.py          | アプリケーションルート設定ファイル                                              |
| api/ocr.py               | /image/の全体処理が記載されたファイル。前処理 ⇒ 推論 ⇒ 後処理の原則に基づき記載 |
| api/preparation.py       | 前処理ファイル。ocr.py から参照される                                           |
| api/paddleocr_predict.py | PaddleOCR 推論ファイル。ocr.py から参照される                                   |
| api/postprocess.py       | 後処理ファイル。ocr.py から参照される                                           |

## PaddleOCR のファインチューニング方法

git clone https://github.com/PaddlePaddle/PaddleOCR

configs 配下にある YAML ファイルを編集
./config/rec/PP-OCRv3/multi_language/japan_PP-OCRv3_rec.yml

事前学習済みモデルのダウンロード
https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/models_list_en.md

YAML ファイルに下記追加
pretrained_model: ./models/japan_PP-OCRv3_rec_train/best_accuracy
