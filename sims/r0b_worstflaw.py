# Бытовые #8/#9/#13 (МОЯ модель, в тексте чисел нет): «худшая найденная жалоба — мелочь».
# Товар хороший/плохой 50/50, 10 отзывов. Отзыв: серьёзная жалоба (плохой 0.3, хороший 0.02), иначе мелкая с 0.4, иначе без жалоб.
import random
rnd=random.Random(7); T=1_000_000; n=10
ps={True:0.02,False:0.3}; pt=0.4
def rev(good):
    u=rnd.random()
    if u<ps[good]: return 2
    return 1 if rnd.random()<pt else 0
A=[0,0]; B=[0,0]
for _ in range(T):
    g=rnd.random()<.5; r=[rev(g) for _ in range(n)]
    if max(r)==1: A[0]+=1; A[1]+=g          # отобранная худшая — мелкая
    c=[x for x in r if x>0]
    if c and rnd.choice(c)==1: B[0]+=1; B[1]+=g  # случайная жалоба — мелкая
# точно
def pA(good): s=ps[good]; return (1-s)**n-((1-s)*(1-pt))**n
def pB(good):  # случайная из жалоб мелкая: E[#triv/#compl | compl>0]; доля мелких среди жалоб постоянна
    s=ps[good]; fr=(1-s)*pt/((1-s)*pt+s); P_any=1-((1-s)*(1-pt))**n; return P_any*fr
exA=pA(True)/(pA(True)+pA(False)); exB=pB(True)/(pB(True)+pB(False))
print("P(good | worst=trivial) MC=%.4f exact=%.4f"%(A[1]/A[0],exA))
print("P(good | random complaint=trivial) MC=%.4f exact=%.4f   prior=0.5"%(B[1]/B[0],exB))
