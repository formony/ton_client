# -*- coding: utf-8 -*-

import unittest
from ton_client import ton_clib


class MyTestCase(unittest.TestCase):
    def test_something(self):
        ton_clib.python_hello_world(b'sdfghf')
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
