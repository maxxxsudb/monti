"""Audit reproducibility and selected blind spots of the submitted suite."""
from contextlib import redirect_stdout
from fractions import Fraction as F
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/inputs/2026-10-21-master-verification/master_verification_suite.py"


def load_module(source):
    namespace = {"__name__": "audited_master", "__file__": str(SOURCE)}
    exec(compile(source, str(SOURCE), "exec"), namespace)
    return namespace


def main():
    source = SOURCE.read_text(encoding="utf-8-sig")
    mutants = {
        1: "band_1_sup = (math.sqrt(17.0) - 3.0) / 8.0",
        4: "band_4_sup = (9.0 - math.sqrt(73.0)) / 6.0",
        5: "band_5_sup = (math.sqrt(13.0) - 3.0) / 6.0",
    }
    for band, assignment in mutants.items():
        assert source.count(assignment) == 1
        changed = source.replace(assignment, assignment.split(" = ")[0] + " = 0.0")
        module = load_module(changed)
        with redirect_stdout(StringIO()):
            module["verify_sections_6_7_8"]()
        print(f"Coverage gap: wrong supremum 0 for band {band} is not rejected")

    changed_cov = source.replace("rhs = cov_yt / (q * (1 - q))", "rhs = F(0)")
    assert changed_cov != source
    caught = False
    with redirect_stdout(StringIO()):
        try:
            load_module(changed_cov)["verify_section_1_protocol_loss"]()
        except AssertionError:
            caught = True
    assert caught
    print("Positive control: wrong covariance identity is rejected")

    module = load_module(source)
    profiles = {
        "N": (1, 1, 1), "L": (1, 0, 1), "W": (0, 1, 1),
        "E": (0, 0, 0), "LW": (0, 0, 1),
    }
    assert len(set(profiles.values())) == 5
    print("Combined-intervention menu: IZ,IR,IZ+IR separates all five profiles")
    p0, p1, rho = F(1, 10), F(1, 5), F(1, 10)
    assert abs(p1 - p0) == rho
    assert p1 > p0 + rho * (p1 - p0)
    print("Absolute TV counterexample remains valid: permitted success 1/5 > claimed 11/100")
    derivative = 2 / (1 + F(1, 4)) ** 2 + F(4, 5)
    assert derivative == F(52, 25) > 2
    print("The mimicry function still has Lipschitz constant 52/25, exceeding 2")
    assert 3**4 * 3**4 * 2 == 13122
    print("13122 = two priors times 81 by 81 strictly positive weight vectors")
    print("PASS: audit findings reproduced; original source is unchanged")


if __name__ == "__main__":
    main()
