# Twicord-core

DiscordにTwitterのカードを飛ばすコードです。  
TwitterのツイートIDを指定すると、seleniumを使ってスクレイピングを行い、Discord Webhookにembedを使った形式で送信します。


## 使い方
- docker上でseleniumを実行します。
```shell
docker-compose up -d
```

- `.env.sample`を`.env`にコピーし、Discord WebhookのURLを設定します。
- main.pyを実行します。
- お好みのTweetIdを指定してください。
