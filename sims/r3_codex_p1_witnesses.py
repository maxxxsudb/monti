import random
from fractions import Fraction

random.seed(2026101431)
trials = 1_000_000


def simulate(name, values, messages, heard, target, exact):
    hit = observed = 0
    for _ in range(trials):
        value = random.choice(values)
        message = random.choice(messages[value])
        if message == heard:
            observed += 1
            hit += value == target
    print(f"{name}: trials={trials} observed={observed} exact={exact} "
          f"decimal={float(exact):.8f} empirical={hit / observed:.8f}")


thresholds = {x: list(range(1, x + 1)) for x in range(1, 7)}
simulate("threshold", list(thresholds), thresholds, 3, 6, Fraction(10, 57))

properties = {}
for x in range(1, 9):
    properties[x] = ["odd" if x % 2 else "even"]
    if x % 3 == 0:
        properties[x].append("div3")
    if x >= 5:
        properties[x].append("ge5")
simulate("property", list(properties), properties, "ge5", 8, Fraction(3, 11))

divisors = {x: [d for d in range(1, x + 1) if x % d == 0]
            for x in range(1, 13)}
simulate("divisor", list(divisors), divisors, 2, 12, Fraction(2, 21))
