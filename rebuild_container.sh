#!/bin/bash
sudo docker stop api \
&& sudo docker rm api \
&& sudo docker build zimtechapi:latest . \
&& bash run_container.sh