# amzmusicplaylistdumper

```shell
python3 amzmusicplaylistdumper/main.py embed_playlist_csv --playlist_asin ""

python3 amzmusicplaylistdumper/main.py selenium_playlist_json --playlist_asin ""
```

```shell
docker compose build

docker compose up -d selenium
docker compose run --rm app selenium_playlist_json --playlist_asin ""

# Wait some seconds

docker compose down
```
