import json
from pathlib import Path
import sys
import requests
from bs4 import BeautifulSoup
import yaml
import uuid
import time

from . import config
from .amazon_url_utility import get_playlist_url


def fetch_playlist(playlist_asin: str):
  session = requests.Session()
  session.headers = {
    'User-Agent': config.USER_AGENT,
  }

  playlist_url = get_playlist_url(playlist_asin=playlist_asin)

  headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ja',
    'Host': 'music.amazon.co.jp',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'User-Agent': config.USER_AGENT,
  }

  res = session.get(playlist_url, headers=headers)
  html = res.text

  bs = BeautifulSoup(html, 'html5lib')
  scripts = bs.select('script')

  found_script_text = None
  for script in scripts:
    if len(script.contents) == 0:
      continue

    script_text = script.contents[0].strip()
    if script_text.startswith('window.amznMusic = '):
      found_script_text = script_text
      break

  if not found_script_text:
    print('not found')
    sys.exit(1)

  start_index = found_script_text.index('window.amznMusic = ') + len('window.amznMusic = ')
  end_index = found_script_text.rindex('};') + 1
  data_string = found_script_text[start_index:end_index]

  data = yaml.load(data_string, Loader=yaml.SafeLoader)
  app_config = data['appConfig']
  device_id = str(app_config['deviceId'])
  version = str(app_config['version'])
  session_id = str(app_config['sessionId'])
  csrf_token = str(app_config['csrf']['token'])
  csrf_ts = str(app_config['csrf']['ts'])
  csrf_rnd = str(app_config['csrf']['rnd'])

  if device_id == '': # first request
    device_id = session_id

  request_id = str(uuid.uuid4())
  timestamp = str(int(time.time() * 1000))

  # print(timestamp)
  # print(session.cookies['session-id'])

  # print(session_id, csrf_token, csrf_ts, csrf_rnd)

  url = 'https://fe.mesk.skill.music.a2z.com/api/showHome'

  request_body = json.dumps({
    'deeplink': json.dumps({
      'interface': 'DeeplinkInterface.v1_0.DeeplinkClientInformation',
      'deeplink': f'/user-playlists/{playlist_asin}',
    }, ensure_ascii=False),
  }, ensure_ascii=False).replace(' ', '')
  print(request_body)

  content_length = len(request_body)

  request_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ja',
    'content-length': str(content_length),
    'content-type': 'text/plain;charset=UTF-8',
    'dnt': '1',
    'origin': 'https://music.amazon.co.jp',
    'referer': 'https://music.amazon.co.jp/',
    # 'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
    # 'sec-fetch-dest': 'empty',
    # 'sec-fetch-mode': 'cors',
    # 'sec-fetch-site': 'cross-site',
    'user-agent': config.USER_AGENT,
    'x-amzn-affiliate-tags': '',
    'x-amzn-application-version': version,
    'x-amzn-authentication': json.dumps({
      'interface': 'ClientAuthenticationInterface.v1_0.ClientTokenElementt',
      'accessToken': '',
    }, ensure_ascii=False).replace(' ', ''),
    'x-amzn-csrf': json.dumps({
      'interface': 'CSRFInterface.v1_0.CSRFHeaderElement',
      'token': str(csrf_token),
      'timestamp': str(csrf_ts),
      'rndNonce': str(csrf_rnd),
    }, ensure_ascii=False).replace(' ', ''),
    'x-amzn-currency-of-preference': 'JPY',
    'x-amzn-device-family': 'WebPlayer',
    'x-amzn-device-height': '1080',
    'x-amzn-device-id': device_id,
    'x-amzn-device-language': 'ja_JP',
    'x-amzn-device-model': 'WEBPLAYER',
    'x-amzn-device-time-zone': 'Asia/Tokyo',
    'x-amzn-device-width': '1920',
    'x-amzn-feature-flags': 'hd-supported',
    'x-amzn-music-domain': 'music.amazon.co.jp',
    'x-amzn-os-version': '1.0',
    'x-amzn-page-url': playlist_url,
    'x-amzn-ref-marker': '',
    'x-amzn-referer': '',
    'x-amzn-request-id': request_id,
    'x-amzn-session-id': session_id,
    'x-amzn-timestamp': str(timestamp),
    'x-amzn-user-agent': config.USER_AGENT,
    'x-amzn-video-player-token': '',
    'x-amzn-weblab-id-overrides': '',
  }

  res = session.post(url, headers=request_headers, data=request_body)
  print(res.headers)

  text = res.text

  Path('a.json').write_text(text, encoding='utf-8')
