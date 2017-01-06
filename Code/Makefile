
.PHONY: mongo_dump mongo_restore

mongo_dump:
	mongodump --archive=dump/ada.archive --gzip --db ada

mongo_restore:
	mongorestore --drop --archive=dump/ada.archive --gzip --db ada

