FROM ubuntu
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends software-properties-common
RUN add-apt-repository ppa:irie/blender 
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y python3 \
                       wget \
                       tar                   
RUN mkdir worker
WORKDIR /worker
RUN mkdir machine
ADD builder/ .