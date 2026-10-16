# Оценка новизны здешними агентами, 16.10.2026

Вопрос: [NOVELTY-PROMPT-2026-10-16.md](NOVELTY-PROMPT-2026-10-16.md). Агенты запущены с чистым контекстом, без инструментов (без поиска и файлов), с одинаковым текстом. Правило подсчёта — research/STATUS.md, «Правило предварительной новизны».

## Агент 1 — Sonnet (ответ дословно)

All from memory; no search or files used.

(A) Deletion vs requota: PARTLY KNOWN. Known: outcome depends on host protocol (Morgan, Chaganty, Dahiya, Doviak 1991 "Let's Make a Deal: The Player's Dilemma"; Gillman; Rosenhouse 2009 "The Monty Hall Problem"; Granberg/Mueser variants; Gill on host strategy). "Monty Fall" is exactly the deletion case (condition on no car, answer 1/2); Monty Crawl and similar are relatives. Possibly new: the clean deletion/requota split and the theorem that for permutation-invariant plans with p0 <= every rival prior deletion costs exactly 0 and all of the 1/2 -> 2/3 gain is from requota; I know of no exact statement of it. Small generalization of known protocol-dependence.

(B) Coin host, unequal priors: NOVEL (modest, niche). I know of no source for the explicit loss formula, the free-protection criterion (p0 <= all rival priors), or the sharp bound 1/y* with y* = -W_{-1}(-e^{-2}) ~ 3.146 (y e^{-y} = e^{-2} does give ~3.146). It is a closed-form computation in a toy model, not a new principle.

(C) Zero-value criterion: PARTLY KNOWN, essentially known. Value of information is zero iff no signal can change the optimal decision (Raiffa & Schlaifer 1961; Howard 1966). That value can differ between forced choice and a walk-away option is standard decision-analysis folklore. The atom criterion is a specialization; the six-piece binary function and the 1/7, 3/7, 3/7 example are new concrete computations, not new theory.

(D) Snapshot vs failure order (flashlights): NOVEL as a puzzle, not scientific novelty. No source known for this exact puzzle (resembles recreational battery/bulb puzzles in Winkler/Gardner style collections). The principle is standard: a test not distinguishing relevant states has zero value; failure order is informative (competing risks / reliability).

(E) Weaker donor, better assembly: NOVEL as an example, not scientific novelty. The rates (1+r)/3 vs (2-r)/3 and the reversal for 1/2 < r < 1 are probably not stated in this form, but the phenomenon is a conditioning/selection effect in the family of inspection-paradox and Simpson-type observations. No new mathematics.

Verdicts:
Scientific novelty (A): NO (exact theorem possibly unpublished, but a small generalization of known protocol-dependence).
Scientific novelty (B): YES (modest).
Scientific novelty (C): NO.
Scientific novelty (D): NO.
Scientific novelty (E): NO.

Strongest candidate: (B), the only item giving an explicit, verifiable closed form with a sharp constant that I cannot match to existing literature. (A) is the cleanest conceptual framing and would be the natural companion theorem, but its core idea is already in the Monty Hall protocol literature. Caveat: unchecked against the literature, so "NOVEL" means "I know of no source".

## Агент 2 — Opus (вердикты и обоснования, сокращено до сути)

Отвечал по памяти, без поиска и файлов. «Не знаю» означает «не помню точного утверждения».

- (A) PARTLY KNOWN. Случай трёх дверей и равных априоров — это Monty Fall (Rosenthal 2008). Сила условия «ведущему запрещена ваша дверь» обсуждается у Rosenthal 2008, Rosenhouse 2009, Falk 1992. Новое: явное разделение на вычёркивание и перепланирование и общая теорема для перестановочных планов при p0 ≤ всех соперников. **Scientific novelty (A): YES** (скромно).
- (B) NOVEL. Ведущие, открывающие каждую козу с вероятностью q, известны (типа Monty Crawl). Источника, где есть формула потерь по множествам C, критерий «защита бесплатна ⇔ p0 ≤ всех соперников» и точная граница 1/y*, y* = −W₋₁(−e⁻²) ≈ 3,146, он не знает. **Scientific novelty (B): YES.**
- (C) PARTLY KNOWN, ядро известно. Информация не имеет ценности, если не может изменить решение (Raiffa–Schlaifer 1961, Howard 1966). Ценность информации немонотонна при добавлении опции (Gould 1974, Hilton 1981). Новы только частности: функция из шести кусков, изолированный ноль, пример +5/108 против 0. **Scientific novelty (C): NO.**
- (D) PARTLY KNOWN. Информативность порядка отказов известна (конкурирующие риски, Cox 1959, Tsiatis 1975). Конкретная конструкция с тремя фонариками, где идеальный снимок стоит 0, а порядок отказов даёт столько же, сколько полная информация, ему неизвестна. **Scientific novelty (D): YES** (слабо).
- (E) PARTLY KNOWN. Надёжность системы зависит от совместного закона, отбор может переворачивать порядок (эффекты типа Симпсона). Источника с явными формулами и окном 1/2 < r < 1 он не знает. **Scientific novelty (E): YES** (слабо).

Сильнейший кандидат — (B): единственный нетривиальный результат в замкнутом виде, с точным «тогда и только тогда» и константой Ламберта.

## Подсчёт по правилу (≥2 агента «YES» или большинство)

