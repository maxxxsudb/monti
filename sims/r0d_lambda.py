# r0d_lambda.py -- Write/Read-смесь из 'Концептуально' 3.2, 3.4: Delta = lam(N-2)/N + (1-lam)(1-2phi)
import random
random.seed(4)
T = 10**6
def sim(N, lam, phi):
    st = sw = 0
    for _ in range(T):
        if random.random() < lam:          # Read: приз поставлен заранее, ведущий информирован, оставляет 1 из O
            p = random.randint(1, N)
            other = p if p != 1 else random.randint(2, N)
            st += p == 1; sw += p == other
        else:                              # Write: приз рождается после вскрытия между двумя оставшимися
            st_win = random.random() < phi
            st += st_win; sw += not st_win
    return (sw - st) / T
for N, lam, phi in [(3, 0.75, 1.0), (3, 0.5, 0.5), (10, 0.4, 0.5), (3, 1.0, 0.5)]:
    ex = lam*(N-2)/N + (1-lam)*(1-2*phi)
    print("N=%d lam=%.2f phi=%.2f  Delta exact %+.4f MC %+.4f" % (N, lam, phi, ex, sim(N, lam, phi)))
