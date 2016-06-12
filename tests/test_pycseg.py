# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import os
import sys
import unittest

import pycseg


class PycsegTestCase(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(sys.path[0], '../data')
        self.sentence = '张华平在北京说的确实在理。'
        self.content = '奥斯特洛夫斯基来到了北京天安门。张华平说的确实在理。'
        self.test_file = 'in.txt'

    def _test_process_sentence(self):
        seg = pycseg.Pycseg()
        seg.load(self.data_dir)
        result = seg.process_sentence(self.sentence)
        print(seg.format_result(result))

    def test_process(self):
        seg = pycseg.Pycseg()
        seg.load(self.data_dir)
        result = seg.process(self.content)
        print(seg.format_result(result))

    def _test_process_file(self):
        seg = pycseg.Pycseg()
        seg.load(self.data_dir)
        seg.process_file(self.test_file, 'out.txt')
        results = seg.process_file(self.test_file)
        for result in results:
            print(seg.format_result(result))

    def _test_split(self):
        results = pycseg.Pycseg._split_by(
            content='123,456，789.ad。efg,,,',
            delimiters=',，。',
            contains_delimiter=True
        )
        print(results)


if __name__ == '__main__':
    unittest.main()
