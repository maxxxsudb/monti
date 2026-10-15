import random

rng = random.Random(14026)
n = 1_000_000
classic = blind_count = blind_switch = mixed_switch = 0
before = after_count = after_good = 0
for _ in range(n):
    prize = rng.randrange(3)
    classic += prize != 0
    opened = rng.choice((1, 2))
    if opened != prize:
        blind_count += 1
        blind_switch += prize != 0
    fixed = rng.random() < 0.75
    mixed_switch += fixed and prize != 0
    engine = rng.randrange(2)
    gearbox = rng.randrange(2)
    before += engine
    if engine or gearbox:
        after_count += 1
        after_good += engine

for label, exact, empirical in (
    ('classic switch', 2 / 3, classic / n),
    ('blind test, switch given failure', 1 / 2, blind_switch / blind_count),
    ('fixed/open mixture, lambda=.75 phi=1 switch', 1 / 2, mixed_switch / n),
    ('repair before selection, engine good', 1 / 2, before / n),
    ('repair after selection, engine good', 2 / 3, after_good / after_count),
):
    print(f'{label}: exact={exact:.8f} empirical={empirical:.8f}')
