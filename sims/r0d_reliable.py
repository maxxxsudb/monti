# r0d_reliable.py -- дискретная версия кандидата: 3 ячейки, 2 бомбы, ваша (№1) под амулетом.
# Каждая незаглушённая бомба за ночь взрывается с вер. p независимо. Утром: взорвалась только №3.
# Точно: P(stay) = (1-p)/(2-p). Без амулета (ваша тоже может взорваться, вы живы): 1/2 при любом p.
import random
random.seed(6)
T = 10**6
for p in (0.1, 0.5, 0.9):
    st = n = st2 = n2 = 0
    for _ in range(T):
        e = random.randint(1, 3)
        boom = {c: (c != e and random.random() < p) for c in (1, 2, 3)}
        # с амулетом: №1 не может взорваться
        if boom[3] and not boom[2]:
            n += 1; st += e == 1
        # без амулета: наблюдаем взрыв только №3 (№1 и №2 целы)
        if boom[3] and not boom[2] and not boom[1]:
            n2 += 1; st2 += e == 1
    print("p=%.1f amulet: P(stay) exact %.4f MC %.4f (n=%d) | no amulet: exact 0.5000 MC %.4f (n=%d)"
          % (p, (1-p)/(2-p), st/n, n, st2/n2, n2))
