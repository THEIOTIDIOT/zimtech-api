#!/bin/bash
sudo docker run --rm --name api \
    --network zimnet \
    -d --restart=unless-stopped -p 5000:5000 zimtechapi:latest \
    && sudo docker exec -it swag rm /config/nginx/proxy-confs/api.subdomain.conf \
    && sudo docker cp $HOME/Git/zimtech-api/api.subdomain.conf swag:/config/nginx/proxy-confs