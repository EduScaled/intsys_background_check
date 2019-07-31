docker rm -f intsys_background_check_instance_1
docker build -t intsys_background_check .
docker run -d --name intsys_background_check_instance_1 intsys_background_check

docker rm -f selenium
docker run -d -p 4444:4444 --name selenium -v /dev/shm:/dev/shm selenium/standalone-chrome:3.141.59-dubnium
