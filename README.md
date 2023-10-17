# Twicord-core

DiscordにTwitterのカードを飛ばすプログラムです。  
TwitterのツイートIDを指定すると、seleniumを使ってスクレイピングを行い、Discord Webhookにembedを使用した形式で送信します。


## 使い方
- docker上でseleniumを実行します。
```shell
docker-compose up -d
```

- `.env.sample`を`.env`にコピーし、Discord WebhookのURLを設定します。
- main.pyを実行します。
- お好みのTweetIdを指定してください。


### `.env`の設定
|                   |                                                                          |
|:------------------|:-------------------------------------------------------------------------|
| WEBHOOK_URL       | Discordに送信するためのWebhookURL                                                |
| DATE_TYPE         | embed最下部の日時表示の種類。 absolute: 絶対時間, relative: 相対時間                         |
| CREATED_AT_FORMAT | 日時を文字列化するときに使うフォーマット。 datetimeのstrftimeに渡される。DATE_TYPEがrelativeの時に参照される。 |


### tweet_dataの形式
`src.get_tweet`内の`create_webhook_content`で生成されるdictオブジェクトの構成です。  
うっすらとTwitter API v2味があります
```json
{
    "data": {
        "public_metrics": {
            "like_count": str,
            "quote_count": str,
            "retweet_count": str,
            "bookmark_count": str,
        },
        "text": str,
        "id": str,
        "url": str,
        "image_urls": list[str],
        "created_at": datetime

    },
    "user": {
        "name": str,
        "screen_name": str,
        "url": str,
        "profile_image_url": str
    },
}
```
