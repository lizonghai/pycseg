# -*- coding: utf-8 -*-
"""Implementation of hidden Markov model."""


def viterbi(obs, states, start_p, trans_p, emit_p, default_prob=0):
    """
    Return the best path, given an HMM model and a sequence of observations
    The complexity of this algorithm is O(T * squr(|S|))

    https://en.wikipedia.org/wiki/Viterbi_algorithm
    https://github.com/llrs/Viterbi

    :param obs:观测序列
    :param states:隐状态
    :param start_p:初始概率（隐状态）
    :param trans_p:转移概率（隐状态）
    :param emit_p: 发射概率 （隐状态表现为显状态的概率）
    :return:
    """
    # 路径概率表 V[时间][隐状态] = 概率
    V = [{}]
    # 一个中间变量，代表当前状态是哪个隐状态
    path = {}

    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = start_p[y] * emit_p[y][obs[0]]
        # V[0][y] = start_p[y] * emit_p.get(y, {}).get(obs[0], default_prob)
        path[y] = [y]

    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}

        for y in states:
            # (概率 隐状态) =  前状态是y0的概率 * y0转移到y的概率 * y表现为当前状态的概率
            # (V[t - 1][y0] * trans_p[y0][y] * emit_p.get(y, {}).get(obs[t], default_prob), y0)
            (prob, state) = max(
                (V[t - 1][y0] * trans_p[y0][y] * emit_p[y][obs[t]], y0)
                for y0 in states)
            # 记录最大概率
            V[t][y] = prob
            # 记录路径
            newpath[y] = path[state] + [y]

        # Don't need to remember the old paths
        path = newpath

    # __viterbi_print_dptable(V)
    # Return the most likely sequence over the given time frame
    n = len(obs) - 1
    (prob, state) = max((V[n][y], y) for y in states)
    return prob, path[state]


def __viterbi_print_dptable(V):
    """ Helps visualize the steps of Viterbi."""
    s = "    " + " ".join(("%10d" % i) for i in range(len(V))) + "\n"
    for y in V[0]:
        s += "%.5s: " % y
        s += " ".join("%.10s" % ("%.2e" % v[y]) for v in V)
        s += "\n"
    print(s)


class HMM(object):
    """Implementation of hidden Markov model."""
    def __init__(self, states=None, observations=None,
                 start_prob=None, transition_prob=None, emission_prob=None):
        """
        :param observations:观测序列
        :param states:隐状态
        :param start_prob:初始概率（隐状态）
        :param transition_prob:转移概率（隐状态）
        :param emission_prob: 发射概率 （隐状态表现为显状态的概率）
        """
        self.states = states if states else []
        self.observations = observations if observations else []
        self.start_prob = start_prob if start_prob else {}
        self.transition_prob = transition_prob if transition_prob else {}
        self.emission_prob = emission_prob if emission_prob else {}

    def add_state(self, state):
        self.states.append(state)

    def add_observations(self, obs):
        self.observations.append(obs)

    def add_start_prob(self, state, prob):
        self.start_prob[state] = prob

    def add_transition_prob(self, state_i, state_j, prob):
        tran_x = self.transition_prob.setdefault(state_i, {})
        tran_x[state_j] = prob

    def add_emission_prob(self, state, obs, prob):
        emit_state = self.emission_prob.setdefault(state, {})
        emit_state[obs] = prob
