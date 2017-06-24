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
import uuid
import struct

from ant.core import driver
from ant.core.node import Node, Network
from ant.core.event import EventCallback
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER
from ant.core.message import ChannelBroadcastDataMessage

from rx.concurrency import TimeoutScheduler
from rx.subjects import Subject

_LOGGER = logging.getLogger('powerbulb.ant')


class AntChannelEventCallback(EventCallback):
    def __init__(self, source):
        self.source = source

    def can_decode(self, payload):
        raise NotImplementedError()

    def decode(self, payload):
        raise NotImplementedError()

    def process(self, msg, channel):
        if not isinstance(msg, ChannelBroadcastDataMessage):
            return
        payload = msg.payload
        if not self.can_decode(payload):
            return
        value = self.decode(payload)
        _LOGGER.debug('received: %s (value=%d)', map(str, msg.payload), value)
        self.source.values.on_next(value)


class AntPowerChannelEventCallback(AntChannelEventCallback):
    def can_decode(self, payload):
        return payload[1] == 0x10  # Standard Power-Only message

    def decode(self, payload):
        # ANT+ Device Profile: Bicycle Power (Standard Power-Only Main Data Page)
        # -----------------------------------------------------------------
        # Byte | Description              | Length   | Units | Notes
        # -----------------------------------------------------------------
        # 0    | Page Number              | 1 bytes  | -     | ...
        # ...
        # 3    | Instantaneous Cadence    | 1 bytes  | RPM   | 0-254 (Invalid=0xFF)
        # ...
        # 6-7  | Instantaneous Power LSB  | 2 bytes  | W     | 0-65.535kW
        # -----------------------------------------------------------------
        return struct.unpack('h', payload[-2:])[0]


class AntHeartRateChannelEventCallback(AntChannelEventCallback):
    def can_decode(self, payload):
        return True

    def decode(self, payload):
        # ANT+ Device Profile: Heart Rate
        # -----------------------------------------------------------------
        # Byte | Description         | Length  | Notes
        # -----------------------------------------------------------------
        # ...
        # 6    | Heart Beat Count    | 1 byte  | Rollover at 255 counts
        # 7    | Computed Heart Rate | 1 byte  | Invalid=0x00, max 255bpm.
        # -----------------------------------------------------------------
        return payload[-1]


class AntDataSource(object):
    def __init__(self, channel, callback):
        self._values = TimeoutSubject()
        channel = channel
        channel.registerCallback(callback)

    @property
    def values(self):
        return self._values


class TimeoutSubject(Subject):
    TIMEOUT_MS = 30 * 1000

    def __init__(self, scheduler=None):
        super(TimeoutSubject, self).__init__()
        self._scheduler = scheduler or TimeoutScheduler()
        self._timer = None
        self._reset()

    def on_next(self, value):
        self._reset()
        super(TimeoutSubject, self).on_next(value)

    def _reset(self):
        if self._timer is not None:
            self._timer.dispose()
        self._timer = self._scheduler.schedule_periodic(self.TIMEOUT_MS,
                                                        self._timeout)

    def _timeout(self, _):
        _LOGGER.warn('timeout (%d secs) exceeded', self.TIMEOUT_MS / 1000)
        super(TimeoutSubject, self).on_completed()


class AntPowerDataSource(AntDataSource):
    def __init__(self, channel):
        AntDataSource.__init__(self, channel,
                               AntPowerChannelEventCallback(self))


class AntHeartRateDataSource(AntDataSource):
    def __init__(self, channel):
        AntDataSource.__init__(self, channel,
                               AntHeartRateChannelEventCallback(self))


class AntDataSourceFactory:
    def create(self, device_type, channel):
        _LOGGER.debug('creating device_type=%s', device_type)
        if device_type == 'hr':
            return AntHeartRateDataSource(channel)
        elif device_type == 'power':
            return AntPowerDataSource(channel)
        else:
            raise ValueError(
                "'{}' is not a supported device type".format(device_type))


class AntChannelFactory(object):
    def __init__(self, node):
        self.node = node

    def create_bike_power(self, network, device_number=0):
        return self.create(network, 11, device_number)

    def create_heart_rate(self, network, device_number=0):
        return self.create(network, 120, device_number)

    def create(self, network, device_type, device_number):
        device_type = self.get_device_type(device_type)
        name = 'C:{}'.format(str(uuid.uuid1()))
        _LOGGER.info(
            'creating network=%s channel=%s device_type=%d, device_number=%d',
            name, network, device_type, device_number)
        channel = self.node.getFreeChannel()
        channel.name = name
        channel.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
        channel.setID(device_type, device_number, 0)
        channel.searchTimeout = TIMEOUT_NEVER
        channel.period = 8070
        channel.frequency = 57
        channel.open()
        return channel

    @staticmethod
    def get_device_type(device_type):
        if device_type == 'hr':
            return 120
        elif device_type == 'power':
            return 11
        else:
            return device_type


class AntNodeFactory(object):
    def create(self, device, key='\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'):
        _LOGGER.info('creating device=%s', device)
        node = Node(driver.USB1Driver(device))
        node.start()
        network = Network(name='N:ANT+', key=key)
        node.setNetworkKey(0, network=network)
        return node, network
