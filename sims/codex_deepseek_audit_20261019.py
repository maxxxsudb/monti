import math
from fractions import Fraction as F
from itertools import product

import r52_adaptive_voi as source


def entropy(probabilities):
    return -sum(float(p) * math.log2(float(p)) for p in probabilities if p)


def conditional_entropy(likelihood, observations, eps):
    answer = 0.0
    for observation in observations:
        masses = [likelihood(h, observation, eps) / 4 for h in source.HYPS]
        total = sum(masses)
        if total:
            answer += float(total) * entropy([p / total for p in masses])
    return answer


alphabet = list(source.KEYS.values())
eps = F(1, 10)
one = conditional_entropy(source.lik1, alphabet, eps)
two = conditional_entropy(source.lik2, list(product(alphabet, repeat=2)), eps)
risk_one = source.bayes_risk(source.lik1, alphabet, eps)
risk_two = source.bayes_risk(source.lik2, list(product(alphabet, repeat=2)), eps)
assert risk_one == risk_two == eps
assert one > two
information_a = entropy([F(1, 3), F(2, 3)])
assert 0.91829 < information_a < 0.91830
assert entropy([F(1), F(0)]) == 0
adaptive_cost_and_risk = F(1, 100) + F(2, 3) * F(1, 10) + F(2, 15)
b_only_cost_and_risk = F(1, 10) + F(2, 15)
assert adaptive_cost_and_risk == F(21, 100)
assert b_only_cost_and_risk - adaptive_cost_and_risk == F(7, 300)
print(f"PASS: IG(A)={information_a:.9f} bits, not 1")
print(f"PASS: R1=R2={risk_one}; H1={one:.9f}; H2={two:.9f}; added information={one-two:.9f} bits")
print("PASS: A then conditional B costs 21/100 including risk, versus 7/30 for B alone")
