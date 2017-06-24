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
import threading

from powerbulb import load_configuration
from powerbulb.net import (
    AntNodeFactory,
    AntChannelFactory,
    AntDataSourceFactory
)
from powerbulb.bulb import LifxLightBulb
from powerbulb.colors import ColorMap
from powerbulb.controller import PowerBulbController

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

_LOGGER = logging.getLogger('powerbulb')


def main(configuration):
    device = configuration['device']
    bulb = configuration['bulb']

    node, network = AntNodeFactory().create(device['path'])
    channel = AntChannelFactory(node).create(network, device['type'],
                                             device['number'])
    source = AntDataSourceFactory().create(device['type'], channel)

    bulb = LifxLightBulb(bulb['ip'], bulb['mac'])
    color_map = ColorMap.load(configuration['color_map'])

    with PowerBulbController(source, bulb, color_map):
        completed = threading.Event()

        def on_error(e):
            _LOGGER.exception(e)
            completed.set()

        source.values.subscribe(on_error=on_error,
                                on_completed=lambda: completed.set())
        try:
            completed.wait()
        except KeyboardInterrupt:
            pass

    channel.close()
    node.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Power meter meets smart lightbulb!')
    parser.add_argument('--configuration', '-c', type=str, required=True,
                        help='The configuration file path.')
    args = parser.parse_args()
    main(load_configuration(args.configuration))
