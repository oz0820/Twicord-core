import os
from datetime import timezone, timedelta
from selenium import webdriver
from dotenv import load_dotenv
import json
import requests

load_dotenv()


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en-US')
    options.add_argument("--window-size=1280x2048")
    options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/111.0.3497.81 Safari/537.36')

    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        options=options
    )

    driver.implicitly_wait(10)

    return driver


def send_webhook(webhook_url, embeds):
    res = requests.post(webhook_url, json.dumps(embeds), headers={'Content-Type': 'application/json'})
    print('status_code', res.status_code)


def create_webhook_content(tweet_data: dict):

    # ベースとなるデータ構造
    webhook_content = {
        "content": tweet_data.get('data').get('url'),
        "embeds": [
            {
                "color": 0x1da0f2,
                "url": tweet_data.get('data').get('url'),
                "author": {
                    "name": f"{tweet_data.get('user').get('name')}(@{tweet_data.get('user').get('screen_name')})",
                    "url": tweet_data.get('user').get('url'),
                    "icon_url": tweet_data.get('user').get('profile_image_url'),
                },
                "fields": [
                    {
                        "name": "Likes",
                        "value": tweet_data.get('data').get('public_metrics').get('like_count'),
                        "inline": True
                    },
                    {
                        "name": "Retweets",
                        "value": tweet_data.get('data').get('public_metrics').get('retweet_count'),
                        "inline": True
                    }
                ],
                "description": tweet_data.get('data').get('text'),
            }
        ]
    }

    # 投稿日時の埋め込み
    if os.getenv('CREATED_AT_TYPE') == "absolute":
        webhook_content['embeds'][0]['timestamp'] = tweet_data.get('data').get('created_at').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    elif os.getenv('CREATED_AT_TYPE') == 'relative':
        created_at_utc = tweet_data.get('data').get('created_at')
        created_at_jst = created_at_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=+9)))
        CREATED_AT_FORMAT = os.getenv('CREATED_AT_FORMAT')

        webhook_content['embeds'][0]['footer'] = {
            "icon_url": "https://www.google.com/s2/favicons?sz=64&domain=pbs.twimg.com",
            "text": "Twitter･" + created_at_jst.strftime(CREATED_AT_FORMAT)
        }

    # 画像を枚数分埋め込む
    for count, image_url in enumerate(tweet_data.get('data').get('image_urls')):
        if count == 0:
            webhook_content['embeds'][0]['image'] = {"url": image_url}
        else:
            embed = {
                "url": tweet_data.get('data').get('url'),
                "image": {
                    "url": image_url,
                }
            }
            webhook_content['embeds'].append(embed)

    return webhook_content
