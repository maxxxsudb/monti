# r0c_partial: uninformed regime = Monty Fall (car may be revealed -> game discarded) instead of Write-world.
# Then mixture is reweighted: P(switch wins | goat shown) = (1+lam)/(2+lam), not 1/2+lam/6. lambda-clock biased.
import random
random.seed(9); T = 10**6
for lam in (0.25, 0.5, 0.75):
    n = w = s = 0
    for _ in range(T):
        car = random.randrange(3)
        if random.random() < lam:  # informed host
            opened = random.choice([1, 2]) if car == 0 else 3 - car
        else:
            opened = random.choice([1, 2])
            if opened == car: continue  # car revealed: game void
        n += 1; other = 3 - opened; s += car == 0; w += car == other
    print(f"lam={lam}: switch={w/n:.4f} exact (1+lam)/(2+lam)={(1+lam)/(2+lam):.4f}  text-formula 1/2+lam/6={0.5+lam/6:.4f}  lam_hat=3*Delta={3*(w-s)/n:.3f}")
