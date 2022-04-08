# radio.discord
[![latest](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml/badge.svg)](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml)

*動作不安定 (α) それなりに動作しますが、局変更時の処理がイマイチ不安定です。\
前提として、radiko のプレミアム会員アカウントが必要です。

## Docker を使わずインストールする場合

### 前提として必要なライブラリ等
- `FFmpeg 4.2.4`
- `Python 3.10`
- `requirements.txt` 記載のライブラリ

### 導入方法
- `$ git clone https://github.com/iamtakagi/radio.discord.git` リポジトリをローカルにクローン

- `$ pip install -r requirements.txt` 必要な pip ライブラリのインストール

- `$ python app.py` 起動

## Docker を使ってインストールする場合
- `app.env.sample` を `app.env` として適宣書き換え

- `$ docker login ghcr.io`

- `docker-compose.yml` 作成
```yml
version: '3'

services:
  app:
    container_name: app
    image: ghcr.io/iamtakagi/radio.discord
    env_file: app.env
    restart: unless-stopped
```

- `$ docker-compose up -d` 

### イメージの更新
`$ docker pull ghcr.io/iamtakagi/radio.discord`

## LICENSE
MIT License.