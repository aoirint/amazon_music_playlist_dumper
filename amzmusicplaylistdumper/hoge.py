import csv
from io import StringIO

from api.embed_playlist import fetch_embed_playlist
from api.urls import get_album_track_url, get_album_url, get_artist_url, get_playlist_track_url, get_playlist_url


def command_embed_playlist_csv(args):
  playlist_asin = args.playlist_asin
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


def main():
  import argparse
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()
  
  parser_embed_playlist_csv = subparsers.add_parser('embed_playlist_csv')
  parser_embed_playlist_csv.add_argument('--playlist_asin', type=str, required=True)
  parser_embed_playlist_csv.set_defaults(handler=command_embed_playlist_csv)

  args = parser.parse_args()
  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()

if __name__ == '__main__':
  main()
