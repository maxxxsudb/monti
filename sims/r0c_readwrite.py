# r0c_readwrite: Read-Monty vs Write-Monty, Monty Fall equivalence, lambda-mixture, phi-model, non-identifiability
import random
from fractions import Fraction as Fr
random.seed(20261014)
T = 10**6

def read_world(N):  # car placed first, player picks 0, host opens N-2 goat doors (informed), leaves one other door
    car = random.randrange(N)
    other = car if car != 0 else random.randrange(1, N)
    return car == 0, car == other, other

def write_world(N):  # host leaves random other door first, then car placed uniformly among the 2 remaining
    other = random.randrange(1, N)
    car = random.choice([0, other])
    return car == 0, car == other, other

def run(f, N, n=T):
    s = w = 0
    for _ in range(n):
        st, sw, _o = f(N); s += st; w += sw
    return s/n, w/n

print("=== 1. Read vs Write, N=3,5,10 (exact read: 1/N,(N-1)/N; write: 1/2,1/2) ===")
for N in (3, 5, 10):
    r = run(read_world, N); wr = run(write_world, N)
    print(f"N={N}: READ stay={r[0]:.4f} sw={r[1]:.4f} exact {1/N:.4f}/{(N-1)/N:.4f} | WRITE stay={wr[0]:.4f} sw={wr[1]:.4f} exact 0.5/0.5")

print("=== 2. Joint law (opened, car) : Write world vs Monty Fall (|goat) ===")
from collections import Counter
cw = Counter(); cf = Counter(); nf = 0
for _ in range(T):
    other = random.randrange(1, 3); car = random.choice([0, other]); opened = 3 - other
    cw[(opened, car)] += 1
for _ in range(T):
    car = random.randrange(3); opened = random.choice([1, 2])  # ignorant host opens random non-player door
    if opened == car: continue
    nf += 1; cf[(opened, car)] += 1
keys = sorted(set(cw) | set(cf))
for k in keys:
    print(f"opened={k[0]} car={k[1]}: write={cw[k]/T:.4f}  montyfall|goat={cf[k]/nf:.4f}  exact=0.25")

print("=== 3. Counterexamples: fixation time is neither necessary nor sufficient ===")
# (a) car placed AFTER opening, by rule pre-committed: car behind the surviving other door w.p. 2/3, player's door w.p. 1/3
s = w = 0
for _ in range(T):
    other = random.randrange(1, 3); car = other if random.random() < 2/3 else 0
    s += car == 0; w += car == other
print(f"(a) placed AFTER, precommitted 2/3 rule: stay={s/T:.4f} sw={w/T:.4f} exact 1/3,2/3")
# (b) car placed BEFORE, host ignorant (Monty Fall) conditioned on goat
s = w = n = 0
for _ in range(T):
    car = random.randrange(3); opened = random.choice([1, 2])
    if opened == car: continue
    n += 1; other = 3 - opened; s += car == 0; w += car == other
print(f"(b) placed BEFORE, ignorant host |goat: stay={s/n:.4f} sw={w/n:.4f} exact 1/2,1/2")

print("=== 4. lambda-mixture, N=3 table and N=5,10 Delta=lambda(N-2)/N ===")
for N in (3, 5, 10):
    for lam in (0, .25, .5, .75, 1):
        s = w = 0
        n = T
        for _ in range(n):
            st, sw, _o = (read_world if random.random() < lam else write_world)(N); s += st; w += sw
        ex = lam*(N-2)/N
        ps = lam/N + (1-lam)/2
        print(f"N={N} lam={lam:.2f}: stay={s/n:.4f}(ex {ps:.4f}) sw={w/n:.4f}  Delta={ (w-s)/n:.4f} ex {ex:.4f}  lam_hat=N/(N-2)*Delta={N/(N-2)*(w-s)/n:.3f}")

print("=== 5. phi-model N=3, phi=1 : lambda_c = 3/4 ===")
# variant A (text): unfixed part resolves in favour of INITIAL pick (door 0) w.p. phi
# variant B (physical 'my choice causes win'): unfixed part resolves in favour of FINAL door w.p. phi
def game(lam, phi, switch, variant):
    if random.random() < lam:
        st, sw, _o = read_world(3); return sw if switch else st
    target_final = True
    if variant == 'A':
        initial_wins = random.random() < phi
        return (not initial_wins) if switch else initial_wins
    else:
        return random.random() < phi  # final door wins w.p. phi whatever it is
n = T
for lam in (0.5, 0.75, 0.9):
    for var in ('A', 'B'):
        ps = sum(game(lam, 1.0, False, var) for _ in range(n))/n
        pw = sum(game(lam, 1.0, True, var) for _ in range(n))/n
        exA = (lam/3 + (1-lam), lam*2/3)
        exB = (lam/3 + (1-lam), lam*2/3 + (1-lam))
        ex = exA if var == 'A' else exB
        print(f"lam={lam} var{var}: stay={ps:.4f}(ex {ex[0]:.4f}) switch={pw:.4f}(ex {ex[1]:.4f})")
print("exact: varA Delta = lam/3-(1-lam) =0 at lam=3/4 ->", Fr(3,4), "; varB Delta = lam/3 >=0 always (switch never loses)")
