sudo docker run --rm --name zimtechapi \
    --network zimnet \
    --ip 172.27.0.4 \
    -d --restart=unless-stopped -p 5000:5000 zimtechapi:latest