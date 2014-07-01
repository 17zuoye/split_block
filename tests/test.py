# -*- coding: utf-8 -*-

import unittest

from split_block import SplitBlockGroup, SplitBlock

class TestSplitBlock(unittest.TestCase):

    def test_maybe_chapped_groups(self):
        print SplitBlockGroup.extract("A. s un  B.no s e C.fa c e  D.ri c e").maybe_chapped_groups()

if __name__ == '__main__': unittest.main()
