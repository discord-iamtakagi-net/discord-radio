# discord-radio
[![latest](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml/badge.svg)](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml)

前提として、radiko のプレミアム会員アカウントが必要です。

- `/radio <station_id>`: 選局コマンド
- `/radiolist`: 局リスト

## Install (Basic)

### Required Libraries
- `FFmpeg 4.2.4`
- `Python 3.10`
- `requirements.txt` 記載のライブラリ

### How to Install
- `$ git clone https://github.com/iamtakagi/radio.discord.git` リポジトリをローカルにクローン

- `$ pip install -r requirements.txt` 必要な pip ライブラリのインストール

- `$ python app.py` 起動

## Install (Docker)
- `.env.sample` 適宣書き換え

- `$ docker login ghcr.io`

- `docker-compose.yml` 作成
```yml
version: '3'

services:
  app:
    container_name: app
    image: ghcr.io/discord-iamtakagi-net/discord-radio:latest
    env_file: 
      - .env
    restart: always
```

- `$ docker-compose up -d` 

### If you need to update the Docker Image
`$ docker pull ghcr.io/iamtakagi/radio.discord`

## LICENSE
MIT License.