| Пункт | Sonnet | Opus | Итог |
|---|---|---|---|
| (A) P12, вычёркивание/перепланирование | NO | YES | 1 из 2 — не достигнуто |
| (B) P12, монетка: формула потерь, критерий, граница 1/y* | YES | YES | **НОВИЗНА ПРЕДВАРИТЕЛЬНО ЕСТЬ** |
| (C) P13, критерий нуля через атомы | NO | NO | НЕТ (оба: частный случай известного принципа ценности информации) |
| (D) P14/R25, снимок против порядка отказов | NO | YES | 1 из 2 — не достигнуто |
| (E) R03, донор-фонарик | NO | YES | 1 из 2 — не достигнуто |

Оба агента называют (B) сильнейшим кандидатом. Оговорка обоих: «NOVEL» означает «источник неизвестен», литература не проверялась.

Замечание к прежнему статусу R01/R02/P11: оба агента считают общий критерий нуля (C) известным принципом. Статус R01/R02/P11 это не отменяет: там другой вопрос и другие оценщики. Но видно, что на оценку «ново» общее ядро не тянет; сильнее выглядят конкретные результаты в замкнутом виде.

# Второй вопрос: P15 и P16 (16.10)

Вопрос: [NOVELTY-PROMPT-2026-10-16b.md](NOVELTY-PROMPT-2026-10-16b.md). (F) — P15, исход-исключение и отсутствие зеркала R02. (G) — P16: (1) формула потерь для любого перестановочного ведущего, (2) «счётчик выдаёт вычеркнутое», (3) худший ведущий — монетка, предел 1/y*. Те же условия: чистый контекст, без инструментов.

## Агент 2 — Opus (сокращено до сути)

Известное по памяти: Selvin 1975; Morgan–Chaganty–Dahiya–Doviak 1991; Bapeswara Rao и Rao 1992; Lucas–Rosenhouse–Schepler 2009; Rosenhouse 2009; Gill 2011; Blackwell 1951/53. По его памяти ни одна из этих работ не содержит утверждений ниже.

- (F) NOVEL as stated. Общий факт, что внешняя опция может повышать или понижать ценность информации, известен. Теорема «исход с l=0 ⇒ полезность при обязательном выборе влечёт полезность при праве уйти» и контрпример 1/7, 3/7, 3/7 ему неизвестны. Из Блэкуэлла это прямо не следует: эксперимент один, меняется набор действий. Оговорка: лемма естественная, могла встречаться в теории поиска (Stone) или в анализе медицинских тестов. **Scientific novelty (F): YES** (скромно).
- (G1) NOVEL: точная формула для произвольного перестановочного ведущего и любых априоров неизвестна, хотя это прямой (аккуратный) байесовский расчёт.
- (G2) NOVEL как точное утверждение, частично известно по духу: что число открытых дверей несёт информацию — фольклор. Точный критерий «нет соседних размеров» и бесплатность вычёркивания при любых априорах, включая фаворита, ему неизвестны.
- (G3) NOVEL: экстремальных результатов по всем перестановочным ведущим, «худший — монетка с q = 1 − p/p0» и точной константы 1/y* ≈ 0,318 он не знает. Техника (двойственность ЛП, лог-вогнутость) стандартна, применение и константа — новые. Оговорка: модель нишевая, значимость скромная.
- **Scientific novelty (G): YES.**

Сильнейшая часть — (G3): настоящая экстремальная теорема по бесконечномерному классу ведущих с неочевидным худшим случаем и точной константой. Вторая — (G2): неожиданное и простое утверждение.

## Агент 1 — Sonnet (сокращено до сути)

- (F) PARTLY KNOWN / NOVEL as stated. Точного утверждения не знает: ни в литературе о Монти с неравными априорами и разными ведущими (Mueser–Granberg, Morgan et al., Bapeswara Rao–Rao, Gill, Selvin, Monty Fall/Crawl), ни в текстах о ценности информации по Блэкуэллу. Известно общее: больше информации не вредит байесовцу, а право уйти меняет ценность информации. **Scientific novelty (F): YES** (скромно по охвату).
- (G1) NOVEL: замкнутой формулы цены вычёркивания для общих законов размера плана не знает.
- (G2) PARTLY KNOWN. Механизм — фольклор: если ведущий всегда открывает ровно k дверей, их число ничего не несёт («открыть N−2 коз» — учебный случай). Новое — рамка «счётчик выдаёт вычеркнутое» и бесплатность при любых априорах, включая фаворита.
- (G3) NOVEL. Константу он проверил сам: при N→∞ и s=(N−1)(1−q) потеря стремится к (1−e^{−s})/(1+s), максимум при e^s = 2+s даёт 1/(2+s) = 1/y*. Супремум не достигается ни при каком конечном N.
- **Scientific novelty (G): YES** ((1) и (3) новые, (2) частично фольклор).

Сильнейшая часть — (G3).

## Подсчёт (второй вопрос)

| Пункт | Sonnet | Opus | Итог |
|---|---|---|---|
| (F) P15, исход-исключение ⇒ нет зеркала R02 | YES | YES | **НОВИЗНА ПРЕДВАРИТЕЛЬНО ЕСТЬ** |
| (G) P16: формула потерь, счётчик, худший ведущий | YES | YES | **НОВИЗНА ПРЕДВАРИТЕЛЬНО ЕСТЬ** |

По частям P16: (G1) и (G3) — оба «NOVEL»; (G2) — Opus «NOVEL как точное утверждение», Sonnet «частично фольклор». Оба агента назвали сильнейшей частью (G3): худший ведущий — монетка с q = 1 − p/p0, точная граница 1/y* ≈ 0,318.
