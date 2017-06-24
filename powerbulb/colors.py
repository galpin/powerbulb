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

import numpy as np
import jsonpickle
from collections import namedtuple

Color = namedtuple('Color', ['hue', 'saturation', 'brightness', 'kelvin'])

jsonpickle.set_encoder_options('json', indent=4)


class ColorMap(object):
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(jsonpickle.encode(self, f))

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return jsonpickle.decode(f.read())

    def get_color(self, value):
        raise NotImplementedError()


class DiscreteColorMap(ColorMap):
    def __init__(self, color_stops):
        assert len(color_stops) > 0
        self.color_stops = color_stops

    def get_color(self, value):
        result = None
        for i, stop in enumerate(self.color_stops):
            lower, colour = stop
            if i == 0:
                result = colour
                continue
            if lower > value:
                break
            result = colour
        return result


class ContinuousColorMap(ColorMap):
    def __init__(self, color_stops):
        assert len(color_stops) > 0
        self.values = []
        self.hue = []
        self.saturation = []
        self.brightness = []
        self.kelvin = []
        for value, color in color_stops:
            self.values.append(value)
            self.hue.append(color.hue)
            self.saturation.append(color.saturation)
            self.brightness.append(color.brightness)
            self.kelvin.append(color.kelvin)

    def get_color(self, value):
        h = np.interp(value, self.values, self.hue)
        s = np.interp(value, self.values, self.saturation)
        b = np.interp(value, self.values, self.brightness)
        k = np.interp(value, self.values, self.kelvin)
        return Color(h, s, b, k)


def _create_color_map(stops, kind):
    if kind == 'discrete':
        return DiscreteColorMap(stops)
    elif kind == 'continuous':
        return ContinuousColorMap(stops)
    else:
        raise ValueError('Unknown kind: "{}".'.format(kind))


def create_ftp_color_map(ftp, kind='discrete'):
    """
    Creates a color profile based on your Functional Threshold Power (FTP).
    :param ftp: The FTP value (specified in W).
    :param kind: The kind of color map (either 'discrete' or 'continuous').
    :return: A color map corresponding to `ftp`.
    """
    z1 = Color(0.08, 0.0, 1.0, 0.14)  # Grey
    z2 = Color(0.66, 1.0, 1.0, 0.14)  # Blue
    z3 = Color(0.32, 1.0, 1.0, 0.14)  # Green
    z4 = Color(0.17, 1.0, 1.0, 0.14)  # Yellow
    z5 = Color(0.11, 1.0, 1.0, 0.14)  # Coral
    z6 = Color(0.00, 1.0, 1.0, 0.06)  # Red
    stops = [
        (ftp * 0.00, z1),
        (ftp * 0.56, z2),
        (ftp * 0.76, z3),
        (ftp * 0.90, z4),
        (ftp * 1.06, z5),
        (ftp * 1.21, z6)
    ]
    return _create_color_map(stops, kind)


def create_hr_color_map(heart_rate, kind='discrete'):
    """
    Creates a color profile based on your Maximum Heart Rate (MHR).
    :param heart_rate: The MHR value (specified in BPM).
    :param kind: The kind of color map (either 'discrete' or 'continuous').
    :return: A color map corresponding to `heart_rate`.
    """
    z0 = Color(0.08, 0.0, 1.0, 0.18)  # White
    z1 = Color(0.08, 0.0, 1.0, 0.14)  # Grey
    z2 = Color(0.66, 1.0, 1.0, 0.14)  # Blue
    z3 = Color(0.32, 1.0, 1.0, 0.14)  # Green
    z4 = Color(0.17, 1.0, 1.0, 0.14)  # Yellow
    z5 = Color(0.11, 1.0, 1.0, 0.14)  # Coral
    z6 = Color(0.00, 1.0, 1.0, 0.06)  # Red
    stops = [
        (heart_rate * 0.00, z0),
        (heart_rate * 0.60, z1),
        (heart_rate * 0.65, z2),
        (heart_rate * 0.75, z3),
        (heart_rate * 0.82, z4),
        (heart_rate * 0.89, z5),
        (heart_rate * 0.94, z6)
    ]
    return _create_color_map(stops, kind)
