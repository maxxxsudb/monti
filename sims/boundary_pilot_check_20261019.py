import json
from fractions import Fraction as F
from pathlib import Path


root = Path(__file__).resolve().parents[1] / "research"
cases = []
for name in ("boundary-pilot-2026-10-19.json", "boundary-pilot-extension-2026-10-19.json"):
    cases.extend(json.loads((root / name).read_text(encoding="utf-8"))["cases"])
results = json.loads((root / "boundary-pilot-results-2026-10-19.json").read_text(encoding="utf-8"))["results"]


def enumerate_event(alpha):
    event = F(0)
    c_and_event = F(0)
    k_and_event = F(0)
    for knows, weight_type in ((True, alpha), (False, 1 - alpha)):
        for prize in "ABC":
            options = [door for door in "BC" if not knows or door != prize]
            for door in options:
                w = weight_type / 3 / len(options)
                if door == "B" and prize != "B":
                    event += w
                    c_and_event += w * (prize == "C")
                    k_and_event += w * knows
    return c_and_event / event, k_and_event / event


k = enumerate_event(F(1))[0]
m = enumerate_event(F(11, 20))[0]
post, posterior_type = enumerate_event(F(22, 49))
assert posterior_type == F(11, 20)
plain = F(11, 20) * F(2, 3) + F(9, 20) * F(1, 2)
gold = {"D-K": k, "L-K": k, "D-M": m, "L-M": m, "MIX-PLAIN": plain, "D-POST": post}
assert len(cases) == len(results) == len(gold) == 6
assert {r["id"] for r in results} == set(gold)
for case in cases:
    assert F(case["gold"]) == gold[case["id"]]
correct = sum(F(r["answer"]) == gold[r["id"]] for r in results)
print(f"Exact gold verified: 6 cases. Observed correct final answers: {correct}/6.")
