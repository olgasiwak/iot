# API for sth

## Running inside a docker container
```
cd /root/api
docker build -t api_image .
docker run -d --name uvicorn_api -p 8888:8888 api_image
```

## Running it on the disco server
```
cd /root/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8888 &
```

## Docs
[Docs site](http://45.56.71.54:8888/docs#/)
