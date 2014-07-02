# -*- coding: utf-8 -*-

import unittest

from split_block import SplitBlockGroup, SplitBlock

class TestSplitBlock(unittest.TestCase):

    def test_maybe_chapped_groups(self):
        groups = SplitBlockGroup.extract("A. s un  B.no s e C.fa c e  D.ri c e").maybe_chapped_groups()
        groups = [SplitBlockGroup(g1).concat_items() for g1 in groups]
        self.assertEqual(groups, ['s un  ', 'no s e ', 'fa c e  ', 'ri c e'])


if __name__ == '__main__': unittest.main()
