# Social-Media-Backend
A Social Media Backend (Twitter/FB) REST API project implement by Django.

	Designed and developed of all back-end features, including User Profile Service, Login Authentication Service, Feeds Management (post, delete, revise, etc), Interaction functionality, etc
	Applied push model to fanout news feeds.
	Used Redis and Memcached to reduce DB query for tables with many reads and fewer writes.
	Adopt HBase to split DB queries for tables with fewer reads and lot writes.
	Optimized the number of comments and likes storage by employing denormalization to reduce DB queries.
	Introduce Message Queue to deliver asynchronous tasks to minimize response time.


## Getting start
deploy project to docker

### Create a file to save your S3 access key

add local_settings.py in Social-Media-Backend/twitter
```
AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
```

### Create docker image

```
docker build -t twitter/back-end .
```

### run docker compose

```
docker-compose up -d && docker-compose logs --tail=100 -f
```

### Create an admin user

Access to project container
```
docker exec -it twitter /bin/bash
```

Command to create an admin
```
python manage.py createsuperuser
```

### How to access

Access to api list
```
http://0.0.0.0:8000/
```

Access to admin page
```
http://0.0.0.0:8000/admin
```


