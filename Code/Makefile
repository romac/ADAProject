
.PHONY: mongo_dump mongo_restore

mongo_dump:
	rm -rf dump/ada
	mongodump -d ada

mongo_restore:
	mongorestore -d ada dump/

