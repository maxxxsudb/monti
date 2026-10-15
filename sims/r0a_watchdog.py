# R0-A: Астрон П5 "Ловушка редкого спасателя" (заявлено 91%)
# Допущения: авария (10%) -> лог чист в конце месяца; без аварии P(0 warnings)=1%.
import random
random.seed(5)
N = 10**6
exact = 0.1/(0.1+0.9*0.01)
clean = crash_clean = 0
w_any = crash_w = 0
for _ in range(N):
    crash = random.random() < 0.1
    if crash: zero = True
    else: zero = random.random() < 0.01
    if zero: clean += 1; crash_clean += crash
    else: w_any += 1; crash_w += crash
print("P(авария|чистый лог) exact=%.4f MC=%.4f" % (exact, crash_clean/clean))
print("P(авария|есть warnings) MC=%.4f (=0 только при допущении 'после рестарта мусор не копится')" % (crash_w/w_any))
# вариант: после рестарта warnings копятся заново, P(0 после рестарта)=0.5
q = 0.5
e2 = 0.1*q/(0.1*q+0.9*0.01)
e3 = 0.1*(1-q)/(0.1*(1-q)+0.9*0.99)
print("если после рестарта лог чист с вер. 0.5: P(авария|чисто)=%.4f, P(авария|warnings)=%.4f" % (e2, e3))
