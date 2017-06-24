# Copyright 2017 Martin Galpin (galpin@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from lifxlan import Light

_LOGGER = logging.getLogger('powerbulb.bulb')


def to_hsbk(color):
    values = (color.hue, color.saturation, color.brightness, color.kelvin)
    return map(lambda x: x * 65535, values)


class LightBulb(object):
    def get_power(self):
        raise NotImplementedError()

    def turn_on(self):
        raise NotImplementedError()

    def turn_off(self):
        raise NotImplementedError()

    def set_color(self, color):
        """
        Sets the color of the bulb, specified in HSBK:

        Hue: range 0 to 65535
        Saturation: range 0 to 65535
        Brightness: range 0 to 65535
        Kelvin: range 2500 (warm) to 9000 (cool)

        :param color: The color to set, specified as a tuple of HSBK values.
        """
        raise NotImplementedError()


class LifxLightBulb(LightBulb):
    def __init__(self, ip_addr, mac_addr):
        _LOGGER.info('creating ip_addr=%s mac_addr=%s', ip_addr, mac_addr)
        self._device = Light(mac_addr, ip_addr)

    def get_power(self):
        _LOGGER.info('getting power')
        return self._device.get_power() == 65536

    def turn_on(self):
        _LOGGER.info('turning on')
        self._device.set_power(True)

    def turn_off(self):
        _LOGGER.info('turning off')
        self._device.set_power(False)

    def set_color(self, color):
        _LOGGER.debug('setting color=%s', color)
        self._device.set_color(to_hsbk(color), rapid=True)
