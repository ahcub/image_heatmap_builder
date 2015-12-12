from os import getcwd
from os.path import join
from unittest import TestCase

from armory.os_utils.path import delete

from src.heatmap_utils import read_coordinates


class TestUtils(TestCase):
    def test_read_coordinates(self):
        test_file_path = join(getcwd(), 'test.csv')
        try:
            expected_array = [(1, 2), (3, 4)]
            with open(test_file_path, 'w') as test_file:
                for row in expected_array:
                    test_file.write(','.join([str(el) for el in row]) + '\n')

            self.assertEquals(expected_array, read_coordinates(test_file_path))
        finally:
            delete(test_file_path)
