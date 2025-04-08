git add .;git commit -m "update";git push

docker build -f docker/python/Dockerfile.prod -t nttkimsong/dejavu-query-app:latest .
docker push nttkimsong/dejavu-query-app:latest