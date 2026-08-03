"""複数候補の試行結果から次に選ぶ候補を決める多腕バンディット。"""

import math

from library_codex.random.RandomGraph import Random

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

