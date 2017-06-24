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

import argparse
import logging
import sys
import time

from powerbulb import load_configuration
from powerbulb.bulb import LifxLightBulb
from powerbulb.colors import ColorMap

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

_LOGGER = logging.getLogger()


def main(configuration, min, max, step, delay):
    bulb = LifxLightBulb(configuration['bulb']['ip'],
                         configuration['bulb']['mac'])
    color_map = ColorMap.load(configuration['color_map'])

    for value in range(min, max + step, step):
        _LOGGER.info('value = %d', value)
        color = color_map.get_color(value)
        bulb.set_color(color)
        time.sleep(delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Sweeps the value in a color map by changing the color of the bulb.")
    parser.add_argument('--configuration', '-c', type=str, required=True,
                        help='The configuration file path.')
    parser.add_argument('--min', '-min', type=int, required=True,
                        help='The minimum value.')
    parser.add_argument('--max', '-max', type=int, required=True,
                        help='The maximum value.')
    parser.add_argument('--step', '-s', type=int, default=1,
                        help='The step size.')
    parser.add_argument('--delay', '-d', type=int, default=0.25,
                        help='The delay between colors, specified in seconds.')
    args = parser.parse_args()
    main(load_configuration(args.configuration), args.min, args.max, args.step,
         args.delay)
