def get_playlist_url(playlist_asin: str) -> str:
  return f'https://music.amazon.co.jp/user-playlists/{playlist_asin}'

def get_embed_playlist_url(playlist_asin: str) -> str:
  return f'https://music.amazon.co.jp/embed/{playlist_asin}'

def get_artist_url(artist_asin: str) -> str:
  return f'https://music.amazon.co.jp/artists/{artist_asin}'

def get_album_url(album_asin: str) -> str:
  return f'https://music.amazon.co.jp/albums/{album_asin}'

def get_playlist_track_url(playlist_asin: str, track_asin: str) -> str:
  return f'https://music.amazon.co.jp/user-playlists/{playlist_asin}?trackAsin={track_asin}'

def get_album_track_url(album_asin: str, track_asin: str) -> str:
  return f'https://music.amazon.co.jp/albums/{album_asin}?trackAsin={track_asin}'
