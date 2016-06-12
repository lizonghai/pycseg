# -*- coding: utf-8 -*-


import unittest

from pycseg.utils import hmm


class HMMTestCase(unittest.TestCase):
    def setUp(self):
        self.states = ('Healthy', 'Fever')
        self.observations = ('normal', 'cold', 'dizzy')
        self.start_probability = {'Healthy': 0.6, 'Fever': 0.4}
        self.transition_probability = {
            'Healthy': {'Healthy': 0.7, 'Fever': 0.3},
            'Fever': {'Healthy': 0.4, 'Fever': 0.6}
        }
        self.emission_probability = {
            'Healthy': {'normal': 0.5, 'cold': 0.4, 'dizzy': 0.1},
            'Fever': {'normal': 0.1, 'cold': 0.3, 'dizzy': 0.6}
        }

    def test_viterbi(self):
        prob, path = hmm.viterbi(self.observations,
                                 self.states,
                                 self.start_probability,
                                 self.transition_probability,
                                 self.emission_probability)
        self.assertEqual(prob, 0.01512)
        self.assertListEqual(path, ['Healthy', 'Healthy', 'Fever'])


if __name__ == '__main__':
    unittest.main()
