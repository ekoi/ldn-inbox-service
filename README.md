# LDN-inbox

poetry build; docker rm -f ldn-inbox-service; docker rmi ekoindarto/ldn-inbox-service:0.1.5; docker build --no-cache -t ekoindarto/ldn-inbox-service:0.1.5 -f Dockerfile . ;docker run -v /Users/akmi/git/DICE/ldn-inbox-service/src/conf:/home/dans/ldn-inbox-service/src/conf  -d -p 1210:1210 --name ldn-inbox-service ekoindarto/ldn-inbox-service:0.1.5; docker exec -it  ldn-inbox-service /bin/bash
