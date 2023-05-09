# amzmusicplaylistdumper

Copy `template.env` to `.env` and set values.

`ROOT_DIR` owner must be `1000:1000`(uid:gid).

```shell
docker compose build

docker compose up -d selenium
docker compose up app

# Wait some seconds

docker compose down
```
