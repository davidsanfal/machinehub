
[![License](http://img.shields.io/:license-gpl-blue.svg?style=flat)](http://opensource.org/licenses/GPL-3.0) 
[![Documentation Status](https://readthedocs.org/projects/machinehub/badge/?version=latest)](https://readthedocs.org/projects/machinehub/?badge=latest)
[![Google Group](https://img.shields.io/badge/-Google%20Group-lightgrey.svg)](https://groups.google.com/forum/?hl=en#!forum/machinehub)
[![Python 3](https://img.shields.io/badge/python-3.x-brightgreen.svg)](https://www.python.org/downloads/)

# What is [machineHUB](docs/machinehub.pdf) ?

## Discover our [machines](https://github.com/bq/machines/)

## Installation

### System dependencies

**[Install FreeCAD](http://www.freecadweb.org/wiki/index.php?title=Install_on_Unix)**


```bash
# Install FreeCAD
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install freecad freecad-doc
```

**[Install Docker](https://docs.docker.com/installation/ubuntulinux/)**

```bash
# Install Docker
sudo apt-get install wget
wget -qO- https://get.docker.com/ | sh
sudo service docker start
```

`Warning`

```bash
# Create a Docker group
sudo usermod -aG docker ubuntu
```

### Python requirements

```bash
cd machinehub
sudo -H pip install -r requirements.txt
```

## Execute

Build the machinehub docker image to use as base to the machine images.

```bash
cd machinehub/machinehub/docker/
docker build -t machinehub .
```

Launch the webapp.

```bash
cd machinehub
python launcher.py
```

gunicorn.

```bash
cd machinehub
gunicorn -w 8 -b 127.0.0.1:5000 launcher:app
```

## Configure

### How to change the address or the admin info

Edit `~/.machinehub/machinehub.conf` yo chage the address, port, or the admin info.

```
[server]
host: 127.0.0.1
port: 5000
[users]
admin: admin #user: password
```

# Try Machinehub

[localhost:5000](http://localhost:5000/)

![](docs/img/home.png)

[localhost:5000/upload](http://localhost:5000/upload)

![](docs/img/upload.png)

Select all the machine .zip files.

![](docs/img/files.png)

Clic in the blue upload button and machinehub will redirect your browser to the home page with the machines. loaded
![](docs/img/uploaded.png)

