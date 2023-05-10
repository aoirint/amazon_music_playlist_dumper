from pathlib import Path
from typing import List
from urllib.parse import urlparse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime, timezone
import time
from pathlib import Path
import os

from . import config
from .amazon_url_utility import get_playlist_url


class SeleniumPlaylistTrackItem(BaseModel):
  index: str
  title: str
  url: str
  artist: str
  artist_url: str
  album: str
  album_url: str
  duration: str
  image_url: str


class SeleniumPlaylist(BaseModel):
  asin: str
  tracks: list[SeleniumPlaylistTrackItem]


def fetch_selenium_playlist(
  selenium_url: str,
  playlist_asin: str,
) -> SeleniumPlaylist:
  playlist_url = get_playlist_url(playlist_asin=playlist_asin)

  options = webdriver.ChromeOptions()

  driver = webdriver.Remote(
    command_executor=selenium_url,
    options=options,
  )
  driver.implicitly_wait(30)
  driver.get(playlist_url)

  time.sleep(1)

  tracks: list[SeleniumPlaylistTrackItem] = []
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
        tracks.append(SeleniumPlaylistTrackItem(
          index=index,
          title=music_title,
          url=music_url,
          artist=artist,
          artist_url=artist_url,
          album=album,
          album_url=album_url,
          duration=duration,
          image_url=image_url,
        ))
        last_index = index

    driver.execute_script('window.scrollBy(0, 500)')
    time.sleep(1)

    scroll_y = driver.execute_script('return window.scrollY')
    if prev_scroll_y == scroll_y:
      break

    prev_scroll_y = scroll_y

  driver.quit()

  return SeleniumPlaylist(
    asin=playlist_asin,
    tracks=tracks,
  )
