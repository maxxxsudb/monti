"""r65: minimal relational-composition model.

Checks the countermodel for the invalid inference
produce(x,y) & drink(z,y) => drink(x,y), and prints the predicted profiles
for correct / association / role-misbinding / ignorance.
"""
import sys

sys.dont_write_bytecode = True

ENTITIES = ("cow", "human", "milk", "water", "yak", "cat")


def main():
    print("=== r65 relational-composition model ===")
    # countermodel: premises true, conclusion false
    produce = {("cow", "milk")}
    drink = {("human", "milk"), ("cow", "water")}
    x, y, z = "cow", "milk", "human"
    assert (x, y) in produce
    assert (z, y) in drink
    assert (x, y) not in drink
    print("countermodel: produce(cow,milk)=T, drink(human,milk)=T, drink(cow,milk)=F")
    print("invalid inference refuted")

    # predicted profiles: Q1..Q6
    correct = ["water", "human", "milk", "water", "water", "human"]
    assoc = ["milk", "human", "milk", "water/unknown", "milk", "human"]
    role = ["milk", "cow", "milk", "milk", "milk", "cow"]
    ignorance = ["?", "?", "?", "?", "?", "?"]
    rows = [("correct", correct), ("association", assoc),
            ("role-misbinding", role), ("ignorance", ignorance)]
    print("\nProfiles (Q1..Q6):")
    for name, prof in rows:
        print(f"  {name:>16}: {prof}")

    # minimal pair Q1 vs Q4 distinguishes association from role-misbinding
    assert assoc[0] == "milk" and assoc[3] in ("water/unknown", "water")
    assert role[0] == "milk" and role[3] == "milk"
    print("\nQ1/Q4: association is familiar-pair-specific; role-misbinding transfers to yak")
    # Q2/Q6: agent question distinguishes association (human) from role (cow)
    assert assoc[1] == "human" and role[1] == "cow"
    assert assoc[5] == "human" and role[5] == "cow"
    print("Q2/Q6: agent question distinguishes association (human) from role (cow)")
    print("All checks passed")


if __name__ == "__main__":
    main()
