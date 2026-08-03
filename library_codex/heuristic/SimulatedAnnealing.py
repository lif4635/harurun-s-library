"""焼きなまし法の温度・受理判定・進行状況を管理する。"""

import math

import time

from library_codex.random.RandomGraph import Random

class SimulatedAnnealing:
    """Time-bounded maximizing SA driven by propose(state)->(delta, commit)."""

    __slots__ = ("duration", "start_temperature", "end_temperature", "random")

    def __init__(self, duration, start_temperature, end_temperature, seed=1):
        if duration < 0 or start_temperature < end_temperature:
            raise ValueError("invalid annealing schedule")
        self.duration = duration
        self.start_temperature = start_temperature
        self.end_temperature = end_temperature
        self.random = Random(seed)

    def run(self, state, propose, max_iterations=None):
        start = time.perf_counter()
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            elapsed = time.perf_counter() - start
            if elapsed >= self.duration:
                break
            ratio = elapsed / self.duration if self.duration else 1.0
            temperature = (self.start_temperature
                           + (self.end_temperature - self.start_temperature) * ratio)
            delta, commit = propose(state)
            accepted = delta >= 0
            if not accepted and temperature > 0:
                accepted = math.log(max(self.random.uniform01(), 1e-300)) < (
                    delta / temperature
                )
            if accepted:
                commit()
            iteration += 1
        return state

class SAManager:
    """Multipoint SA that gradually retains only the highest-scoring states."""

    __slots__ = ("duration", "start_temperature", "end_temperature", "state_max",
                 "random", "iterations")

    def __init__(self, duration, start_temperature, end_temperature,
                 state_max=1, seed=1):
        if state_max <= 0 or start_temperature < end_temperature:
            raise ValueError("invalid SA manager parameters")
        self.duration = duration
        self.start_temperature = start_temperature
        self.end_temperature = end_temperature
        self.state_max = state_max
        self.random = Random(seed)
        self.iterations = 0

    def run(self, initialize, update, max_iterations=None):
        states = [initialize() for _ in range(self.state_max)]
        start = time.perf_counter()
        loops = 0
        while max_iterations is None or loops < max_iterations:
            elapsed = time.perf_counter() - start
            if elapsed >= self.duration:
                break
            ratio = elapsed / self.duration if self.duration else 1.0
            temperature = (self.start_temperature
                           + (self.end_temperature - self.start_temperature) * ratio)
            for index, (state, score) in enumerate(states):
                threshold = temperature * math.log(
                    max(self.random.uniform01(), 1e-300)
                )
                states[index] = update(state, score, threshold)
                self.iterations += 1
            wanted = max(1, round(self.state_max * max(0.0, 1.0 - ratio)))
            if wanted < len(states):
                states.sort(key=lambda pair: pair[1], reverse=True)
                del states[wanted:]
            loops += 1
        return max(states, key=lambda pair: pair[1])

