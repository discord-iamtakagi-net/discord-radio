# radio.discord
*動作不安定 (α) それなりに動作するとは思いますが、局変更時の処理がイマイチ不安定です。\
前提として、radiko のプレミアム会員アカウントが必要です。

## 前提 (Docker を使わず動かす場合)
- `FFmpeg 4.2.4`
- `Python 3.10`
- `requirements.txt` 記載のライブラリ

## インストール (Docker)
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

## LICENSE
MIT License.