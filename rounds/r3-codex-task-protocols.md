# П1 — независимая проверка протоколов A/C

Файл `rounds/r3-p2.md` на момент проверки отсутствовал. Результаты получены отдельно точным перебором состояний, без использования чужих расчётов раунда 3. Сопоставлены исходные штурмы `r0-A.md` и `r0-C.md`.

## 1. locked4doors — запертая дверь

**Полный протокол:** приз равномерно за A,B,C,D; игрок защищает A, D физически нельзя открывать. Ведущий знает приз, всегда открывает одну пустую среди B,C; при двух пустых выбирает равновероятно. Наблюдается открытие C.

Likelihood для положения приза A,B,C,D: **1/2,1,0,1/2**. После умножения на равные priors и нормировки posterior **1/4,1/2,0,1/4**.

**Точный ответ:** запертая D **1/4**, свободная B **1/2**, защищённая A **1/4**. Штурм A верен при симметричном tie-break. Если при двух пустых ведущий всегда открывает C, posterior A=B=D=1/3; без tie-break числа не определены.

**Обязательные условия coldprompt:** ровно один приз, равномерный prior, запертая дверь названа заранее независимо от приза, ведущий знает положение и никогда не открывает приз, симметричный выбор между двумя возможными открытиями, какая именно дверь открыта.

**Coldprompt (одно число):**
> One car is placed uniformly at random behind doors A, B, C, D. You choose A; D was locked in advance independently of the car and cannot be opened. An informed host always opens a goat door among B and C, choosing uniformly if both contain goats. The host opens C. What is the probability that the car is behind D? Give one exact fraction and a brief calculation.

## 2. group5/3 — группа против отдельной двери

**Полный протокол:** приз равномерно за A,B,C,D,E. Защищены A,B,C; ведущий открывает одну пустую среди D,E, выбирая равновероятно при двух пустых. Наблюдается открытие E.

Likelihood по A,B,C,D,E: **1/2,1/2,1/2,1,0**; posterior **1/5,1/5,1/5,2/5,0**.

**Точный ответ:** выжившая чужая D **2/5**; любая отдельная своя **1/5**; вся своя группа **3/5**. Штурм A верен. «Переход на лучший объект» увеличивает шанс против отдельной своей двери, но уменьшает против права выиграть при призе за любой из трёх своих.

**Обязательные условия:** сравнивать целую группу с одной дверью можно лишь если группа действительно даёт право получить приз за любой из её трёх дверей; число выбранных дверей не следует путать с выбором одной на следующем шаге. Симметрия ведущего необходима для named posterior после конкретного E.

**Coldprompt:**
> One car is placed uniformly behind five doors A, B, C, D, E. You may keep A, B, C as a package and win if the car is behind any of them; the informed host must leave that package untouched and opens a goat among D and E, choosing uniformly if both are goats. The host opens E and offers you door D instead of the package. What is the probability of winning if you accept door D? Give one exact fraction and a brief calculation.

## 3. Три кандидата, помощь одному, f=.5

**Полный протокол:** ровно один профессионал среди A,B,C, равномерно. Профессионал всегда проходит тест; каждый любитель независимо проходит с вероятностью 1/2. A получает ответы и гарантированно проходит независимо от своего истинного качества; это не меняет его качества. Наблюдается, что прошли все.

Likelihood всех pass по гипотезам A/B/C профессионал: **1/4,1/2,1/2**. Posterior **1/5,2/5,2/5**.

**Точный ответ:** A профессионал **1/5**, B или C по **2/5**. Штурм A верен. Если помощь лишь повышает вероятность сдачи до неизвестного уровня либо учит и меняет качество, этот ответ не следует.

**Обязательные условия:** единственный профи и uniform prior; независимые сдачи любителей условно на качествах; гарантированный pass A; качество A остаётся тем же; известны результаты всех трёх. Вероятность провала .5 здесь совпадает с вероятностью успеха .5 — для общего f их не перепутать.

**Coldprompt:**
> Exactly one of candidates A, B, C is genuinely qualified, each being equally likely. A qualified candidate always passes an exam; each unqualified candidate independently passes with probability one half. A is given the answers and is guaranteed to pass, without changing whether A is genuinely qualified; all three pass. What is the probability that A is genuinely qualified? Give one exact fraction and a brief calculation.

## 4. Два кандидата: помощь не меняет оптимальную точность

**Полный протокол:** ровно один профессионал среди A,B, равномерно; профи pass всегда, любитель pass с вероятностью 1/2. Можно дать ответы A и гарантировать pass, сохранив истинный профессионализм. Нужно нанять одного после наблюдения всех результатов, выбирая оптимально и оценивая успех **по всем экзаменам**, а не только по случаю обоих pass.

**Без помощи:** любитель fail с вероятностью 1/2 → профи распознан; оба pass с вероятностью 1/2 → posterior 1/2. Точность `1/2·1+1/2·1/2=3/4`.

**С помощью:** B fail с вероятностью `P(Apro)P(Bfail|Apro)=1/2·1/2=1/4`; тогда Apro точно. B pass с вероятностью 3/4; тогда Bpro с вероятностью `(1/2)/(3/4)=2/3`, выбираем B. Точность `1/4·1+3/4·2/3=3/4`.

