<p align="center"><img src="docs/logo/machinehub.png" align="center"</p>
<p align="center"><img src="docs/logo/bq-logo-human-right-technology.png" width="400" align="center">

[![Documentation Status](https://readthedocs.org/projects/machinehub/badge/?version=latest)](https://readthedocs.org/projects/machinehub/?badge=latest) [![Python 3](https://img.shields.io/badge/python-3.x-brightgreen.svg)](https://www.python.org/downloads/)</p>

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

# How to use Machinehub

You can use the [Advanced REST client](https://chrome.google.com/webstore/detail/advanced-rest-client/hgmloofddffdnphfgcellkdfbfbjeloo) to test Machinehub. It is a Chorme extension with an easy REST client.

**Base URL http://0.0.0.0:5000/v1**

| Call  | Type | Content-Type | Header | Payload | Info |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| /machine/{machinename}/{username} | PUT | multipart-form-data | Authorization: Bearer {AUTH_TOKEN} |{machine_name}.zip ||
| /machine/{machinename}/{username} | GET |||||
| /machine/{machinename}/{username} | POST | multipart-form-data | | input.zip ||
| /machine/{machinename}/{username} | POST | application/json || Json with the machine input data ||
| /machine/{machinename}/{username} | DELETE |  | Authorization: Bearer {AUTH_TOKEN} ||
| /users/authenticate | GET || Authorization: Bearer {AUTH_TOKEN} ||http basic authentication. Return the AUTH_TOKEN|
| /users/check_credentials | GET || Authorization: Bearer {AUTH_TOKEN} |||

## License

Machinehub is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/). Please read the LICENSE files for more details.

<p align="center">
<img src="docs/logo/by-sa.png" width="200" align = "center">
</p>