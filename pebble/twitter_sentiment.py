# Use the blink(1) to communicate the sentiment of Pebble-related Twitter tweets
# Interpolates between green for :) and red for :( for each tweet as it arrives in real-time
# Written by Kevin Conley

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import atexit
import os
import textblob # pip install textblob
import twitter # pip install python-twitter
from lib.blink1_ctypes import Blink1
from sys import exit

TWITTER_URL = 'https://twitter.com/'
TWITTER_STATUS_URL = TWITTER_URL + '#!/twitter/status/'

FADE_DURATION_MS = 1000

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
OFF = (0, 0, 0)

b1 = Blink1()
# You can create this environment variable to use a specific blink(1), otherwise it will use id 0
b1.open_by_id(int(os.getenv('PEBBLE_TWITTER_SENTIMENT_BLINK1_ID', 0)))

# Create these and add them to your environment variables or set them directly here:
# https://apps.twitter.com/app
CONSUMER_KEY = os.getenv('CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', None)
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY', None)
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', None)

TWEET_TOPICS_TO_TRACK = ['@Pebble', '#pebble', '#pebbletime']

COLOR_GRADIENT_STEPS = 100

def back_to_black():
  b1.fade_to_rgb(0, *OFF)

def polarity_to_gradient_step(polarity):
  polarity_magnitude = abs(polarity)
  step = max(0, int((polarity * COLOR_GRADIENT_STEPS) - 1))
  if polarity < 0:
    step = COLOR_GRADIENT_STEPS - 1 - step
  return step

def interpolate_color(color1, color2, step):
  return [channel1 + ((channel2 - channel1) * step / COLOR_GRADIENT_STEPS) for \
          (channel1, channel2) in zip(color1, color2)]

def is_retweet(status):
  return (status.retweeted or ('RT ' in status.text))

def process_stream():
  if None in [CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET]:
    print 'You must set CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, and ACCESS_TOKEN_SECRET!'
    exit(-1)

  api = twitter.Api(consumer_key=CONSUMER_KEY,
                    consumer_secret=CONSUMER_SECRET,
                    access_token_key=ACCESS_TOKEN_KEY,
                    access_token_secret=ACCESS_TOKEN_SECRET)

  stream = api.GetStreamFilter(track=TWEET_TOPICS_TO_TRACK)

  for tweet in stream:
    status = twitter.status.Status.NewFromJsonDict(tweet)
    # Skip retweets
    if is_retweet(status):
      continue

    # Calculate the tweet's sentiment polarity (in range [-1, 1])
    status_textblob = textblob.TextBlob(status.text)
    sentiment_polarity = status_textblob.sentiment.polarity
    print '%s - (%f)' % (status.text, sentiment_polarity)
    print '%s%s\n' % (TWITTER_STATUS_URL, status.id)

    # Change the color based on the tweet's sentiment polarity
    gradient_step = polarity_to_gradient_step(sentiment_polarity)
    upper_gradient_color = GREEN if sentiment_polarity >= 0 else RED
    interpolated_color = interpolate_color(BLUE, upper_gradient_color, gradient_step)
    b1.fade_to_rgb(FADE_DURATION_MS, *interpolated_color)

if __name__ == '__main__':
  # Turn the blink(1) off when script exits
  atexit.register(back_to_black)

  process_stream()