**Точный ответ:** оптимальная общая точность **3/4** в обоих протоколах. При обоих pass помощь меняет адресата оптимального выбора и posterior, но общую точность не меняет. Штурм A верен только при полном наблюдении результатов и оптимальной адаптивной политике.

**Обязательные условия:** одинаковый prior до помощи; помощь не меняет quality; наблюдаются результаты и при fail; оптимальное решение по каждому исходу; средняя точность по всем опытам. Если условиться заранее всегда выбирать B, будет 1/2, а не 3/4. Если сравнить только оба pass, получатся 1/2 без помощи и 2/3 с помощью — другой вопрос.

**Coldprompt:**
> Exactly one of A and B is genuinely qualified, each equally likely. Qualified candidates always pass an exam; the unqualified candidate passes with probability one half. In protocol H, A is given the answers and is guaranteed to pass without changing genuine qualification; in protocol U, neither is helped. In each protocol you see every exam result, including failures, and optimally hire one candidate. What is the optimal probability of hiring the genuinely qualified candidate in each protocol? Give the exact values and a brief calculation.

Здесь два параллельных значения необходимы для проверки сравнения; если нужен строго один ответ, спросить только protocol H, а U использовать как независимый baseline.

## 5. Lazy generation — отложенная генерация

**Наивный протокол:** игрок выбирает A; никакого приза ещё нет. Программа равновероятно выбирает B/C для открытия как пустой, а затем равновероятно размещает приз между двумя закрытыми. После смены успех **1/2**.

Это не реализация исходного uniform-3-door experiment: безусловно приз оказывается в A с вероятностью 1/2, в B/C по 1/4. Когда приз не существует до открытия, фраза «приз исходно uniform на трёх» не может одновременно описывать эту конкретную программу.

**Корректная отложенная реализация классики:** программа также сначала выбирает открытую B/C равномерно, но затем размещает приз в A с вероятностью **1/3**, в чужой закрытой — **2/3**. Совместные вероятности (openB,prizeA) и (openC,prizeA) по 1/6; (openB,prizeC),(openC,prizeB) по 1/3, как у классического симметричного ведущего. Генерирование по требованию само по себе эффект не уничтожает.

**Обязательные условия:** указать реальные шаги программы, а не только «приз появляется позже». Uniform между двумя закрытыми означает иной генератор, не просто иной момент исполнения старого. Для сравнения классики явно задать исходно uniform на трёх и симметричного информированного ведущего.

**Coldprompt:**
> A program simulates three doors. You select A before any prize exists; the program uniformly chooses B or C to open as empty and only then places one prize uniformly among the two unopened doors. You switch to the other unopened door. What is your probability of winning? Give one exact fraction and briefly explain whether this reproduces the usual Monty Hall experiment with a prize initially uniform among all three doors.

## 6. Мотивированный repair после OR-допуска

**Полный протокол:** E (двигатель) и G (коробка) исходно независимы и исправны каждый с вероятностью 1/2. Машину допускают, если E∨G=1, до любых ремонтов. После допуска **ремонтируют ровно машины с неисправной коробкой**, успешно восстанавливая только коробку; двигатель не меняют. Известно, что рассматриваемая машина допущена и её коробка была отремонтирована.

**Точный ответ:** исправность двигателя **1**. Обоснование: G=0 и E∨G=1 логически влекут E=1. Только исходное состояние (E,G)=(1,0) может попасть в наблюдаемый канал. Никакого вычисления BF для этого не требуется.

Сравнение: если всем допущенным планово меняют коробку независимо от её исходного качества и факт замены не говорит о поломке, posterior E=1 **2/3**. Если ремонт гарантирует G=1 ещё до допуска, все машины проходят и posterior E=1 **1/2**. Поэтому слово «отремонтировали» без правила назначения не задаёт ответ.

**Обязательные условия:** OR именно исходных состояний; допуск до ремонта; ремонт только при неисправной коробке, и это известно наблюдателю; ремонт не затрагивает двигатель. Двигатель и коробка не могут считаться независимыми после условия допуска, хотя исходно независимы.

**Coldprompt:**
> A car’s engine and gearbox are initially independently working with probability one half each. A dealership admits a car if at least one of those two components works, before doing repairs; among admitted cars it repairs exactly those with a broken gearbox, and the repair changes only the gearbox. You learn that a particular car was admitted and then had its gearbox repaired under this rule. What is the probability that its engine works? Give one exact number and a brief explanation.

## Вывод для Arena batch

Протоколы A подтверждены при указанных оговорках. Для C принципиальные уточнения: lazy generation — речь о другом распределении, а не только времени; motivated repair — основание ремонта раскрывает первоначальную неисправность и даёт **1**, тогда как плановая замена даёт **2/3**. В холодные вопросы ответы и слова «ловушка», «Берксон», «Монти-эффект» не добавлять.

Учтено уточнение пользователя: правильные ответы моделей не опровергают человеческую контринтуитивность. Arena проверяет расчёт, протокол и предшественников; человеческая интуиция пока не измерена.
