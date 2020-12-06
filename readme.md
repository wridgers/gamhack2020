# gamhack2020

## deps

- `python` + `requirements.txt`
- `docker`
- `docker-compopse`
- `pandoc`

linux user/group id should be 1000, if not change `docker-compose.yml`. this is so the container can update the mounted
filesystem without permissions issues

## instructions

- run `make` to build `www`
- `docker-compose up -d` to start the web server and arena

## arena

`arena` is a container that loops forever and runs fights

entrypoint is a bash script (`arean.sh`), so you can change `engine.py` and subsequent fights will change.
