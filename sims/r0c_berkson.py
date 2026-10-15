# r0c_berkson: batteries (2/3 -> 1/2) and cars repaired before/after admission (routine vs motivated repair)
import random
random.seed(11); T = 10**6
c = b2 = c1 = b2g1 = 0
for _ in range(T):
    a, b = random.random() < .5, random.random() < .5
    if not (a or b): continue
    c += 1; b2 += b
    if a: c1 += 1; b2g1 += b
print(f"batteries: P(B2|sold)={b2/c:.4f} exact 2/3; P(B2|sold,B1 ok)={b2g1/c1:.4f} exact 1/2")
# cars: engine E, gearbox G ~ Bern(1/2). Admitted iff E or G (at admission time).
def car(protocol):
    E, G = random.random() < .5, random.random() < .5
    if protocol == 'before_routine': G = True  # gearbox replaced before admission
    adm = E or G
    if not adm: return None
    if protocol == 'after_routine': G = True
    if protocol == 'after_motivated':
        if G: return 'skip'   # only cars whose gearbox turned out broken get repaired
        G = True
    return E
for p in ('before_routine', 'after_routine', 'after_motivated'):
    n = e = 0
    for _ in range(T):
        r = car(p)
        if r is None or r == 'skip': continue
        n += 1; e += r
    print(f"{p:16s}: P(engine good | in salon, gearbox now good) = {e/n:.4f}")
print("exact: before 1/2, after_routine 2/3, after_motivated 1")
