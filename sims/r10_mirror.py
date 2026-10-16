"""Round 10: search for a nontrivial mirror of R02.

Wanted: an iid test (P11 setting) whose last application helps under forced
choice but is worthless when walking away (+1/-2/0) is allowed, while playing
is sometimes profitable (abstain value > 0). Grid over 3-outcome tests.
"""
import sys
from fractions import Fraction as F
from itertools import product

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from r10_envelope import bayes_value, forced, abstain  # noqa: E402

D = int(sys.argv[1]) if len(sys.argv) > 1 else 6
laws = [[F(a, D), F(b, D), F(D - a - b, D)]
        for a in range(D + 1) for b in range(D + 1 - a)]
hits = []
for n in (3, 4):
    for g1, g0 in product(laws, laws):
        if any(x == 0 for x in g0) or g1 == g0:
            continue
        fl = bayes_value(n, n, g1, g0, forced) - bayes_value(n, n - 1, g1, g0, forced)
        if fl <= 0:
            continue
        ab_prev = bayes_value(n, n - 1, g1, g0, abstain)
        ab_full = bayes_value(n, n, g1, g0, abstain)
        if ab_full == ab_prev and ab_full > 0:
            hits.append((n, g1, g0, fl, ab_full))
for n, g1, g0, fl, ab in hits[:15]:
    print(f"n={n} g1={[str(x) for x in g1]} g0={[str(x) for x in g0]} forced gain={fl} abstain value={ab} (gain 0)")
print(f"{len(hits)} nontrivial mirrors on grid D={D}")
