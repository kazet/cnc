from unittest import TestCase

from utils.random import random_token


class RandomTokenGeneratorTestCase(TestCase):
    def test_length(self):
        self.assertEqual(len(random_token(2)), 2)
        self.assertEqual(len(random_token(143)), 143)
