"""Independent exact checks of the two hard-task solution documents."""
from fractions import Fraction as F
from functools import lru_cache
from math import gcd, log2
from functools import reduce


def solve(channels, cost, horizon, initial=(1, 1, 1, 1)):
    @lru_cache(None)
    def dp(weights, t):
        total = sum(weights)
        best = (F(total - max(weights), total), "stop")
        if not t:
            return best
        for name, rows in channels.items():
            den = sum(rows[0])
            value = cost
            for col in zip(*rows):
                nxt = tuple(w * p for w, p in zip(weights, col))
                mass = sum(nxt)
                if not mass:
                    continue
                divisor = reduce(gcd, nxt)
                normalized = tuple(x // divisor for x in nxt)
                value += F(mass, total * den) * dp(normalized, t - 1)[0]
            if value < best[0]:
                best = value, name
        return best
    return [dp(initial, t) for t in range(1, horizon + 1)]


def channel(labels):
    m = max(labels) + 1
    return tuple(tuple(9 * (m - 1) if j == label else 1
                       for j in range(m)) for label in labels)


def main():
    channels = {"Q2quarter": channel((0, 1, 2, 3)),
                "Q2half": channel((0, 1, 1, 0)),
                "Q1": channel((0, 1, 0, 2))}
    expected = {
        F(1, 10): [F(1, 5)] * 5,
        F(1, 20): [F(3, 20), F(3, 20), F(197, 1500),
                    F(5483, 45000), F(27307, 225000)],
        F(0): [F(1, 10), F(1, 10), F(11, 500),
               F(29, 2500), F(203, 50000)],
    }
    for cost, claimed in expected.items():
        results = solve(channels, cost, 5)
        values = [v for v, _ in results]
        print("cost", cost, "values", list(map(str, values)),
              "matches supplied table", values == claimed, flush=True)
        assert values == claimed
    pair = {k: v for k, v in channels.items() if k != "Q2quarter"}
    print("pair only", solve(pair, F(1, 10), 5), flush=True)

    router = {"router": ((19, 1), (19, 1), (1, 19), (1, 19)),
              "specialist1": ((1, 0), (0, 1), (0, 1), (0, 1)),
              "specialist3": ((0, 1), (0, 1), (1, 0), (0, 1))}
    result = solve(router, F(0), 2, (13, 12, 13, 12))
    assert result == [(F(12, 25), "specialist1"), (F(1, 20), "router")]
    # Fix the first test; the second is still optimally chosen.
    first_specialist = F(37, 50) * solve(
        router, F(0), 1, (0, 12, 13, 12))[0][0]
    assert first_specialist == F(6, 25)
    print("router counterexample", result, "specialist start", first_specialist)

    # Three-state one-step gains: same maximum posterior, different decisions.
    ternary = {str(i): tuple((9, 1) if h == i else (1, 9)
                            for h in range(3)) for i in range(3)}
    for weights in [(2, 2, 0), (2, 1, 1), (0, 2, 2), (1, 1, 1)]:
        print("three-state", weights, solve(ternary, F(3, 10), 3, weights))

    # The claimed entropy lower bound would require 0 >= 3/4 bits.
    claimed_lower = 1 - F(1, 4) * log2(2)
    assert claimed_lower > 0
    print("entropy lower bound counterexample: true=0, claimed >=", claimed_lower)
    # M4 inverse = (15/13) I - (1/26) J.
    column = (F(9, 10), F(1, 20), F(9, 10), F(1, 20))
    garbling = tuple(F(15, 13) * x - sum(column) / 26 for x in column)
    assert min(garbling) == -F(1, 65)
    print("Q1 garbling column", garbling)

    binary = {"repeat": ((9, 1), (1, 9))}
    one = solve(binary, F(1, 1000), 1, (9, 1))[0]
    two = solve(binary, F(1, 1000), 2, (9, 1))[-1]
    assert one == (F(1, 10), "stop")
    assert two[0] == F(1459, 50000) and two[1] == "repeat"
    print("myopic stop but two steps help", one, two)
    print("checks completed")


if __name__ == "__main__":
    main()
