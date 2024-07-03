#docker run --name dup-envoy -d -p 8888:8888 -p 9901:9901 -v /c/projects/dup/tools/envoy:/etc/envoy envoyproxy/envoy:v1.24-latest
docker restart dup-envoy
docker logs dup-envoy
#docker exec -it dup-envoy /bin/sh
