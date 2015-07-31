
[![License](http://img.shields.io/:license-gpl-blue.svg?style=flat)](http://opensource.org/licenses/GPL-3.0) [![Google Group](https://img.shields.io/badge/-Google%20Group-lightgrey.svg)](https://groups.google.com/forum/?hl=en#!forum/machinehub)

# What is [machineHUB](docs/machinehub.pdf) ?


## Discover our [machines](https://github.com/bq/machines/)

## Installation

### Python requirements

```bash
cd machinehub
sudo -H pip install -r requirements.txt
```

### Engines

 * [FreeCAD](http://www.freecadweb.org/wiki/index.php?title=Installing)

```bash
sudo apt-get install freecad
```


## Execute

```bash
cd machinehub
python launcher.py
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

### How to add pyooml to machinehub

```bash
git clone https://github.com/Obijuan/friki.git
cd friki
cp pyooml.py ~/.machinehub/machines/
cp HMatrix.py ~/.machinehub/machines/
```