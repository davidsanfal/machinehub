FROM ubuntu
RUN apt-get -y update
RUN apt-get install -y freecad \
                       python
RUN mkdir worker
WORKDIR /worker
RUN mkdir machine
ADD builder/ .