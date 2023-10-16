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


### tweet_dataの形式
`src.get_tweet`内の`create_webhook_content`で生成されるdictオブジェクトの構成です。  
うっすらとTwitter API v2味があります
```json
{
    "data": {
        "public_metrics": {
            "like_count": str or null,
            "quote_count": str or null,
            "retweet_count": str or null,
            "bookmark_count": str or null,
        },
        "text": str,
        "id": str,
        "url": str,
        "image_urls": list[str],
        "created_at": str(datetime)

    },
    "user": {
        "name": str,
        "screen_name": str,
        "url": str,
        "profile_image_url": str
    },
}
```
