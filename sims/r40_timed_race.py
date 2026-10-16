"""P40: гонка взрывов с учётом времени первого взрыва (тихий амулет) против светящегося амулета.

Бомбы с одинаковыми независимыми непрерывными часами (закон любой; здесь Exp(1) и Weibull для проверки).
Решение сразу после первого взрыва. Клетка 0 — волшебник, априоры (p0, p, ..., p), p0 >= p.
Формула: W_timed = p0(1-rho^(N-1)) + (N-1)/(N-2) p rho^(N-2), rho = p/p0;
светящийся амулет (своя бомба участвует в гонке, вспышка видна): p0 + p/(N-1);
без учёта времени (тихий): max(p0, p(N-1)/(N-2)).
"""
import math
from fractions import Fraction as F


def timed_numeric(N, p0, surv, dens, T=60.0, steps=200000):
    p = (1 - p0) / (N - 1)
    h = T / steps
    tot = 0.0
    for i in range(steps):
        t = (i + 0.5) * h
        S, f = surv(t), dens(t)
        # первый взорвался соперник d (N-1 вариантов); свой пуст: p0 f S^(N-2); пуст другой соперник: p f S^(N-3)
        tot += (N - 1) * max(p0 * f * S ** (N - 2), p * f * S ** (N - 3)) * h
    return tot


def timed_formula(N, p0):
    p = (1 - p0) / (N - 1)
    rho = p / p0
    return p0 * (1 - rho ** (N - 1)) + (N - 1) / (N - 2) * p * rho ** (N - 2)


if __name__ == "__main__":
    laws = {"exp": (lambda t: math.exp(-t), lambda t: math.exp(-t)),
            "weibull2": (lambda t: math.exp(-t * t), lambda t: 2 * t * math.exp(-t * t))}
    for N in (3, 4, 5):
        for p0 in (1 / N, 0.4, 0.5, 0.7):
            if p0 < (1 - p0) / (N - 1):
                continue
            for name, (S, f) in laws.items():
                assert abs(timed_numeric(N, p0, S, f, T=12.0, steps=60000) - timed_formula(N, p0)) < 1e-4, (N, p0, name)
    # Порог «тихий с временем» против «светящегося»: rho* = ((N-2)/(N-1))^(1/(N-2)); N=3: r*=2.
    for N in (3, 4, 5, 8):
        rho_star = ((N - 2) / (N - 1)) ** (1 / (N - 2))
        for rho in (rho_star * 0.97, rho_star * 1.03):
            if rho > 1:
                continue
            p0 = 1 / (1 + (N - 1) * rho)
            p = rho * p0
            glow = p0 + p / (N - 1)
            assert (timed_formula(N, p0) > glow) == (rho > rho_star)
    # N=3, равные априоры: 2/3 в обоих режимах гонки; (1/2,1/4,1/4) — ровно ничья с светящимся.
    assert abs(timed_formula(3, 1 / 3) - 2 / 3) < 1e-12 and abs(timed_formula(3, 0.5) - 0.625) < 1e-12
    print("P40: формула гонки с временем подтверждена квадратурой (Exp, Weibull); порог rho* подтверждён.")
    print("ALL OK")
