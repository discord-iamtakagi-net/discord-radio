# discord-radio
[![latest](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml/badge.svg)](https://github.com/iamtakagi/radio.discord/actions/workflows/latest.yml)

前提として、radiko のプレミアム会員アカウントが必要です。

- `/radio <station_id>`: 選局コマンド
- `/radiolist`: 局リスト

## Install
 `$ docker-compose up -d` 

```yml
version: '3'

services:
  app:
    container_name: discord-radio
    image: ghcr.io/discord-iamtakagi-net/discord-radio:latest
    env_file: 
      - .env
    restart: always
```

## LICENSE
MIT License.
