import csv
import json
from io import StringIO
from datetime import datetime, timezone
import os
from dotenv import dotenv_values
from pydantic import BaseModel, parse_obj_as

from api.embed_playlist import fetch_embed_playlist
from api.selenium_playlist import fetch_selenium_playlist
from api.amazon_url_utility import get_album_track_url, get_album_url, get_artist_url, get_playlist_track_url, get_playlist_url


class EmbedPlaylistCsvConfig(BaseModel):
  playlist_asin: str


def command_embed_playlist_csv(args):
  config = parse_obj_as(EmbedPlaylistCsvConfig, vars(args))

  playlist_asin = config.playlist_asin

  embed_playlist = fetch_embed_playlist(playlist_asin=playlist_asin)

  sio = StringIO()
  writer = csv.writer(sio)

  writer.writerow([
    'playlist_asin',
    'playlist_url',
    'track_index',
    'track_asin',
    'track_title',
    'track_artist',
    'track_artist_asin',
    'track_artist_url',
    'track_album',
    'track_album_asin',
    'track_album_url',
    'track_album_track_url',
    'track_playlist_track_url',
    'track_sample_url',
  ])

  for track in embed_playlist.tracks:
    writer.writerow([
      playlist_asin,
      get_playlist_url(playlist_asin=playlist_asin),
      track.index,
      track.asin,
      track.title,
      track.artist_name,
      track.artist_asin,
      get_artist_url(artist_asin=track.artist_asin),
      track.album_name,
      track.album_asin,
      get_album_url(album_asin=track.album_asin),
      get_album_track_url(album_asin=track.album_asin, track_asin=track.asin),
      get_playlist_track_url(playlist_asin=playlist_asin, track_asin=track.asin),
      track.sample_url,
    ])

  output_text = sio.getvalue()
  print(output_text)


class SeleniumPlaylistJsonConfig(BaseModel):
  selenium_url: str
  playlist_asin: str


def command_selenium_playlist_json(args):
  config = parse_obj_as(SeleniumPlaylistJsonConfig, vars(args))

  selenium_url = config.selenium_url
  playlist_asin = config.playlist_asin

  timestamp_utc_aware = datetime.now(timezone.utc)

  # TODO: wait selenium up

  selenium_playlist = fetch_selenium_playlist(
    selenium_url=selenium_url,
    playlist_asin=playlist_asin,
  )

  print(
    json.dumps(
      {
        'musics': selenium_playlist.tracks,
        'fetched_at': timestamp_utc_aware.isoformat(),
      },
      ensure_ascii=False,
    )
  )


def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--env_file', type=str)
  args, _ = parser.parse_known_args()
  env_file = args.env_file

  env_vals = dict(os.environ)
  if env_file:
    env_vals.update(dotenv_values(dotenv_path=env_file))

  subparsers = parser.add_subparsers()

  parser_embed_playlist_csv = subparsers.add_parser('embed_playlist_csv')
  parser_embed_playlist_csv.add_argument('--playlist_asin', type=str, default=env_vals.get('AMPD_PLAYLIST_ASIN'))
  parser_embed_playlist_csv.set_defaults(handler=command_embed_playlist_csv)

  parser_selenium_playlist_json = subparsers.add_parser('selenium_playlist_json')
  parser_selenium_playlist_json.add_argument('--selenium_url', type=str, default=env_vals.get('AMPD_SELENIUM_URL'))
  parser_selenium_playlist_json.add_argument('--playlist_asin', type=str, default=env_vals.get('AMPD_PLAYLIST_ASIN'))
  parser_selenium_playlist_json.set_defaults(handler=command_selenium_playlist_json)

  args = parser.parse_args()
  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()

if __name__ == '__main__':
  main()
