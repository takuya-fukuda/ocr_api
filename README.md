#APIの概要

##環境
python3.10.15
Ubuntu20.04.06 LTS

##アプリケーションルート
| パス | 概要 |
| -- | -- |
| http://localhost:5000/ | ヘルスチェック用 |
| http://localhost:5000/image/ | 券面OCR用 |

##POSTリクエスト
| body | 型 |
| -- | -- |
| 画像データ(base64) | ? |

##レスポンス
| キー | 型 | サンプル |
| -- | -- | -- |
| race | str | 01 |
| date | str | 2021-07-08 |
| sum | str | 800 |
| uid | str | 12-345-3333333334455 |
| image | str | fa;jgiegjaj;alse******acdfe |

##起動方法
1.Window上にWSL経由でUbuntuアプリをインストール
  以下Ubuntuアプリ内で実行

2.Pythonのインストール
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

4.gitのクローンとライブラリインストール
mkdir work

cd work

git clone https://3ize.backlog.jp/git/TOTAR_OCR/backend.git

cd backend

pip install -r requirements.txt

python run.py

※windowsだと起動はできますが、APIにリクエストしてもエラーが出ます。

##Flaskフォルダ構成
| filename | description |
| -- | -- |
| run.py | API起動用ファイル |
| api/config* | DBなどの設定ファイルが格納される |
| api/cvdrawtext* | PaddleOCRの設定ファイルなどが格納される今回は必要ない |
| api/ppocr_onnx* | PaddleOCRのモデルファイルや推論スクリプトが格納される |
| api/__init__.py | アプリケーションルート設定ファイル |
| api/detect.py | /image/の全体処理が記載されたファイル。前処理⇒推論⇒後処理の原則に基づき記載 |
| api/preparation.py | 前処理ファイル。detect.pyから参照される |
| api/paddleocr_dev.py | PaddleOCR推論ファイル。detect.pyから参照される |
| api/postprocess.py | 後処理ファイル。detect.pyから参照される |


