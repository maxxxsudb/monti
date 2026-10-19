"""Counterexamples to latent-state and correction-rate claims."""

from fractions import Fraction as F


tables = (
    {("B", "B"): 30, ("B", "C"): 15, ("C", "B"): 0, ("C", "C"): 55},
    {("B", "B"): 15, ("B", "C"): 30, ("C", "B"): 15, ("C", "C"): 40},
)
for table, repair in zip(tables, (F(1, 3), F(2, 3))):
    assert sum(table.values()) == 100
    first_b = sum(n for (first, _), n in table.items() if first == "B")
    final_b = sum(n for (_, final), n in table.items() if final == "B")
    d = F(first_b, 100)
    s = F(table["B", "B"], first_b)
    u = F(table["C", "B"], 100 - first_b)
    assert (d, F(final_b, 100)) == (F(9, 20), F(3, 10))
    assert F(final_b, 100) == d * s + (1 - d) * u
    assert F(table["B", "C"], first_b) == repair

# Different representations can all preserve the correct answer.
same_representation = F(0)
check_probability = F(0)
claimed_accuracy = same_representation + (1 - same_representation) * check_probability
actual_accuracy = sum((F(1, 3), F(2, 3)))
assert claimed_accuracy == 0 and actual_accuracy == 1

# Removing the conditioning from the last factor counts defect prevalence twice.
defect = F(1, 2)
wrong_given_defect = F(1)
wrong_unconditional = defect * wrong_given_defect
assert defect * wrong_unconditional == F(1, 4)
assert wrong_unconditional == F(1, 2)

parameter_sets = ((F(2, 5), F(0), F(1)), (F(4, 5), F(1, 2), F(1)))
for d, alpha, beta in parameter_sets:
    assert d * (1 - alpha * beta) == F(2, 5)
assert F(1, 2) * F(1) == F(1) * F(1, 2)

print("PASS: transition margins do not identify correction; "
      "representation mismatch does not imply error; "
      "unconditional factor double-counts; latent parameters are non-identifiable")
