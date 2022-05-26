from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime, timezone
import time
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

PLAYLIST_URL = os.environ['PLAYLIST_URL']
SELENIUM_URL = os.environ['SELENIUM_URL']
ROOT_DIR = Path(os.environ['ROOT_DIR'])

timestamp_utc_aware = datetime.now(timezone.utc)

options = webdriver.ChromeOptions()

driver = webdriver.Remote(
    command_executor=SELENIUM_URL,
    options=options,
)
driver.get(PLAYLIST_URL)

time.sleep(1)

musics = []
last_index = 0

prev_scroll_y = -1
while True:
  music_rows = driver.find_elements(by=By.CSS_SELECTOR, value='music-image-row')
  for music_row in music_rows:
    index = int(music_row.find_element(by=By.CSS_SELECTOR, value='.index').text)

    image_elm = music_row.find_element(by=By.CSS_SELECTOR, value='music-image')
    image_url = image_elm.get_attribute('src')

    music_elm = music_row.find_element(by=By.CSS_SELECTOR, value='.col1 > music-link')
    music_title = music_elm.get_attribute('title')
    music_url = music_elm.find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')

    artist_elm = music_row.find_element(by=By.CSS_SELECTOR, value='.col2 > music-link')
    artist = artist_elm.get_attribute('title')
    artist_url = artist_elm.find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')

    album_elm = music_row.find_element(by=By.CSS_SELECTOR, value='.col3 > music-link')
    album = album_elm.get_attribute('title')
    album_url = album_elm.find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')

    duration_elm = music_row.find_element(by=By.CSS_SELECTOR, value='.col4 > music-link')
    duration = duration_elm.get_attribute('title')

    if last_index < index:
      musics.append({
        'index': index,
        'music_title': music_title,
        'music_url': music_url,
        'artist': artist,
        'artist_url': artist_url,
        'album': album,
        'album_url': album_url,
        'duration': duration,
        'image_url': image_url,
      })
      last_index = index

  driver.execute_script('window.scrollBy(0, 500)')
  time.sleep(1)

  scroll_y = driver.execute_script('return window.scrollY')
  if prev_scroll_y == scroll_y:
    break

  prev_scroll_y = scroll_y


datetime_string = timestamp_utc_aware.strftime('%Y%m%d_%H%M%S')
with open(ROOT_DIR / f'{datetime_string}.json', 'w', encoding='utf-8') as fp:
  json.dump({
    'musics': musics,
    'fetched_at': timestamp_utc_aware.isoformat(),
  }, fp, ensure_ascii=False)

driver.quit()
