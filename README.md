# Social-Media-Backend(twitter)
A twitter-like backend project implement by Django.

## Getting start
### Deploy in Docker

install Docker Desktop

### configuration files
#### Create configuration files
Create configuration files like below
```
    BackEnd
    	|── Dockerfile
	├── docker-compose.yaml
	├── compose
	│   	├── mysql
	│	│     ├── conf
	│	│     │	    │── my.cnf
	│	│     ├── init
	│	│	    │── init.sql
	│   	│   
	│	├── redis
	│	      ├── conf
	│		    │── redis.conf
	│

```

Dockerfile
```
FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /back-end-code
WORKDIR /back-end-code
COPY requirements.txt /back-end-code
RUN pip install -r requirements.txt
COPY . /back-end-code
```

docker-compose.yaml
```
version: "3"
services:
  twitter:
    container_name: twitter
    restart: always
    depends_on:
      - mysql
      - redis
      - memcached
      - hbase
    volumes:
      - .:/other-code
    links:
      - mysql
      - redis
      - memcached
      - hbase
    tty: true
    image: twitter/back-end:latest
    ports:
      - "8000:8000"
    command:
      - /bin/bash
      - -c
      - |
        sleep 60
        echo sleep over
        python manage.py makemigrations
        python manage.py migrate
        python manage.py runserver 0.0.0.0:8000

  mysql:
    container_name: mysql
    platform: linux/amd64
    volumes:
      - ./mysql:/var/lib/mysql:rw 
      - ./compose/mysql/conf/my.cnf:/etc/mysql/my.cnf 
      - ./compose/mysql/init:/docker-entrypoint-initdb.d/ 
    image: mysql:8.0 #
    command: --default-authentication-plugin=mysql_native_password --mysqlx=0
    security_opt:
      - seccomp:unconfined
    expose:
      - 3306
    ports:
      - "3306:3306" 
    restart: always 
    environment:
      - MYSQL_ROOT_PASSWORD=yourpassword
      - MYSQL_DATABASE=twitter

  redis:
    container_name: redis
    image: redis:latest
    expose:
      - 6379
    ports:
      - "6379:6379"
    volumes:
      - ./redis:/data
      - ./compose/redis/conf/redis.conf:/etc/redis/redis.conf
    restart: always
    command: redis-server /etc/redis/redis.conf

  memcached:
    container_name: memcached
    image: memcached:latest
    expose:
      - 11211
    restart: always
    ports:
      - "11211:11211"
    entrypoint:
      - memcached
      - -m 64

  hbase:
    container_name: hbase
    image: harisekhon/hbase:latest
    logging:
      driver: none
    external_links:
      - hadoop
      - zookeeper
    ports:
      - 16000:16000
      - 16010:16010
      - 16030:16030
      - 16201:16201
      - 16301:16301
      - 9090:9090
      - 9095:9095
      - 8080:8080
      - 8085:8085
      - 2181:2181
    volumes:
      - ./hbase:/hbase-data
      - "/etc/timezone:/etc/timezone:ro"
      - "/etc/localtime:/etc/localtime:ro"  
```

my.cnf
```
#
# The MySQL Server configuration file.
#
# For explanations see
# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

[mysqld]
pid-file = /var/run/mysqld/mysqld.pid
socket = /var/run/mysqld/mysqld.sock
datadir = /var/lib/mysql
secure-file-priv= NULL
port = 3306
bind-address=0.0.0.0
skip_name_resolve = 1

# Custom config should go here
!includedir /etc/mysql/conf.d/
```

init.sql
```
# compose/mysql/init/init.sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

redis.conf
```
# ./compose/redis/conf/redis.conf
# https://juejin.cn/post/6844903716290576392
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
port 6379
bind 0.0.0.0
```

#### add local setting file
add local_settings.py in Social-Media-Backend/twitter
```
AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
```

#### modify setting file
modify ALLOWED_HOST, mysql host, Redis host, Memcached host and HBase host in settings.py file in Social-Media-Backend/twitter


```
ALLOWED_HOST = ['*']
```

```
DATABASES = {
'default': {
 'ENGINE': 'django.db.backends.mysql',
 'NAME': 'twitter',
 'HOST': 'mysql',
 'PORT': '3306',
 'USER': 'root',
 'PASSWORD': 'yourpassword',
 }
}

```

```
HBASE_HOST = 'hbase'
CACHES = {
'default': {
 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
 'LOCATION': 'memcached:11211', 
 'TIMEOUT': 86400,
},
'testing': {
 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
 'LOCATION': 'memcached:11211', 
 'TIMEOUT': 86400,
 'KEY_PREFIX': 'testing',
},
'ratelimit': {
 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
 'LOCATION': 'memcached:11211', 
 'TIMEOUT': 86400 * 7,
 'KEY_PREFIX': 'rl',
 },
}
REDIS_HOST = 'redis'
```

#### modify requirement.txt
modify requirement.txt
```
boto3==1.16.36
botocore==1.19.63
celery==5.0.5
click==7.1.2
cryptography==2.1.4
Django==3.1.3
django-filter==2.4.0
django-model-utils==4.1.1
django-notifications-hq==1.6.0
django-ratelimit==3.0.1
django-storages==1.10.1
djangorestframework==3.12.2
django-tastypie
happybase==1.2.0
kombu==5.1.0
mysqlclient==2.0.3
pycrypto==2.6.1
python-memcached==1.59
pytz==2021.1
PyYAML==6.0
redis==3.5.3
requests==2.18.4
thriftpy2==0.4.14
Twisted==17.9.0
notifications==0.3.2
pymysql==1.0.2
mysqlclient==2.0.3
python-dateutil==2.8.2
```

### Create docker image

```
docker build -t twitter/back-end .
```

### run docker compose

```
docker-compose up -d && docker-compose logs --tail=100 -f
```

### How to access

```
http://0.0.0.0:8000/
```

