from pathlib import Path
from typing import List
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from . import config
from .urls import get_embed_playlist_url


class EmbedPlaylistTrackItem(BaseModel):
  index: str
  asin: str
  title: str
  artist_asin: str
  artist_name: str
  album_asin: str
  album_name: str
  sample_url: str

class EmbedPlaylist(BaseModel):
  asin: str
  tracks: List[EmbedPlaylistTrackItem]


def fetch_embed_playlist(playlist_asin: str) -> EmbedPlaylist:
  url = get_embed_playlist_url(playlist_asin=playlist_asin)

  headers = {
    'User-Agent': config.USER_AGENT,
  }

  req = requests.get(url, headers=headers)
  html = req.text

  bs = BeautifulSoup(html, 'html5lib')

  tracks_container_tag = bs.find(id='tracksContainer')

  track_item_tags = tracks_container_tag.find_all(class_='trackItem')

  tracks: List[EmbedPlaylistTrackItem] = []

  for track_item_tag in track_item_tags:
    track_index_tag = track_item_tag.find(name='input', class_='trackIndex')
    # track_asin_tag = track_item_tag.find(name='input', class_='trackAsin')
    track_title_tag = track_item_tag.find(class_='trackTitle')

    track_artist_tag = track_item_tag.find(class_='trackArtist')
    track_artist_anchor_tag = track_artist_tag.find(name='a')

    track_album_tag = track_item_tag.find(class_='trackAlbum')
    track_album_anchor_tag = track_album_tag.find(name='a')

    track_asin = track_item_tag['data-asin']
    track_sample_url = track_item_tag['data-url']

    track_index = track_index_tag['value'].strip()
    track_title = track_title_tag.text.strip()

    track_artist_name = track_artist_tag.text.strip()

    track_artist_url_raw = track_artist_anchor_tag['href']
    track_artist_asin = Path(urlparse(track_artist_url_raw).path).name

    track_album_name = track_album_tag.text.strip()

    track_album_url_raw = track_album_anchor_tag['href']
    track_album_asin = Path(urlparse(track_album_url_raw).path).name

    tracks.append(EmbedPlaylistTrackItem(
      index=track_index,
      asin=track_asin,
      title=track_title,
      artist_asin=track_artist_asin,
      artist_name=track_artist_name,
      album_asin=track_album_asin,
      album_name=track_album_name,
      sample_url=track_sample_url,
    ))

  return EmbedPlaylist(
    asin=playlist_asin,
    tracks=tracks,
  )
