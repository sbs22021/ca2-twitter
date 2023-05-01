# Mongo DB installation

https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

## 1. Import the publickey used by the package management system

```sh
sudo apt-get install gnupg
```

Issue the following command to import the MongoDB public GPG Key from 
https://pgp.mongodb.com/server-6.0.asc:


```sh
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor
```

## 2. Create a list for mongodb

```sh
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
```

## 3. Reload local package database.
Issue the following command to reload the local package database:

```sh
sudo apt-get update
```

## 4. Install latest stable version

```sh
sudo apt-get install -y mongodb-org
```

Restart the server
```sh
sudo shutdown -r now
```

## 5. Attach disk to mongodb data folder

Refer to MountDisk.md file to mount ssd disk on `/var/lib/mongodb` for performance. log files will be on separate disk `/var/log/mongodb`

## 6. Configuration file
Configuration file `/etc/mongod.conf` https://www.mongodb.com/docs/manual/reference/configuration-options/#std-label-conf-file

# Start / Stop Mongo

Start:

```sh
sudo systemctl start mongod
```

Status:
```sh
sudo systemctl status mongod
```

Stop:
```sh
sudo systemctl stop mongod
```


## 7. Install mongo spark connector 3.0.1

https://www.mongodb.com/docs/spark-connector/current/
https://spark-packages.org/package/mongodb/mongo-spark
https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/3.0.1/mongo-spark-connector_2.12-3.0.1.jar



