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
# limitations under the License.#

import logging

_LOGGER = logging.getLogger('powerbulb.controller')


class PowerBulbController(object):
    BUFFER_TIME_MS = 1000

    def __init__(self, source, bulb, color_map, scheduler=None):
        self._source = source
        self._bulb = bulb
        self._color_map = color_map
        self._scheduler = scheduler
        self._subscription = None

    def __enter__(self):
        self._subscription = self._source.values \
            .buffer_with_time(self.BUFFER_TIME_MS, scheduler=self._scheduler) \
            .where(lambda x: len(x) > 0) \
            .select(lambda x: float(sum(x)) / len(x)) \
            .subscribe(on_next=self._update)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._subscription.dispose()

    def _update(self, value):
        color = self._color_map.get_color(value)
        self._bulb.set_color(color)
        _LOGGER.debug('set color, value=%d, color=%s', value, color)
