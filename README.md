## Introduction

**PowerBulb** connects a Smart Trainer to a Smart Lightbulb (e.g. [LIFX](https://eu.lifx.com/products/lifx)) using ANT and a Raspberry Pi.

### Video

[![](http://img.youtube.com/vi/BCdriQX_YVw/0.jpg)](http://www.youtube.com/watch?v=BCdriQX_YVw "YouTube Video")

## Hardware Requirements

1. Smart Trainer, Power Meter or HR monitor
2. Raspberry Pi + Squeeze 
3. ANT+ USB Dongle (e.g. Dynastream ANTUSB-m)
4. LIFX Smart Bulb

## Software Installation

### ANT+ Adapter

Configure a `udev` rule for the ANT+ adapter so to create a serial USB device.

Create a file at `sudo vi /etc/udev/rules.d/garmin-ant2.rules` containing the following line:

    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1009", RUN+="/sbin/modprobe usbserial vendor=0x0fcf product=0x1009", MODE="0666", OWNER="pi", GROUP="root"

Note that depending on your specific adapter, `idVendor` and `idProduct` might need changing. Check your device using
`dmesg | grep usb`.

### Application (Raspberry Pi)

Run the following commands to install the Python requirements in a virtual environment:

    $ sudo apt-get install libncurses5-dev
    $ pip install virtualenv
    $ python -m virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements_pi.txt
    $ git submodule update --init ext/python-ant
    $ cd ext/python-ant
    $ python setup.py install
    $ cd ../../

## Running

You can start running by using:

    $ python app.py -c config.json
    
### Generating a FTP Color Map

**PowerBulb** uses a map of power (W) or heart rate (BPM) to color (HSBK). The default map (`colors/ftp.json`) is based
on a Functional Threshold Power (FTP) of 225W.

You can generate a new color map based on your own FTP using the following command:

    $ python create_ftp_color_map.py --ftp 320 --output colors/ftp.json --kind discrete
    
The colors match Zwift: Z1 (gray), Z2 (blue), Z3 (green), Z4 (yellow), Z5 (orange), Z6 (red).
    
Note: If you'd rather use heart rate, use `create_hr_color_map.py` instead and edit `config.json` to point
at the new file.

### Configuration

The application configuration is stored in `config.json` in the root of the repository.

The contents of the file should be as follows:

    {
        "device": {
            "path": "/dev/ttyUSB0", 
            "type": "power", 
            "number": 0
        }, 
        "bulb": {
            "ip": "192.168.254.50", 
            "mac": "d0:73:d5:21:5c:6d"
        }, 
        "color_map": "colors/ftp.json"
    }
    
The configuration can be customized as follows:

#### device

| Path     | Description                                    |
| ---------|:-----------------------------------------------|
| `path`   | The USB/serial ANT+ device                     |
| `type`   | The device type (can be `power` or `hr`)       |
| `number` | The device number (can be `0` for all devices) |

#### bulb

| Path     | Description                                    |
| ---------|:-----------------------------------------------|
| `ip`     | The IP address of the LIFX bulb                |
| `mac`    | The physical address of the LIFX bulb          |

### color_map

| Path        | Description                                                 |
| ------------|:------------------------------------------------------------|
| `color_map` | The path to the JSON file containing to value -> color map  |

### Using supervisord

You can deamonize the application and detach it from the terminal using [supervisord](http://supervisord.org/). This
will continually run the application and restart it if no device is found.

    $ supervisord -c supervisord.conf
    $ supervisorctl status
    app                              RUNNING   pid 3773, uptime 0:00:25



## Other Utilities

* `sweep_color_map.py -c config.json -min 50 -max 500` (test the color map and sweep a W range)
* `find_lifx_devices.py` (dumps LIFX color lights on the LAN)
