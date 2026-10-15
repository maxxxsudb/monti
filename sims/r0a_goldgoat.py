# R0-A: Астрон П4 "Золотая коза" / гибрид 3 "Конкретной причины" (заявлено 1/2)
# Протокол P: ведущий предпочитает показать G* (если G* среди 2,3 и не машина-ограничение).
# Протокол R: ведущий открывает случайную козу из 2,3 и честно называет её тип.
import random, itertools
random.seed(3)
N = 10**6
perms = list(itertools.permutations(["A", "G", "S"]))  # S = золотая коза

def host(lay, proto):
    goats = [d for d in (1, 2) if lay[d] != "A"]
    if proto == "P":
        gs = [d for d in goats if lay[d] == "S"]
        if gs: return gs[0]
    return random.choice(goats)

for proto in ("P", "R"):
    cntS = winS = cntG = winG = 0
    for _ in range(N):
        lay = random.choice(perms)
        d = host(lay, proto)
        if d != 2: continue  # открыта дверь 3 (индекс 2)
        car2 = lay[1] == "A"
        if lay[2] == "S": cntS += 1; winS += car2
        else: cntG += 1; winG += car2
    print("протокол %s: P(маш.за 2|дв.3=золотая)=%.4f  P(маш.за 2|дв.3=обычная)=%.4f"
          % (proto, winS/cntS, winG/cntG))
print("exact: P: 1/2 и 1;  R: 2/3 и 2/3")
