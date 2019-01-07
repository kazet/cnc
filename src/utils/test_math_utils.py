import math

from unittest import TestCase

from utils.math_utils import euclidean_distance


class EuclideanDistanceTestCase(TestCase):
    def test_zero_distance(self):
        self.assertEqual(
            euclidean_distance(
                (0, 0, 0),
                (0, 0, 0),
            ),
            0
        )

        self.assertEqual(
            euclidean_distance(
                (1, 2, 3),
                (1, 2, 3),
            ),
            0
        )

    def test_single_axis_distance(self):
        self.assertEqual(
            euclidean_distance(
                (0, 0, 0),
                (0, 0, -4),
            ),
            4
        )

        self.assertEqual(
            euclidean_distance(
                (1, 2, 3),
                (1, 2, -2),
            ),
            5
        )

    def test_multiple_axes_distance(self):
        self.assertEqual(
            euclidean_distance(
                (1, 1, 1),
                (2, 2, 2),
            ),
            math.sqrt(3)
        )
