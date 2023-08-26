#!/bin/bash
sudo docker run --rm --name api \
    --network zimnet \
    -d -p 5000:5000 zimtechapi:latest \
    && sudo docker cp $HOME/Git/zimtech-api/api.subdomain.conf swag:/config/nginx/proxy-confs