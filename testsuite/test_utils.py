# -*- coding: utf-8 -*-

import unittest
from ton_client import utils as tc_utils


class UtilsTestCase(unittest.TestCase):
    def test_raw_to_userfriendly(self):
        raw = '-1:8156775b79325e5d62e742d9b96c30b6515a5cd2f1f64c5da4b193c03f070e0d'
        uf = 'Ef-BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb'

        uf_test = tc_utils.raw_to_userfriendly(raw)
        self.assertEqual(uf, uf_test)

    def test_userfriendly_to_raw(self):
        raw = '-1:8156775b79325e5d62e742d9b96c30b6515a5cd2f1f64c5da4b193c03f070e0d'.upper()
        uf = 'Ef-BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb'

        raw_test = tc_utils.userfriendly_to_raw(uf)
        self.assertEqual(raw, raw_test)


if __name__ == '__main__':
    unittest.main()
