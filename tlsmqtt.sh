#!/bin/bash

# Copyright 2020 OBAYASHI CORPORATION
# 2021.2.14
# tlsmqtt.sh
# ver 0.1
# mitsuboshi.kunihito@obayashi.co.jp

sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto

mosquitto_sub -d -t "topic/test"
mosquitto_pub -d -t "topic/test" -m "Hello World."

openssl genrsa -des3 -out ca.key 2048
openssl req -new -x509 -days 1096 -key ca.key -out ca.crt
openssl genrsa -out server.key 2048
openssl req -new -out server.csr -key server.key # Common Name = 192.168.73.163
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 366

sudo mkdir /etc/mosquitto/ca_certificates/PCA/
sudo mkdir /etc/mosquitto/ca_certificates/PCA/private/
sudo cp ca.key /etc/mosquitto/ca_certificates/PCA/private/
sudo chown root:root /etc/mosquitto/ca_certificates/PCA/private/ca.key
sudo chmod 600 /etc/mosquitto/ca_certificates/PCA/private/ca.key
sudo chmod 700 /etc/mosquitto/ca_certificates/PCA/private

sudo cp server.key server.crt /etc/mosquitto/certs/

sudo cp server.csr ca.srl /etc/mosquitto/ca_certificates/PCA/

sudo cp ca.crt /etc/mosquitto/ca_certificates/
ln -s /etc/mosquitto/ca_certificates/ca.crt ~/ca4mosquitto.crt

rm ca.key server.csr ca.crt ca.srl server.key server.crt
sudo vi /etc/mosquitto/mosquitto.conf
# add
#	port 8883
#	cafile /etc/mosquitto/ca_certificates/ca.crt
#	keyfile /etc/mosquitto/certs/server.key
#	certfile /etc/mosquitto/certs/server.crt
mosquitto -c /etc/mosquitto/mosquitto.conf

mosquitto_sub -d -h 192.168.73.163 -t "topic/test" --cafile /etc/mosquitto/ca_certificates/ca.crt -p 8883
mosquitto_pub -d -h 192.168.73.163 -t "topic/test" -m "hello world" --cafile /etc/mosquitto/ca_certificates/ca.crt -p 8883


cat 3_20210212054140.json | jq . > gwfile.json
