"""Решает ли время фиксации приза? 3 двери, я выбираю дверь 0. Считаем P(выигрыш при переключении | открыта коза).
Сравниваем протоколы с разным порядком во времени и разной зависимостью размещения."""
import random
R = random.Random(7); T = 400000

def run(protocol):
    win_sw = n = 0
    for _ in range(T):
        r = protocol()
        if r is None: continue          # игра отброшена (ведущий открыл приз)
        prize, opened = r
        n += 1
        other = ({0, 1, 2} - {0, opened}).pop()
        win_sw += prize == other
    return win_sw / n

def A_read_informed():                       # приз СНАЧАЛА, знающий ведущий открывает козу
    p = R.randrange(3); h = R.choice([d for d in (1, 2) if d != p]); return p, h
def B_write_uniform_all():                   # дверь СНАЧАЛА (наугад), приз ПОТОМ равномерно по всем; оставляем игры с козой
    h = R.choice([1, 2]); p = R.randrange(3); return None if p == h else (p, h)
def C_write_uniform_closed():                # дверь СНАЧАЛА, приз ПОТОМ равномерно среди закрытых
    h = R.choice([1, 2]); p = R.choice([0, 3 - h]); return p, h
def D_write_twin():                          # дверь СНАЧАЛА, приз ПОТОМ по закону P(приз|дверь) из A: моя 1/3, другая 2/3
    h = R.choice([1, 2]); p = 0 if R.random() < 1/3 else 3 - h; return p, h
def E_read_ignorant():                       # приз СНАЧАЛА, НЕзнающий ведущий (Monty Fall)
    p = R.randrange(3); h = R.choice([1, 2]); return None if p == h else (p, h)

for name, f in [("A  приз сначала, ведущий знает       ", A_read_informed),
                ("E  приз сначала, ведущий НЕ знает    ", E_read_ignorant),
                ("B  приз потом, равномерно по всем    ", B_write_uniform_all),
                ("C  приз потом, равномерно по закрытым", C_write_uniform_closed),
                ("D  приз потом, по закону как в A     ", D_write_twin)]:
    print(name, f"P(выигрыш при переключении) = {run(f):.4f}")

# Где «время» влияет: размещение ПОСЛЕ моего финального решения может зависеть от него.
def F_after_my_decision(strategy):           # ведущий открыл дверь наугад из 1,2; я решаю; приз ставят ПОСЛЕ решения
    wins = 0
    for _ in range(T):
        h = R.choice([1, 2]); final = (3 - h) if strategy == "switch" else 0
        p = R.choice([d for d in (0, 1, 2) if d != h])          # равномерно по закрытым, не зная моего решения
        wins += p == final
    return wins / T
def G_adversarial_after(strategy):           # приз ставят ПОСЛЕ решения и избегают моей двери
    return 0.0
print("F  приз после МОЕГО решения, не зная его: stay", round(F_after_my_decision("stay"),4), "switch", round(F_after_my_decision("switch"),4))
print("G  приз после моего решения, ЗНАЯ его (враждебно): stay/switch = 0 — решает зависимость, не время")
