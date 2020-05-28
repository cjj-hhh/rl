import json
import os
import unittest

import dispatch
import parse


MEAN_CANCEL_RATES = [0.03493870431607338, 0.03866776293519174, 0.041760728528424544, 0.05007157148698522,
                     0.059208628863229744, 0.07455933064560377, 0.08571890195014424, 0.09848048263719175,
                     0.11230701971967454, 0.12717324794320947]
SAMPLE_DIR = os.path.abspath('../samples')


class DispatchTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.alpha = 2 / (5 * 60)
        cls.gamma = 0.9
        cls.idle_reward = -2 / (60 * 60)

        with open(os.path.join(SAMPLE_DIR, 'dispatch_observ'), 'r') as f:
            cls.dispatch_observ = json.load(f)

    def test_sarsa(self):
        drivers, requests, candidates = parse.parse_dispatch(self.dispatch_observ)
        dispatcher = dispatch.Sarsa(self.alpha, self.gamma, self.idle_reward)
        for _ in range(3):
            d = dispatcher.dispatch(drivers, requests, candidates)
            assert d

    def test_dql(self):
        drivers, requests, candidates = parse.parse_dispatch(self.dispatch_observ)
        dispatcher = dispatch.Dql(self.alpha, self.gamma, self.idle_reward)
        for _ in range(3):
            d = dispatcher.dispatch(drivers, requests, candidates)
            assert d

    @staticmethod
    def test_hungarian():
        scored_candidates = [
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_a', order_id='r_1', order_driver_distance=0, pick_up_eta=0)), 0),
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_a', order_id='r_2', order_driver_distance=0, pick_up_eta=0)), 20),
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_b', order_id='r_1', order_driver_distance=0, pick_up_eta=0)), 10),
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_b', order_id='r_2', order_driver_distance=0, pick_up_eta=0)), 25),
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_c', order_id='r_1', order_driver_distance=0, pick_up_eta=0)), 1),
            dispatch.ScoredCandidate(parse.DispatchCandidate(
                dict(driver_id='d_z', order_id='r_99', order_driver_distance=0, pick_up_eta=0)), 1),
        ]
        assignment = dispatch.hungarian(scored_candidates)
        assert assignment and len(assignment) == 3
        assert assignment['r_1'] == 'd_b'  # reward 10
        assert assignment['r_2'] == 'd_a'  # reward 20
        assert assignment['r_99'] == 'd_z'  # reward 1


    @staticmethod
    def test_cancel_rate():
        rate = dispatch.completion_rate(0)
        assert 0.97 < rate < 1.0, rate
        for i in range(10):
            distance = 200 + i * 200
            rate = 1 - dispatch.completion_rate(distance)
            assert abs(rate - MEAN_CANCEL_RATES[i]) < 0.01, rate

        rate = dispatch.completion_rate(5000)
        assert 0 <= rate < 1e-6, rate