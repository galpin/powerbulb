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
import numpy as np

from tempfile import NamedTemporaryFile

from powerbulb.colors import Color, DiscreteColorMap, ContinuousColorMap


def assert_color_equal(first, second):
    np.testing.assert_almost_equal(first.hue, second.hue)
    np.testing.assert_almost_equal(first.saturation, second.saturation)
    np.testing.assert_almost_equal(first.brightness, second.brightness)
    np.testing.assert_almost_equal(first.kelvin, second.kelvin)


def interpolate(color_stops, x):
    xp = [stop for stop, _ in color_stops]
    h = np.interp(x, xp, [color.hue for _, color in color_stops])
    s = np.interp(x, xp, [color.saturation for _, color in color_stops])
    b = np.interp(x, xp, [color.brightness for _, color in color_stops])
    k = np.interp(x, xp, [color.kelvin for _, color in color_stops])
    return Color(h, s, b, k)


class DiscreteColorMapTestCase(unittest.TestCase):
    def test_can_round_trip(self):
        expected = DiscreteColorMap([
            (0, Color(1, 10, 100, 1000)),
            (5, Color(2, 20, 200, 2000)),
            (10, Color(3, 30, 300, 3000))
        ])
        with NamedTemporaryFile() as f:
            expected.save(f.name)
            actual = DiscreteColorMap.load(f.name)
        self.assertEqual(len(expected.color_stops), len(actual.color_stops))
        for x, y in zip(expected.color_stops, actual.color_stops):
            self.assertEqual(x, y)

    def test_can_get_colors_at_stops(self):
        color_stops = [
            (0, Color(1, 10, 100, 1000)),
            (5, Color(2, 20, 200, 2000)),
            (10, Color(3, 30, 300, 3000))
        ]
        sut = DiscreteColorMap(color_stops)
        for value, color in color_stops:
            assert_color_equal(color, sut.get_color(value))

    def test_can_get_color_between_stops(self):
        stop1 = Color(1, 10, 100, 1000)
        stop2 = Color(2, 20, 200, 2000)
        stop3 = Color(3, 30, 300, 3000)
        color_stops = [
            (0, stop1),
            (3, stop2),
            (5, stop3)
        ]
        sut = DiscreteColorMap(color_stops)
        assert_color_equal(stop1, sut.get_color(0))
        assert_color_equal(stop1, sut.get_color(1))
        assert_color_equal(stop1, sut.get_color(2))
        assert_color_equal(stop2, sut.get_color(3))
        assert_color_equal(stop2, sut.get_color(4))
        assert_color_equal(stop3, sut.get_color(5))

    def test_can_get_color_beyond_stops(self):
        stop1 = Color(1, 10, 100, 1000)
        stop2 = Color(3, 30, 300, 3000)
        color_stops = [
            (0, stop1),
            (1, stop2)
        ]
        sut = DiscreteColorMap(color_stops)
        assert_color_equal(stop1, sut.get_color(-1))
        assert_color_equal(stop2, sut.get_color(3))


class ContinuousColorMapTestCase(unittest.TestCase):
    def test_can_round_trip(self):
        expected = ContinuousColorMap([
            (0, Color(1, 10, 100, 1000)),
            (5, Color(2, 20, 200, 2000)),
            (10, Color(3, 30, 300, 3000))
        ])
        with NamedTemporaryFile() as f:
            expected.save(f.name)
            actual = ContinuousColorMap.load(f.name)
        np.testing.assert_array_almost_equal(expected.hue, actual.hue)
        np.testing.assert_array_almost_equal(expected.brightness, actual.brightness)
        np.testing.assert_array_almost_equal(expected.saturation, actual.saturation)
        np.testing.assert_array_almost_equal(expected.kelvin, actual.kelvin)

    def test_can_get_colors_at_stops(self):
        color_stops = [
            (0, Color(1, 10, 100, 1000)),
            (5, Color(2, 20, 200, 2000)),
            (10, Color(3, 30, 300, 3000))
        ]
        sut = ContinuousColorMap(color_stops)
        for value, color in color_stops:
            assert_color_equal(color, sut.get_color(value))

    def test_can_get_interpolated_colors_between_stops(self):
        color_stops = [
            (0, Color(1, 10, 100, 1000)),
            (3, Color(2, 20, 200, 2000)),
            (5, Color(3, 30, 300, 3000))
        ]
        sut = ContinuousColorMap(color_stops)
        assert_color_equal(interpolate(color_stops, 0), sut.get_color(0))
        assert_color_equal(interpolate(color_stops, 1), sut.get_color(1))
        assert_color_equal(interpolate(color_stops, 2), sut.get_color(2))
        assert_color_equal(interpolate(color_stops, 3), sut.get_color(3))
        assert_color_equal(interpolate(color_stops, 4), sut.get_color(4))

    def test_can_get_extrapolated_colors(self):
        color_stops = [
            (0, Color(1, 10, 100, 1000)),
            (3, Color(2, 20, 200, 2000)),
            (5, Color(3, 30, 300, 3000))
        ]
        sut = ContinuousColorMap(color_stops)
        assert_color_equal(interpolate(color_stops, -1), sut.get_color(-1))
        assert_color_equal(interpolate(color_stops, 5), sut.get_color(5))

