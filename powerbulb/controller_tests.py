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

import unittest

from mock import Mock
from rx.subjects import Subject
from rx.testing import TestScheduler

from powerbulb.controller import PowerBulbController
from powerbulb.colors import Color, DiscreteColorMap


class PowerBulbControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.source = Mock()
        self.source.values = Subject()
        self.bulb = Mock()
        self.bulb.turn_on = Mock()
        self.bulb.set_color = Mock()
        self.color_map = DiscreteColorMap([
            (1, Color(1, 1, 1, 1)),
            (2, Color(2, 2, 2, 2)),
            (3, Color(3, 3, 3, 3))
        ])
        self.scheduler = TestScheduler()
        self.sut = PowerBulbController(self.source, self.bulb, self.color_map,
                                       scheduler=self.scheduler)

    def test_sets_bulb_to_color_from_map(self):
        with self.sut:
            expected = self.color_map.get_color(1)
            self.source.values.on_next(1)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            self.bulb.set_color.assert_called_with(expected)

            expected = self.color_map.get_color(2)
            self.source.values.on_next(2)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            self.bulb.set_color.assert_called_with(expected)

            expected = self.color_map.get_color(3)
            self.source.values.on_next(3)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            self.bulb.set_color.assert_called_with(expected)

    def test_uses_average_over_value_during_buffer_window(self):
        with self.sut:
            self.source.values.on_next(1)
            self.source.values.on_next(2)
            self.source.values.on_next(3)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            expected = self.color_map.get_color(2)  # e.g. (1+2+3)/3=2
            self.bulb.set_color.assert_called_with(expected)

    def test_does_not_throw_when_no_values_are_received(self):
        with self.sut:
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
            self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)

    def test_disposes_of_values_subscription_on_exit(self):
        with self.sut:
            pass
        self.source.values.on_next(1)
        self.scheduler.advance_by(PowerBulbController.BUFFER_TIME_MS)
        self.bulb.set_color.assert_not_called()
