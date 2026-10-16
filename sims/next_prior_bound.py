from fractions import Fraction as Q
from itertools import product


def direct(priors, q, protected):
    result = Q(0)
    checked = range(1, len(priors)) if protected else range(len(priors))
    checked = tuple(checked)
    for bits in product((0, 1), repeat=len(checked)):
        masses = []
        for target, prior in enumerate(priors):
            weight = prior
            for door, opened in zip(checked, bits):
                probability = Q(0) if door == target else q
                weight *= probability if opened else 1 - probability
            masses.append(weight)
        result += max(masses)
    return result


def ordered(priors, q):
    p, s = priors[0], 1 - q
    return sum((q**j * max(Q(0), min(q * w, s * (p - w)))
                for j, w in enumerate(sorted(priors[1:], reverse=True))), Q(0))


count = 0
for n in range(2, 5):
    for raw in product((1, 2, 5), repeat=n):
        priors = tuple(Q(x, sum(raw)) for x in raw)
        for q in (Q(1, 4), Q(1, 2), Q(4, 5)):
            gap = direct(priors, q, False) - direct(priors, q, True)
            assert gap == ordered(priors, q)
            bound = max(q * (1 - q**k) / (1 + k * (1 - q))
                        for k in range(1, n))
            assert gap <= bound
            p = priors[0]
            clipped = (p, *(min(w, (1 - q) * p) for w in priors[1:]))
            total = sum(clipped)
            normalized = tuple(x / total for x in clipped)
            assert ordered(normalized, q) >= gap
            count += 1

sharp = 0
for m in range(1, 7):
    for k in range(1, m + 1):
        for q in (Q(1, 4), Q(1, 2), Q(4, 5)):
            p = 1 / (1 + k * (1 - q))
            priors = (p, *((1 - q) * p for _ in range(k)), *(Q(0) for _ in range(m - k)))
            assert ordered(priors, q) == q * (1 - q**k) / (1 + k * (1 - q))
            sharp += 1

print(f"PASS: {count} exact prior/channel cases; {sharp} extremal configurations")
