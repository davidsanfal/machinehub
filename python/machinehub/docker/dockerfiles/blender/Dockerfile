FROM ubuntu
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends software-properties-common
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y python3 \
                       wget \
                       tar
RUN wget http://ftp.halifax.rwth-aachen.de/blender/release/Blender2.76/blender-2.76b-linux-glibc211-x86_64.tar.bz2
RUN tar -jxvf blender-2.76b-linux-glibc211-x86_64.tar.bz2                     
RUN mkdir worker
WORKDIR /worker
RUN mkdir machine
ADD builder/ .