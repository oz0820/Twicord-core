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
        # driver.quit()


    """driver = get_driver()
    driver.get(url)

    for i in range(100):
        driver.find_element(By.TAG_NAME, 'iframe')

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        if soup.select_one('[data-testid="tweet"]') is not None:
            # time.sleep(0.5)
            break
        time.sleep(0.5)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()"""

    tweet_elm = soup.select_one('[data-testid="tweet"]')
    author_elm = tweet_elm.select_one('div > div > div:nth-child(2)')
    tweet_body = tweet_elm.select_one('div > div > div:nth-child(3)')

    tweet_og_url = soup.select_one('[property="og:url"]').get('content')

    # アカウントアイコン
    profile_image_url = soup.select_one('[data-testid="tweet"] > div > div > div:nth-child(2)').select_one('img').get('src').replace('normal', '400x400')
    # 短縮本文
    tweet_og_description = soup.select_one('[property="og:description"]').get('content')
    tweet_og_image = soup.select_one('[property="og:image"]').get('content')

    # アカウント名
    user_name = soup.select_one('[property="og:title"]').get('content')[:-5]

    # 表示ID
    user_screen_name = soup.select_one('[property="og:url"]').get('content').split('/')[3]

    # アカウントページ
    user_url = f'https://twitter.com/{user_screen_name}'

    # 投稿日時(UTC)
    post_datetime = soup.select_one('time[datetime]').get('datetime')
    # _post_datetime_utc = datetime.strptime(soup.select_one('time[datetime]').get('datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')
    # _post_datetime_jst = _post_datetime_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=+9)))
    # post_datetime = _post_datetime_jst.strftime('%Y/%m/%d %H:%M')

    public_metrics = {
        "retweet_count": 0,
        "quote_count": 0,
        "like_count": 0,
        "bookmark_count": 0,
    }
    for c in tweet_elm.select_one('div[role="group"]').children:
        if c.get_text().find('Repost') != -1:
            public_metrics['retweet_count'] = int(c.select_one('span[data-testid]').get_text().replace(',', ''))
        elif c.get_text().find('Quote') != -1:
            public_metrics['quote_count'] = int(c.select_one('span[data-testid]').get_text().replace(',', ''))
        elif c.get_text().find('Like') != -1:
            public_metrics['like_count'] = int(c.select_one('span[data-testid]').get_text().replace(',', ''))
        elif c.get_text().find('Bookmark') != -1:
            public_metrics['bookmark_count'] = int(c.select_one('span[data-testid]').get_text().replace(',', ''))

    # 引用RTの引用元を削除する
    for del_elm in tweet_elm.select_one(' div > div > div:nth-child(3)').select('div[id] > div[id]'):
        del_elm.clear()

    tweet_image_urls = []
    for elm in tweet_elm.find_all('img', attrs={'alt': 'Image'}):
        tweet_url = elm.get('src').split('?')[0] + '?format=webp&name=large'
        tweet_image_urls.append(tweet_url)

    tweet_data = {
        "data": {
            "public_metrics": {
                'like_count': public_metrics.get('like_count'),
                'quote_count': public_metrics.get('quote_count'),
                'retweet_count': public_metrics.get('retweet_count'),
                "bookmark_count": public_metrics.get('bookmark_count'),
            },
            "text": unescape(tweet_og_description),
            "id": tweet_og_url.split('/')[-1],
            "url": tweet_og_url,
            "image_urls": tweet_image_urls,
            "created_at": post_datetime

        },
        "user": {
            "name": unescape(user_name),
            "screen_name": user_screen_name,
            "url": user_url,
            "profile_image_url": profile_image_url
        },
    }

    # print(json.dumps(tweet_data, ensure_ascii=False, indent=2))
    """print(
        f'user_name:   \t{user_name}\n'
        f'screen_name: \t{user_screen_name}\n'
        f'user_url    \t{user_url}\n'
        f'profile_image\t{profile_image_url}\n'
        f'本文:\n'
        f'----------------------\n'
        f'{tweet_og_description}\n'
        f'----------------------\n'
        f'public_metrics\t{public_metrics}\n'
        f'投稿日時:      \t{post_datetime}\n'
        f'画像:         \t{tweet_image_urls}'
    )"""
    return tweet_data
