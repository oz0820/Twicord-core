from xml.sax.saxutils import unescape
from bs4 import BeautifulSoup
import time

from src.utils import get_driver


def get_tweet_data(tweet_id):
    url = f'https://twitter.com/x/status/{tweet_id}/'

    with get_driver() as driver:
        driver.get(url)

        for i in range(100):
            html = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            # tweetの親要素に設定されているAttributeを確認して、読み込み待ちをする
            if soup.select_one('[data-testid="tweet"]') is not None:
                # time.sleep(0.5)
                break
            time.sleep(0.5)

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

    tweet_elm = soup.select_one('article[data-testid="tweet"]')  # tweet本体が乗っているarticleタグ
    tweet_og_url = soup.select_one('[property="og:url"]').get('content')  # ツイートのURL

    # アカウントアイコン
    profile_image_url = soup.select_one('[data-testid="tweet"] > div > div > div:nth-child(2)').select_one('img').get('src').replace('normal', '400x400')
    tweet_og_description = soup.select_one('[property="og:description"]').get('content')  # 短縮本文
    tweet_og_image = soup.select_one('[property="og:image"]').get('content')

    # アカウント名(表示名)
    user_name = soup.select_one('[property="og:title"]').get('content')[:-5]

    # screen_name
    user_screen_name = tweet_og_url.split('/')[3]

    # ユーザーページ
    user_url = f'https://twitter.com/{user_screen_name}'

    # 投稿日時(UTC)
    post_datetime = soup.select_one('time[datetime]').get('datetime')

    # いいね/RT数を抜き出し
    public_metrics = {
        "retweet_count": "0",
        "quote_count": "0",
        "like_count": "0",
        "bookmark_count": "0",
    }
    for c in tweet_elm.select_one('div[role="group"]').children:
        if c.get_text().find('Repost') != -1:
            public_metrics['retweet_count'] = c.select_one('span[data-testid]').get_text()
        elif c.get_text().find('Quote') != -1:
            public_metrics['quote_count'] = c.select_one('span[data-testid]').get_text()
        elif c.get_text().find('Like') != -1:
            public_metrics['like_count'] = c.select_one('span[data-testid]').get_text()
        elif c.get_text().find('Bookmark') != -1:
            public_metrics['bookmark_count'] = c.select_one('span[data-testid]').get_text()

    # 引用RTの引用元を削除する(引用元の画像が紛れ込んで非常に面倒だったため、引用元を消し飛ばす)
    for del_elm in tweet_elm.select_one(' div > div > div:nth-child(3)').select('div[id] > div[id]'):
        del_elm.clear()

    # ツイート本体のelement内のimgタグを全て抽出し、webp+高画質指定する(altの内容を指定しないと絵文字の画像が紛れ込む)
    tweet_image_urls = []
    for elm in tweet_elm.find_all('img', attrs={'alt': 'Image'}):
        tweet_url = elm.get('src').split('?')[0] + '?format=webp&name=large'
        tweet_image_urls.append(tweet_url)

    # GIF/Video(現状埋め込み再生の方法が分からないので、書き出すデータに含めない)
    for elm in tweet_elm.find_all('video', attrs={"aria-label": "Embedded video"}):
        thumbnail_url = elm.get('poster')
        url = elm.get('src')
        # tweet_image_urls.append(thumbnail_url)

    tweet_data = {
        "data": {
            "public_metrics": {
                "like_count": public_metrics.get('like_count'),
                "quote_count": public_metrics.get('quote_count'),
                "retweet_count": public_metrics.get('retweet_count'),
                "bookmark_count": public_metrics.get('bookmark_count'),
            },
            "text": unescape(tweet_og_description),     # ツイート本文。metaのog:descriptionから取得
            "id": tweet_og_url.split('/')[-1],          # ツイートURLから取得
            "url": tweet_og_url,                        # ツイートURL。metaのog:urlから取得
            "image_urls": tweet_image_urls,             # list[str] 添付画像のURL
            "created_at": post_datetime                 # datetime型の文字列
        },
        "user": {
            "name": unescape(user_name),                # 表示名
            "screen_name": user_screen_name,            # スクリーンネーム
            "url": user_url,                            # ユーザーのホーム
            "profile_image_url": profile_image_url      # ユーザーのアイコンURL
        },
    }

    return tweet_data
