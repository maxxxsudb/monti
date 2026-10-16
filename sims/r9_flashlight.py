"""R03 в форме фонариков: точный перебор протокола (независимо от таблицы P3).

Три фонарика: W (всё исправно), P (села батарейка, лампа цела),
C (перегорела лампа, батарейка цела). Шесть размещений равновероятны.
Ваш фонарик A не проверяют. Мастер из двух других отбраковывает неисправный;
если неисправны оба, бракует C с вероятностью r. Вы ставите в A
батарейку из оставленного или из отбракованного фонарика.
"""
from fractions import Fraction as F
from itertools import permutations

GOOD_BULB = {"W": 1, "P": 1, "C": 0}
GOOD_BATT = {"W": 1, "P": 0, "C": 1}


def run(r):
    keep_batt = rej_batt = keep_light = rej_light = F(0)
    for a, x, y in permutations("WPC"):
        if x > y:  # пара {x, y} без порядка; итого 3 равновероятных типа A
            continue
        if "W" in (x, y):
            cases = [(x if y == "W" else y, "W", F(1))]
        else:  # оба неисправны
            cases = [("C", "P", r), ("P", "C", 1 - r)]
        for rej, keep, w in cases:
            w *= F(1, 3)
            keep_batt += w * GOOD_BATT[keep]
            rej_batt += w * GOOD_BATT[rej]
            keep_light += w * GOOD_BULB[a] * GOOD_BATT[keep]
            rej_light += w * GOOD_BULB[a] * GOOD_BATT[rej]
    return keep_batt, rej_batt, keep_light, rej_light


if __name__ == "__main__":
    for r in (F(1, 2), F(3, 4), F(1)):
        kb, rb, kl, rl = run(r)
        assert (kb, rb, kl, rl) == (1 - r / 3, (1 + r) / 3, (2 - r) / 3, (1 + r) / 3)
        print(f"r={r}: батарейка исправна: оставленный {kb}, брак {rb}; "
              f"ваш фонарик светит: с батарейкой оставленного {kl}, брака {rl}")
    # Лемма границы: Success_X = E[лампа A]*Q_X + Cov(лампа A, батарейка X); E[лампа A] = 2/3.
    for r in (F(1, 4), F(1, 2), F(3, 4), F(1)):
        kb, rb, kl, rl = run(r)
        assert kl - F(2, 3) * kb == -r / 9 and rl - F(2, 3) * rb == (1 + r) / 9
    # Рычаг правдоподобия x «лучшая деталь»: правило мастера при двух неисправных переворачивает выбор.
    lo, hi = run(F(1, 4)), run(F(3, 4))
    assert lo[0] > lo[1] and hi[0] > hi[1]          # оставленная батарейка надёжнее у обоих мастеров
    assert lo[2] > lo[3] and hi[2] < hi[3]          # но лучший донор противоположный
    print(f"r=1/4: батарейка {lo[0]} vs {lo[1]}, светит {lo[2]} vs {lo[3]}; "
          f"r=3/4: батарейка {hi[0]} vs {hi[1]}, светит {hi[2]} vs {hi[3]}")
    print("OK: формулы P3, лемма ковариации и разворот по правилу мастера подтверждены точно.")
