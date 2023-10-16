from src.utils import create_webhook_content, send_webhook
from src.get_tweet import get_tweet_data
from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if __name__ == '__main__':
    tweet_id = input('tweetId: ')

    tweet_data = get_tweet_data(tweet_id)
    webhook_content = create_webhook_content(tweet_data)

    send_webhook(WEBHOOK_URL, webhook_content)



