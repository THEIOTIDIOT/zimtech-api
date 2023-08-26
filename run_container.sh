#!/bin/bash
sudo docker run --name api \
    --network zimnet \
    -d --restart=unless-stopped -p 5000:5000 zimtechapi:latest \
    && sudo docker cp $HOME/Git/zimtech-api/api.subdomain.conf swag:/config/nginx/proxy-confs