# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, absolute_import
import math

import pycseg.definitions as definitions
from pycseg.utils import hmm
from pycseg.data_store import Feature, WordsGraph


class POSTagging(object):
    """词性标注"""

    def __init__(self, words_graph=None, d_store=None):
        self.words_graph = words_graph
        self.d_store = d_store

    def pos_tagging(self):
        self.words_graph.generate_words_dag()
        seg_words_result = self.words_graph.words_segment()
        for seg_words in seg_words_result:
            words = seg_words['words']
            index = seg_words['index']
            pos_tags = self.generate_pos_tags(words, self.d_store.core_dct,
                                              self.d_store.lexical_ctx)

    def generate_pos_tags(self, words, dictionary=None, lexical=None):
        """词性标注"""
        hmm_model = self.generate_hmm_model(words, dictionary, lexical)

        prob, tags = hmm.viterbi(hmm_model.observations, hmm_model.states,
                                 hmm_model.start_prob,
                                 hmm_model.transition_prob,
                                 hmm_model.emission_prob)

        # 打印结果
        #print(' '.join(['{}/{}'.format(word.content, Feature(tag_code=tag).tag
        #                               ) for word, tag in zip(words, tags)]))
        return tags

    @staticmethod
    def generate_hmm_model(words, dictionary, lexical):
        """生成HMM模型中的观察序列 和 发射概率"""
        smoothing_param = 0.1
        hmm_model = hmm.HMM(states=lexical.states,
                          start_prob=lexical.start_prob,
                          transition_prob=lexical.transition_prob)
        for word in words:
            # 观察序列
            hmm_model.add_observations(word.alias)
            # 发射概率
            # 发射概率平滑
            for pos in lexical.states:
                hmm_model.add_emission_prob(pos, word.alias,
                                          smoothing_param * 1 / lexical.total_freq)
            # 发射概率计算
            word_attr = dictionary.get(word.alias, [])
            for freq, pos in word_attr:
                pos = word.feature.tag_code if pos == 2 else pos
                state_freq = max(lexical.state_freq.get(pos, 0), 1)
                hmm_model.add_emission_prob(pos, word.alias,
                                          (1 - smoothing_param) * (
                                          freq + 0.1) / state_freq + smoothing_param * 1 / lexical.total_freq)
        #POSTagging.print_hmm_model(hmm_model)
        return hmm_model

    @staticmethod
    def print_hmm_model(hmm_model):
        print('状态序列 - 词性列表:')
        print(hmm_model.states)
        print('观察序列 - 词:')
        print(' '.join(hmm_model.observations))
        print('发射概率 - 词在特定词性下的词频/此词性总数')
        for k, v in hmm_model.emission_prob.items():
            print('{}-{}:{}'.format(Feature(tag_code=k).tag, k, ','.join(
                ['{}={:e}'.format(word, prob) for word, prob in v.items()])))
