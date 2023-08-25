sudo docker run --rm --name zimtechapi \
    --network zimnet \
    -d --restart=unless-stopped -p 5000:5000 zimtechapi:latest