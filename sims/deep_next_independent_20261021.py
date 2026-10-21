"""Independent exact checks of the two-probe theorem and four controls."""
from fractions import Fraction as F
from decimal import Decimal, getcontext

getcontext().prec = 45


class Q2:
    def __init__(self, a=0, b=0):
        self.a, self.b = F(a), F(b)

    def __add__(self, other):
        other = other if isinstance(other, Q2) else Q2(other)
        return Q2(self.a+other.a, self.b+other.b)

    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.a, -self.b)

    def __sub__(self, other):
        return self+-other if isinstance(other, Q2) else self+Q2(-other)

    def __rsub__(self, other):
        return -self+other

    def __mul__(self, other):
        other = other if isinstance(other, Q2) else Q2(other)
        return Q2(self.a*other.a+2*self.b*other.b,
                  self.a*other.b+self.b*other.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = other if isinstance(other, Q2) else Q2(other)
        den = other.a*other.a-2*other.b*other.b
        return self*Q2(other.a/den, -other.b/den)

    def __rtruediv__(self, other):
        return Q2(other)/self

    def __eq__(self, other):
        other = other if isinstance(other, Q2) else Q2(other)
        return (self.a, self.b) == (other.a, other.b)

    def dec(self):
        return (Decimal(self.a.numerator)/Decimal(self.a.denominator)
                + Decimal(2).sqrt()*Decimal(self.b.numerator)/Decimal(self.b.denominator))


def main():
    t, w, g = Q2(2, -1), Q2(F(22, 49), F(12, 49)), Q2(F(18, 49), F(-8, 49))
    f = lambda x: 2*x/(1+x)
    assert F(1, 2) < t.dec() < Decimal(2)/3
    assert 0 < w.dec() < 1 and g.dec() > 0
    assert (1-w)*F(2, 3) == g
    assert f(t)-(w*t+(1-w)*F(2, 3)) == g
    assert 2/((1+t)*(1+t)) == w
    assert w+(1-w)*F(2, 3)-1 == -g/2
    print('PASS exact Q(sqrt(2)): endpoint balance, minimum, derivative, endpoint x=1')
    print('optimal points:', 0, t.dec(), 'gap:', g.dec())
    print('relative gap increase vs 2/15:', (g.dec()/(Decimal(2)/15)-1)*100, '%')
    wr, gr = F(35, 44), F(3, 22)
    assert (1-wr)*F(2, 3) == gr
    assert f(F(3, 5))-(wr*F(3, 5)+(1-wr)*F(2, 3)) == gr
    print('PASS rational battery {0,3/5}: weights=', str(wr), 'gap=', str(gr))
    print('relative gap loss vs optimum:', (1-(Decimal(3)/22)/g.dec())*100, '%')

    variants = [(F(1, 2), F(2, 5)), (F(1, 3), F(1, 5)),
                (F(1, 2), F(1, 5)), (F(1, 3), F(2, 5))]
    post = [prior*F(4, 5)/(prior*F(4, 5)+(1-prior)*ordinary)
            for prior, ordinary in variants]
    assert post == [F(2, 3), F(2, 3), F(4, 5), F(1, 2)]
    assert post[2]-post[0] == F(2, 15) and post[0]-post[3] == F(1, 6)
    print('PASS exact controls A B C D:', [str(p) for p in post])

    dx, dy, lam, kappa, ell = F(2, 3)-f(F(1, 10)), F(2, 3)-f(F(1, 5)), F(2, 5), F(13, 20), F(7, 100)
    joint = {}
    for z1 in (0, 1):
        prob1 = lam if z1 else 1-lam
        next_prob = (1-kappa)*lam+kappa*z1+ell
        assert 0 <= next_prob <= 1
        for z2 in (0, 1):
            latent_prob = prob1*(next_prob if z2 else 1-next_prob)
            mu1, mu2 = f(F(1, 10))+z1*dx, f(F(1, 5))+z2*dy
            for a1 in (0, 1):
                for a2 in (0, 1):
                    joint[a1,a2] = joint.get((a1,a2), F(0))+latent_prob*(mu1 if a1 else 1-mu1)*(mu2 if a2 else 1-mu2)
    assert sum(joint.values()) == 1
    mean1 = sum(a1*p for (a1,a2),p in joint.items())
    mean2 = sum(a2*p for (a1,a2),p in joint.items())
    cov = joint[1,1]-mean1*mean2
    assert cov == lam*(1-lam)*kappa*dx*dy
    assert (mean2-f(F(1, 5)))/dy-lam == ell
    print('PASS exact latent model: covariance=', str(cov), 'learning=', str(ell))
    print('Proof of global optimality uses convexity; no source NumPy/SciPy script executed.')
    print('No human data, no universal causal diagnosis or optimal sampling-cost claim.')


if __name__ == '__main__':
    main()
