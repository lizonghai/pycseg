# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import sys
import os
import unittest

from pycseg.data_store import Feature, Dictionary, BiDictionary, Context, DataStore

PYCSEG_DATA_DIR='pycseg'


class DictionaryTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(PYCSEG_DATA_DIR, 'data', 'nr.dct')

    def test_directory_load(self):
        d = Dictionary()
        d.load(self.filename)
        #for k, v in d.iteritems():
        #    print(k)
        #    print(v)
        #matches = d.matches('中华人民共和国成立了')
        #for m in matches:
        #    print(m[0])
        #    print(m[1])

    def test_get_frequence(self):
        d = Dictionary()
        d.load(self.filename)
        d.get_frequence('镇')


class BiDictionaryTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(PYCSEG_DATA_DIR, 'data', 'bigramDict.dct')

    def test_directory_load(self):
        d = BiDictionary()
        d.load(self.filename)
        #for k, v in d.iteritems():
        #    print(k)
        #    print(v)


class ContextTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(PYCSEG_DATA_DIR, 'data', 'lexical.ctx')

    def test_context_load(self):
        cxt = Context()
        cxt.load(self.filename)
        #print(cxt.states)
        #print(cxt.start_prob)
        #print(cxt.transition_prob)


class DataStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(PYCSEG_DATA_DIR, 'data')

    def test_data_store(self):
        d_store = DataStore(self.data_dir)


class POSCodeTestCase(unittest.TestCase):
    def test_pos_encode(self):
        self.assertEqual(Feature('a').tag_code, 24832)
        self.assertEqual(Feature('ad').tag_code, 24932)
        print('{} = {}'.format('ul', Feature('ul').tag_code))

    def test_pos_decode(self):
        self.assertEqual(Feature(tag_code=24832).tag, 'a')
        self.assertEqual(Feature(tag_code=24932).tag, 'ad')
        print('{} = {}'.format(30058, Feature(tag_code=30058).tag))


if __name__ == '__main__':
    unittest.main()
