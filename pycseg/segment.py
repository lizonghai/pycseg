# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, absolute_import

import pycseg.definitions as definitions
from pycseg.data_store import Feature, Atom, Word, WordsGraph, DataStore


class Segment(object):
    """分词"""

    def __init__(self, sentence, d_store=None):
        self.sentence = sentence
        self.d_store = d_store
        self.words_graph = WordsGraph()

    def get_words_graph(self):
        return self.words_graph

    def atom_segment(self):
        """原子切分"""
        prev_type, cur_type = definitions.CT_SENTENCE_BEGIN, 0
        atom = definitions.SENTENCE_BEGIN
        for c in self.sentence:
            cur_type = self.char_type(c)
            if (cur_type == definitions.CT_NUM or
                        cur_type == definitions.CT_LETTER) and (
                            prev_type == definitions.CT_NUM or
                            prev_type == definitions.CT_LETTER):
                atom = ''.join([atom, c])
            else:
                self.words_graph.append_atom(atom, Feature(tag_code=prev_type))
                atom = c
            prev_type = cur_type
        # 最后一个atom
        self.words_graph.append_atom(atom, Feature(tag_code=prev_type))
        # SENTENCE_END
        self.words_graph.append_atom(definitions.SENTENCE_END,
                               Feature(tag_code=definitions.CT_SENTENCE_END))

    def word_match(self):
        """
        找出字典中所有匹配的词
        """
        atoms = self.words_graph.get_atoms()
        # 处理开始标识符
        match = self.d_store.core_dct[definitions.SENTENCE_BEGIN]
        self.words_graph.generate_word(0, 1, Feature(tag_code=match[0][1]),
                                       weight=match[0][0])
        # 处理句子atom
        len_atom = len(atoms)
        for i in range(1, len_atom - 1):
            # print('==match:')
            # print(''.join([atom.content for atom in atoms[i:]]))
            # 找出所有的匹配词
            # matches格式: matches = [(word, [(freq, pos)...]), ...]
            matches = self.d_store.core_dct.matches(
                                    [atom.content for atom in atoms[i:]])
            if matches:
                for match in matches:
                    # print(match[0])
                    pos = 0 if len(match[1]) > 1 else match[1][0][1]
                    # 过滤系统内部标识符, 如: 始##始
                    if 0 < pos < 256:
                        continue
                    # 字构成词的权重，即词频
                    weight = sum([v[0] for v in match[1]])
                    self.words_graph.generate_word(i, i + len(match[0]),
                                                   feature=Feature(tag_code=pos),
                                                   weight=weight
                                                   )
            else:
                # 没有找到任何匹配
                feature = None
                if atoms[i].feature == definitions.CT_NUM:
                    feature = Feature('m')
                    alias = definitions.OOV_WORD_M
                elif atoms[i].feature == definitions.CT_LETTER:
                    feature = Feature('nx')
                    alias = definitions.OOV_WORD_NX
                else:
                    pos, alias = 0, None
                self.words_graph.generate_word(i, i + 1, feature, 0, alias)
                # print('==match end===')

        # 处理结束标识符
        match = self.d_store.core_dct[definitions.SENTENCE_END]
        self.words_graph.generate_word(len_atom - 1, len_atom,
                                       Feature(tag_code=match[0][1]),
                                       weight=match[0][0])

    def char_type(self, c):
        """返回汉字/字符类型"""
        c_type = 0
        c_str = c.encode('utf-8')
        if c_str.isalpha():
            c_type = definitions.CT_LETTER
        elif c_str.isdigit():
            c_type = definitions.CT_NUM
        elif (c in definitions.SEPERATOR_C_SUB_SENTENCE or
                      c in definitions.SEPERATOR_E_SUB_SENTENCE or
                      c in definitions.SEPERATOR_C_SENTENCE or
                      c in definitions.SEPERATOR_E_SENTENCE):
            c_type = definitions.CT_DELIMITER
        else:
            c_type = definitions.CT_CHINESE
        return c_type

    def segment(self):
        self.atom_segment()
        # self.words_dag.atoms_print()
        self.word_match()
        # self.words_dag.atoms_dag_print()
        self.words_graph.generate_words_dag(self.d_store.bigram_dct)
        seg_words_result = self.words_graph.words_segment(3)
        #for seg_words in seg_words_result:
        #    words = seg_words['words']
        #    words_index = seg_words['index']
        #    print(' '.join([word.content for word in words]))
        #    print(words_index)
        return seg_words_result
