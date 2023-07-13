# Cyberboy Inc (Backend)

This project is build on Django, servers the APIs for Cyberboy applications.

## Requirements
- docker
- docker-compose

## Setup
First you need to decrypt the .env file, to get all the credentials for setup 
```openssl aes-256-cbc -d -salt -in _env.enc -out .env```
when you make any change to .env file regenerate the encrypted file
```openssl aes-256-cbc -salt -in .env -out _env.enc```

## Setup on Development
``` docker-compose build ```

``` docker-compose up -d```

``` docker-compose exec app bash```

``` python manage.py migrate```

``` python manage.py runserver 0:9001```
