# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import codecs
import math

import pycseg.definitions as definitions
from pycseg.data_store import DataStore, Feature
from pycseg.segment import Segment
from pycseg.oov_detection import OOVDetection
from pycseg.pos_tagging import POSTagging


class Pycseg(object):
    def __init__(self):
        self.d_store = DataStore()

    def load(self, data_dir):
        return self.d_store.load(data_dir)

    def process_sentence(self, sentence):
        """
        处理句子，返回分词和词性标注结果
        返回格式：[(word, pos), (word, pos) ...(word, pos)]
        """
        #print('=== Segment =====')
        seg = Segment(sentence, d_store=self.d_store)
        seg.atom_segment()
        seg.word_match()

        words_graph = seg.get_words_graph()

        #print('=== OOV Detection =====')
        detection = OOVDetection(words_graph, self.d_store)
        detection.oov_detection()

        words_graph.generate_words_dag(self.d_store.bigram_dct)
        #words_graph.print_words()
        #words_graph.print_words_dag()
        seg_words_result = words_graph.words_segment()
        #print(' '.join([w.content for w in seg_words_result[0]['words']]))

        #print('=== POS Tagging =====')
        pre_poss = 0
        best_words, best_tags = None, None
        for seg_result in seg_words_result:
            words = seg_result['words']
            tagging = POSTagging()
            tags = tagging.generate_pos_tags(words,
                                             self.d_store.core_dct,
                                             self.d_store.lexical_ctx)
            #print(' '.join(['{}/{}'.format(w, p) for w, p in zip(words, tags)]))

            # 对结果进行评分，并记住评分最高的一个
            poss = self.compute_possibility(words, tags, self.d_store)
            if poss > pre_poss:
                pre_poss = poss
                best_words = words
                best_tags = tags

        best_words = map(lambda w: w.content, best_words)
        return {'words': best_words[1:-1], 'tags': best_tags[1:-1]}

    def process(self, content):
        """
        处理文本，返回分词和词性标注结果
        返回格式：[(word, pos), (word, pos) ...(word, pos)]
        """
        sentences = self._split_by(content, definitions.SEPERATOR_C_SENTENCE,
                                   contains_delimiter=True)
        results = {'words': [], 'tags': []}
        for sentence in sentences:
            result = self.process_sentence(sentence)
            results['words'].extend(result['words'])
            results['tags'].extend(result['tags'])
        return results

    def process_file(self, filename, out_filename=None):
        """
        处理文件，结果写入文件或将结果返回
        """
        results = {'words': [], 'tags': []}
        with codecs.open(filename, 'r', 'utf-8') as input_file:
            for line in input_file:
                print('PROCESS LINE:{}'.format(line))
                result = self.process(line.strip())
                print(self.format_result(result))
                results['words'].extend(result['words'])
                results['tags'].extend(result['tags'])

        if out_filename is None:
            return results
        else:
            with codecs.open(out_filename, 'w', 'utf-8') as output_file:
                output_file.write(self.format_result(results))
                output_file.write('\n')

    @staticmethod
    def format_result(result):
        return ' '.join(['{}/{}'.format(w, Feature(tag_code=p).tag) for w, p in zip(result['words'], result['tags'])])

    @staticmethod
    def _split_by(content, delimiters, contains_delimiter=False):
        results = []
        begin_pos, pos = 0, 0
        for c in content:
            if c in delimiters:
                if contains_delimiter:
                    results.append(content[begin_pos:pos+1])
                else:
                    results.append(content[begin_pos:pos])
                begin_pos = pos + 1
            pos += 1
        if begin_pos < pos:
            results.append(content[begin_pos:pos])
        return results

    @staticmethod
    def compute_possibility(words, tags, d_store):
        poss = 0
        for word in words:
            poss += word.weight

        for i in range(len(tags)-1):
            poss = poss + math.log(d_store.lexical_ctx.transition_prob[tags[i]][tags[i+1]]
                                   ) - math.log(d_store.lexical_ctx.start_prob[tags[i]])
        #print('compute_possibility: {}'.format(poss))
        return poss
