import math
import time

from library_codex.random.RandomGraph import Random


class LogTable:
    __slots__ = ("values", "mask")

    def __init__(self, bits=16, seed=88172645463325252):
        size = 1 << bits
        self.mask = size - 1
        values = [0.0] * size
        value = seed & ((1 << 64) - 1)
        log_max = math.log(2.0) * 64
        for index in range(size):
            value ^= value << 7 & ((1 << 64) - 1)
            value ^= value >> 9
            values[index] = math.log(max(1, value)) - log_max
        self.values = values

    def __call__(self, index):
        return self.values[index & self.mask]


class MultiArmedBandit:
    __slots__ = ("n", "last", "iteration", "threshold", "counts", "rewards",
                 "weights", "temperature", "random", "cooling")

    def __init__(self, arm_count, seed=1):
        if arm_count <= 0:
            raise ValueError("arm_count must be positive")
        self.n = arm_count
        self.last = -1
        self.iteration = 0
        self.threshold = arm_count * 5
        self.counts = [0] * arm_count
        self.rewards = [0.0] * arm_count
        self.weights = [1.0] * arm_count
        self.temperature = 1.0
        self.random = Random(seed)
        self.cooling = 1.0

    def play(self):
        if self.last != -1:
            raise RuntimeError("reward must be reported before the next play")
        self.iteration += 1
        if self.iteration <= self.threshold:
            self.last = (self.iteration - 1) % self.n
            return self.last
        total = sum(self.weights)
        point = self.random.uniform01() * total
        for arm, weight in enumerate(self.weights):
            point -= weight
            if point <= 0:
                self.last = arm
                return arm
        self.last = self.n - 1
        return self.last

    def reward(self, value):
        if self.last < 0:
            raise RuntimeError("play must be called before reward")
        arm = self.last
        self.rewards[arm] += value
        self.counts[arm] += 1
        average = self.rewards[arm] / self.counts[arm]
        self.weights[arm] = math.exp(max(-700.0, min(700.0,
                                                     average / self.temperature)))
        self.last = -1
        if self.iteration % self.threshold == 0:
            self.cooling = max(0.7, self.cooling - 0.01)
            average_reward = sum(self.rewards) / self.threshold
            self.temperature = 1.0 if average_reward < 0 else max(
                1e-300, average_reward ** self.cooling
            )
            for index in range(self.n):
                average = self.rewards[index] / max(1, self.counts[index])
                self.weights[index] = math.exp(max(
                    -700.0, min(700.0, average / self.temperature)
                ))

    def best(self):
        return max(range(self.n), key=self.weights.__getitem__)


class TopK:
    __slots__ = ("k", "hash_function", "values")

    def __init__(self, count, hash_function=hash):
        if count < 0:
            raise ValueError("count must be nonnegative")
        self.k = count
        self.hash_function = hash_function
        self.values = {}

    def insert(self, value):
        key = self.hash_function(value)
        old = self.values.get(key)
        if old is None or value < old:
            self.values[key] = value
        if len(self.values) >= max(1, self.k << 1):
            self.normalize()

    def normalize(self):
        if len(self.values) > self.k:
            selected = sorted(self.values.items(), key=lambda item: item[1])[:self.k]
            self.values = dict(selected)

    def get(self):
        self.normalize()
        return sorted(self.values.values())


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


log_table = LogTable
Top_K = TopK
SA_manager = SAManager
Simulated_Annealing = SimulatedAnnealing
