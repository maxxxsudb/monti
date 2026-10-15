# r0d_everyday.py -- протоколы "бытовых Монти" из 'Истинные и спорные'. Вы держите 1, приз равновероятен в 1..3.
import random
random.seed(3)
T = 10**6
def run(name, proto, exact):
    st = sw = acc = 0
    for _ in range(T):
        r = proto()
        if r is None: continue
        acc += 1; st += r == 'stay'; sw += r == 'switch'
    print("%-62s P(stay) exact %-6s MC %.4f | P(switch) MC %.4f | accepted %d" % (name, exact, st/acc, sw/acc, acc))

def A_informed():                       # (а) ведущий знает, обходит ваш и приз
    p = random.randint(1, 3); opened = random.choice([d for d in (2, 3) if d != p])
    other = 5 - opened
    return 'stay' if p == 1 else ('switch' if p == other else None)
def B_blind():                          # (б) один из невыбранных проверяется вслепую (тоннели, дорогой анализ, код, антидот...)
    p = random.randint(1, 3); opened = random.choice([2, 3])
    if opened == p: return None         # проверка нашла приз -> другой сценарий
    return 'stay' if p == 1 else 'switch'
def B_blind_fixed():                    # (б') проверяют всегда №3 (ключи на полке, "сейф №2")
    p = random.randint(1, 3)
    if p == 3: return None
    return 'stay' if p == 1 else 'switch'
def C_both_report_one():                # (в) тестируют ОБА невыбранных, сообщают только про один плохой
    return A_informed()
def D_unnamed():                        # (г) "одно из двух других точно занято" без указания какое: всегда истинно
    p = random.randint(1, 3); return 'stay' if p == 1 else 'other'
def E_prior(pa=0.6):                    # (д) первый выбор "самый вероятный": P(A)=0.6, B,C по 0.2; ведущий информирован
    u = random.random(); p = 1 if u < pa else (2 if u < pa + (1-pa)/2 else 3)
    opened = random.choice([d for d in (2, 3) if d != p]); other = 5 - opened
    return 'stay' if p == 1 else 'switch'
def E_prior_blind(pa=0.6):              # (д') то же, но проверка вслепую
    u = random.random(); p = 1 if u < pa else (2 if u < pa + (1-pa)/2 else 3)
    opened = random.choice([2, 3])
    if opened == p: return None
    return 'stay' if p == 1 else 'switch'
# Амулет: 3 ячейки, 2 бомбы, 1 пусто; вы на №1 под амулетом.
def amulet_a():                         # прочтение a: ведущий взрывает случайную из ВЗРЫВАЕМЫХ (не вашу) бомб
    e = random.randint(1, 3); bombs = [c for c in (1, 2, 3) if c != e]
    expl = random.choice([b for b in bombs if b != 1])
    if expl != 3: return None
    return 'stay' if e == 1 else 'switch'
def amulet_b():                         # прочтение b: ведущий выбирает случайную из ВСЕХ бомб; если вашу -- амулет гасит, взрыва нет
    e = random.randint(1, 3); bombs = [c for c in (1, 2, 3) if c != e]
    pick = random.choice(bombs)
    if pick != 3: return None           # наблюдали именно взрыв №3
    return 'stay' if e == 1 else 'switch'
def amulet_c():                         # прочтение c: ведущий жмёт кнопку на случайной из двух ДРУГИХ ячеек (не зная)
    e = random.randint(1, 3); pick = random.choice([2, 3])
    if pick != 3 or e == 3: return None # нажал 3 и она взорвалась
    return 'stay' if e == 1 else 'switch'
def amulet_d():                         # прочтение d: подрываются ВСЕ бомбы разом, ваша погашена; видим ровно один взрыв в №3
    e = random.randint(1, 3); expl = [c for c in (1, 2, 3) if c != e and c != 1]
    if expl != [3]: return None
    return 'stay' if e == 1 else 'switch'

run("(а) информированный ведущий (Монти)", A_informed, "1/3")
run("(б) вслепую проверен один из двух невыбранных", B_blind, "1/2")
run("(б') всегда проверяют конкретный №3", B_blind_fixed, "1/2")
run("(в) проверили оба невыбранных, показали один плохой", C_both_report_one, "1/3")
run("(г) 'одно из двух других плохое', не названо (P(stay))", D_unnamed, "1/3")
run("(д) первый выбор P=0.6, ведущий информирован", E_prior, "0.6")
run("(д') первый выбор P=0.6, проверка вслепую", E_prior_blind, "0.75")
run("амулет a: случайная из взрываемых бомб", amulet_a, "1/3")
run("амулет b: случайная из всех бомб, ваша погашена", amulet_b, "1/2")
run("амулет c: случайная из двух других ячеек (вслепую)", amulet_c, "1/2")
run("амулет d: все бомбы разом, видим 1 взрыв", amulet_d, "0")
