## API の概要

レシートの合計金額 OCR

![OCR例](./image.jpg)

## 使用している AI モデル

| モデル名                     |
| ---------------------------- |
| PaddleOCR の ONNX 変換モデル |

PaddleOCR 推論用コード

```
ocr_ja = PaddleOCR(use_angle_cls=True, lang='japan', use_gpu=False, enable_mkldnn=True, cpu_threads=cpu_threads, use_onnx=True, det_model_dir=det_model, rec_model_dir=ja_rec_model, cls_model_dir=cls_model)
ocr_result_ja = ocr_ja.ocr(img_path)
```

## ブランチ

VisionAPI はアルゴリズムの修正が必要

| ブランチ名  | 概要                                                           |
| ----------- | -------------------------------------------------------------- |
| main        | PaddleOCR で推論                                               |
| onnxruntime | PaddleOCR を ONNXruntime で推論                                |
| visionapi   | visionAPI で推論(ただしレスポンスに BBOX は付けず、値のみ返却) |
| yomitoku    | yomitoku で推論(ただしレスポンスに BBOX は付けず、値のみ返却)  |

## 環境

python3.10.15
Ubuntu20.04.06 LTS

## アプリケーションルート

| パス                        | 概要             |
| --------------------------- | ---------------- |
| http://publicIP:5000/       | ヘルスチェック用 |
| http://publicIP:5000/image/ | 券面 OCR 用      |

## POST リクエスト

| body               | 型  |
| ------------------ | --- |
| 画像データ(base64) | ?   |

## レスポンス

| キー  | 型  | サンプル                      |
| ----- | --- | ----------------------------- |
| sum   | str | 800                           |
| image | str | fa;jgiegjaj;alse**\*\***acdfe |

## 起動方法

1.Window 上に WSL 経由で Ubuntu アプリをインストール
以下 Ubuntu アプリ内で実行

2.Python のインストール

```
sudo apt update

sudo apt install software-properties-common

sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt update

sudo apt install python3.10

python3.10 --version
```

3.仮想環境の作成

```
python3.10 -m venv [your_env_name]

cd [your_env_name]

source bin/activate
```

4.git のクローンとライブラリインストール

```
mkdir work

cd work

git clone https://github.com/takuya-fukuda/ocr_api.git

cd backend

pip install -r requirements.txt

python run.py
```

## Flask フォルダ構成

| filename           | description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| run.py             | API 起動用ファイル                                                              |
| api/config/\*      | DB などの設定ファイルが格納される                                               |
| api/model/\*       | PaddleOCR のモデルファイルが格納される                                          |
| api/**init**.py    | アプリケーションルート設定ファイル                                              |
| api/ocr.py         | /image/の全体処理が記載されたファイル。前処理 ⇒ 推論 ⇒ 後処理の原則に基づき記載 |
| api/preparation.py | 前処理ファイル。ocr.py から参照される                                           |
| api/postprocess.py | 後処理ファイル。ocr.py から参照される                                           |

## PaddleOCR のファインチューニング方法

git clone https://github.com/PaddlePaddle/PaddleOCR

configs 配下にある YAML ファイルを編集
./config/rec/PP-OCRv3/multi_language/japan_PP-OCRv3_rec.yml

```
#事前学習済みモデルのダウンロード
https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/models_list_en.md

#YAMLファイルに対象パラメータに下記追加(modelフォルダを作成して保存しておいた)
pretrained_model: ./models/japan_PP-OCRv3_rec_train/best_accuracy

#後は必要に応じてパラメータを編集。デフォでもいい。画像の拡張とかエポック数を調整
epoch_num: 100

- RecConAug:
    prob: 0
    ext_data_num: 0

batch_size_per_card: 30
```

./tools/program.py の修正

```
修正前
device = "gpu:{}".format(dist.ParallelEnv().dev_id) if use_gpu else "cpu"

修正後
device = paddle.get_device() if use_gpu else "cpu"
```

学習用コード

```
python tools/train.py -c configs/rec/PP-OCRv3/multi_language/japan_PP-OCRv3_rec.yml
```

学習後にモデルを保存

```
python tools/export_model.py -c configs/rec/PP-OCRv3/multi_language/japan_PP-OCRv3_rec.yml -o Global.pretrained_model=./output/v3_japan_mobile/latest.pdparams
```

下記に更新モデルが保存されているはずなので確認
output\inference\japan_PP-OCRv3_rec_infer

ONNX 変換用パッケージのインストール

```
pip install paddle2onnx
```

ONNX に変換

```
cd output

paddle2onnx --model_dir ./inference/japan_PP-OCRv3_rec_infer \
    --model_filename inference.pdmodel \
    --params_filename inference.pdiparams \
    --save_file ./model/rec_model/japan_PP-OCRv3_rec_infer.onnx \
    --opset_version 11
```

## ファインチューニングのデータセットサンプル

ファイル名は、yaml ファイルに合わせること
今回は./train_data/train_list.txt を作成

画像名とラベルはタブスペース

train_list.txt

```
./IMG_3093.jpg	1000
./IMG_3096.jpg	500
./IMG_3099.jpg	100
```
