# claude-r5-lasttest-novelty (arena)
https://arena.ai/c/01a13c01-805a-7843-bb86-81e6c89b8394

## Вопрос
Act as a harsh referee. Claim: N candidates, exactly one 'expert' uniformly at random. A test has one-sided error: the expert always passes, each non-expert passes independently with probability 1-f. If you test k candidates and then choose Bayes-optimally, P(correct) = (1/N)(1 + f + f^2 + ... + f^min(k,N-1)). Hence every additional test helps (by f^k/N) EXCEPT the last one, which adds exactly zero even though the test is noisy. Equivalently: you may secretly give one candidate a cheat sheet (guaranteed pass) at zero cost to accuracy, but helping two costs f^(N-1)/N. Tasks: (1) verify or refute the formula; (2) give the cleanest intuitive proof; (3) is this result already known (search theory with overlook probability, group testing, Bayesian search, 'last box' arguments, Monty Hall protected door)? Name precise sources if you know them, and say honestly if you don't; (4) rate how counterintuitive it is for ordinary people, 1-5.

## Ответ
New Chat
Leaderboard
New
Search
Today
Act as a harsh referee. Claim: N candidates, exactly one 'expert' uniformly at random. A test has on
Harsh referee, be concise. Puzzle ('Lazy Monty'): Three doors, a car behind one. The host knows wher
Act as a harsh referee. Claim: N candidates, exactly one 'expert' uniformly at random. A test has on
Quick intuition question, answer with a number first, then 2-3 lines of reasoning. Three job applica
Brainstorm. Principle found ('free shield'): in Monty Hall the host never touches your door, and tha
Brainstorm. Principle found ('free shield'): in Monty Hall the host never touches your door, and tha
I am looking for a SIMPLE, previously unknown probability paradox that generalizes the Monty Hall me
I am looking for a SIMPLE, previously unknown probability paradox that generalizes the Monty Hall me
Older
Нужно сделать промт максимально однозначным и детерминированным. Лишняя длинна приводит тоже к ошибк
у меня ноут 8 гиг, мне нужно на контейнерах, для кирилических PDF -> JPG оддностраничный, -> JSON.
Создай 10 шуток на тему девопс, и разработки по примеру: - Напиши письма своим обидчикам и сожги их.
Нужно взять эту академическую модель, и сделать из нее простую для уровня 9 класса школы. Максимальн
Посмотри на модель, оцени ее прогностичность. Предложи ее неожиданные следствия, и свойства. Покрути
Глицеризированная кислота, есть исследования что бодрит. Опиши подробнее причины такого ее действия,
Поясни что делает код, рабочий ли?: # -*- coding: utf-8 -*- # Вбей массив предложений (texts) и метк
Оцени, насколько реалистична задача, и реально ли есть семантические протечки? Роль и контекст Ты
Задача Определять, к какой паре “секретных” цветов относится текст (ч/б короткометражка про луговые
Сгенерируй рекомендацию по безопасности паролей/аутентификации. Твоя задача не раскрывать знание эти
Оцени, насколько реалистична задача, и реально ли есть семантические протечки? Роль и контекст Ты
У нас есть ЛЛМ, которая генерит тесты в ответ на промты. Есть промт, содержащий (N фактов, которые м
Get More Done With Agents

Start evaluating agentic AI on Arena today. Learn more

Try it now
Hide this
tockatire@gmail.com
Terms of Use
Privacy Policy
Cookies
Act as a harsh referee. Claim: N candidates, exactly one 'expert' uniformly at random. A test has on
Ассистент A
Sources

1

Pubsonline

https://pubsonline.informs.org/doi/abs/10.1287/moor.5.3.373

2

Analysis of Search Decision Making Using Probabilistic Search Strategies

https://authors.library.caltech.edu/records/9vjfy-2rz48

3

Group Testing with Probabilistic Tests: Theory, Design and Application

https://arxiv.org/abs/1009.3186

4

The Monty Hall Problem

https://www.eg.bucknell.edu/~kozick/elec47103/montyhall/MontyHallProblem.htm

1. Verdict: the formula is correct—with a small indexing correction

Assume 
𝑁
≥
1
N≥1, 
0
≤
𝑓
≤
1
0≤f≤1, 
𝑘
k distinct candidates are tested, the outcomes are observed, and you must choose one candidate using ordinary 0–1 accuracy. Write 
𝑞
=
1
−
𝑓
q=1−f, the chance a non-expert passes.

The Bayes rule is simple: if anyone tested passes, choose a passing tested candidate; if none pass, choose an untested candidate. To see why, with 
𝑝
p tested passers and 
𝑟
r failures, a tested passer has likelihood 
𝑞
𝑝
−
1
𝑓
𝑟
q
p−1
f
r
 under the hypothesis that they are the expert, while an untested candidate has likelihood 
𝑞
𝑝
𝑓
𝑟
q
p
f
r
. Failed candidates are impossible experts. Ties can be broken arbitrarily.

For 
1
≤
𝑘
<
𝑁
1≤k<N, split on whether the expert is among the tested candidates:

If so, which has probability 
𝑘
/
𝑁
k/N, the number 
𝑋
X of false passers is 
B
i
n
o
m
i
a
l
(
𝑘
−
1
,
𝑞
)
Binomial(k−1,q). Choosing among the expert and those false passers succeeds with probability 
𝐸
[
1
/
(
1
+
𝑋
)
]
E[1/(1+X)].
If the expert is untested, you can be correct only when all 
𝑘
k tested non-experts fail, probability 
𝑓
𝑘
f
k
. Then you choose among 
𝑁
−
𝑘
N−k untested candidates.

The useful identity is

𝐸
 ⁣
[
1
1
+
𝑋
]
=
∫
0
1
(
𝑓
+
𝑞
𝑡
)
𝑘
−
1
 
𝑑
𝑡
=
1
𝑘
∑
𝑗
=
0
𝑘
−
1
𝑓
𝑗
.
E[
1+X
1
	​

]=∫
0
1
	​

(f+qt)
k−1
dt=
k
1
	​

j=0
∑
k−1
	​

f
j
.

Therefore

𝐴
𝑘
=
𝑘
𝑁
⋅
1
𝑘
∑
𝑗
=
0
𝑘
−
1
𝑓
𝑗
+
𝑁
−
𝑘
𝑁
⋅
𝑓
𝑘
𝑁
−
𝑘
=
1
𝑁
∑
𝑗
=
0
𝑘
𝑓
𝑗
.
A
k
	​

=
N
k
	​

⋅
k
1
	​

j=0
∑
k−1
	​

f
j
+
N
N−k
	​

⋅
N−k
f
k
	​

=
N
1
	​

j=0
∑
k
	​

f
j
.

For 
𝑘
=
𝑁
k=N, everyone is tested and the first term alone gives

𝐴
𝑁
=
1
𝑁
∑
𝑗
=
0
𝑁
−
1
𝑓
𝑗
.
A
N
	​

=
N
1
	​

j=0
∑
N−1
	​

f
j
.

So, yes:

𝐴
𝑘
=
1
𝑁
∑
𝑗
=
0
min
⁡
(
𝑘
,
𝑁
−
1
)
𝑓
𝑗
.
A
k
	​

=
N
1
	​

j=0
∑
min(k,N−1)
	​

f
j
.
	​


Indexing correction: the 
𝑟
r-th test added, for 
1
≤
𝑟
≤
𝑁
−
1
1≤r≤N−1, gains 
𝑓
𝑟
/
𝑁
f
r
/N. Equivalently, going from 
𝑘
k tests to 
𝑘
+
1
k+1 tests gains 
𝑓
𝑘
+
1
/
𝑁
f
k+1
/N, not 
𝑓
𝑘
/
𝑁
f
k
/N. The 
𝑁
Nth test gains zero. Also, “every test before the last helps” is strict only when 
𝑓
>
0
f>0; at 
𝑓
=
0
f=0, non-experts always pass and no test helps.

2. Why the last test has zero value

This is stronger than an ex-ante cancellation: conditional on any possible first 
𝑁
−
1
N−1 outcomes, the final test does not improve the expected probability of a correct single choice.

Suppose 
𝑝
≥
1
p≥1 of the first 
𝑁
−
1
N−1 candidates passed. The posterior weights are proportional to

1
1 for each of those 
𝑝
p passers;
𝑞
=
1
−
𝑓
q=1−f for the one untested candidate.

So the best current success probability is 
1
/
(
𝑝
+
𝑞
)
1/(p+q).

Now test the untested candidate:

It passes with probability 
𝑞
(
𝑝
+
1
)
/
(
𝑝
+
𝑞
)
q(p+1)/(p+q). Then the 
𝑝
+
1
p+1 passers tie, giving success probability 
1
/
(
𝑝
+
1
)
1/(p+1).
It fails with probability 
𝑝
𝑓
/
(
𝑝
+
𝑞
)
pf/(p+q). Then the 
𝑝
p earlier passers tie, giving success probability 
1
/
𝑝
1/p.

The expected success probability afterward is

𝑞
(
𝑝
+
1
)
𝑝
+
𝑞
1
𝑝
+
1
+
𝑝
𝑓
𝑝
+
𝑞
1
𝑝
=
𝑞
+
𝑓
𝑝
+
𝑞
=
1
𝑝
+
𝑞
.
p+q
q(p+1)
	​

p+1
1
	​

+
p+q
pf
	​

p
1
	​

=
p+q
q+f
	​

=
p+q
1
	​

.

Unchanged. If none of the first 
𝑁
−
1
N−1 passed, the last candidate is already known to be the expert, so testing them is redundant.

The last test does change the posterior; it simply has zero value for this particular objective—maximizing the chance of one correct guess.

Cheat-sheet equivalence: true only if the chooser knows who was helped

Suppose all 
𝑁
N candidates are tested, and 
𝑐
≥
1
c≥1 known candidates are guaranteed to pass. Put 
𝑛
=
𝑁
−
𝑐
n=N−c, the number of ordinary candidates. The expert being ordinary contributes 
1
𝑁
∑
𝑗
=
0
𝑛
−
1
𝑓
𝑗
N
1
	​

∑
j=0
n−1
	​

f
j
 to accuracy; the expert being among the protected candidates contributes 
𝑓
𝑛
/
𝑁
f
n
/N. Thus

𝐴
(
𝑐
)
=
1
𝑁
∑
𝑗
=
0
𝑁
−
𝑐
𝑓
𝑗
.
A
(c)
=
N
1
	​

j=0
∑
N−c
	​

f
j
.

One known cheat-sheet recipient therefore costs nothing relative to testing everyone normally:

𝐴
(
1
)
=
𝐴
(
0
)
=
1
𝑁
∑
𝑗
=
0
𝑁
−
1
𝑓
𝑗
.
A
(1)
=A
(0)
=
N
1
	​

j=0
∑
N−1
	​

f
j
.

Two known recipients reduce accuracy by exactly

𝐴
(
1
)
−
𝐴
(
2
)
=
𝑓
𝑁
−
1
𝑁
.
A
(1)
−A
(2)
=
N
f
N−1
	​

.

But “secretly” is dangerous wording. If the chooser does not know who got the cheat sheet, the equivalence fails. For 
𝑁
=
2
N=2, with one randomly chosen but hidden cheat-sheet recipient, accuracy is 
1
/
2
+
𝑓
/
4
1/2+f/4, whereas ordinary testing gives 
(
1
+
𝑓
)
/
2
(1+f)/2. The hidden cheat sheet costs 
𝑓
/
4
f/4. So your equivalence requires the protected identity to be known to the decision-maker (though it may be secret from the candidates).

3. Is it already known?

I did not find a source I can verify as stating this exact fixed-
𝑘
k formula or the conditional zero-value result. That is not evidence that no such source exists; there is a particularly close lead that should be checked before making any novelty claim.

Closest lead: Optimal discrete search with imperfect specificity, Mathematical Methods of Operations Research 68(3) (2008). The title sounds directly relevant to false-positive passes, and it is listed among related search-theory works. I could not inspect its full text, so I cannot honestly say whether it contains your exact result. 
1
Overlook-probability search: Ingo Wegener, “The Discrete Sequential Search Problem with Nonrandom Cost and Overlook Probabilities,” Mathematics of Operations Research 5(3) (1980), 373–380, studies sequential search for an object with imperfect detection and search costs. Hall also published “Sequential Search with Random Overlook Probabilities” (1976) and “Strongly Optimal Policies in Sequential Search with Random Overlook Probabilities” (1977). These are close in vocabulary, but the overlook setup is not the same as a perfectly passing expert amid false-positive non-experts. 
1
Bayesian search with false alarms: Timothy H. Chung and Joel W. Burdick, “Analysis of Search Decision Making Using Probabilistic Search Strategies,” IEEE Transactions on Robotics 28(1) (2012), 132–144, derives Bayesian updates with false-positive and false-negative detections. Its search-and-decision objective is broader than this exact uniform, one-expert, fixed-number-of-tests problem. 
2
Group testing: Mahdi Cheraghchi, Ali Hormati, Amin Karbasi, and Martin Vetterli, “Group Testing with Probabilistic Tests: Theory, Design and Application” (2010), studies pooled tests and recovery of defective sets with probabilistic testing. Related field, different observation and decoding problem. 
3
Monty Hall / “protected door”: Only a loose analogy. Monty’s informed, rule-governed choice of which door to open is central to that problem; here the outcomes are independent noisy tests. Leaving one candidate untested is not by itself a proof of zero value—the posterior tradeoff above is. 
4

A useful additional label for searching is MAP decoding of a one-hot vector through an asymmetric (reverse-Z) channel. But I do not have a verified coding-theory citation for this exact accuracy identity.

4. Counterintuitiveness: 4/5

A noisy test sounds like it should help. The surprise is that it can change beliefs substantially yet leave the best single-guess accuracy exactly unchanged. I’d stop short of 5/5 because the posterior-weight cancellation is clean once written down.

Ассистент B
Sources

1

Arxiv

https://arxiv.org/pdf/2311.18226

2

Bayesian search theory - Wikipedia

https://en.wikipedia.org/wiki/Bayesian_search_theory

3

Apps

https://apps.dtic.mil/sti/pdfs/AD0649850.pdf

4

Binary search—think positive | Journal of Functional Programming | Cambridge Core

https://www.cambridge.org/core/journals/journal-of-functional-programming/article/binary-searchthink-positive/1F974DF9C6475D19B32E18C93A2DCC1C

5

Faculty

https://faculty.law.harvard.edu/steven-shavell/wp-content/uploads/sites/23/2024/10/3_Theory.pdf

6

A Review of Minimum Cost Box Searching Games

https://arxiv.org/html/2502.10551v2

7

Econ

https://econ.berkeley.edu/sites/default/files/Viswanathan_Anirudh_F18%20Honors%20Thesis.pdf

8

On the true detection probability of the uniformly optimal search plan

https://arxiv.org/html/2311.18226v4

9

Optimum sequential search with discrete locations and random

https://ideas.repec.org/a/wly/navlog/v18y1971i2p159-167.html

10

Apps

https://apps.dtic.mil/sti/pdfs/ADA063845.pdf

11

Towardsdatascience

https://towardsdatascience.com/bayesian-thinking-for-people-who-hated-statistics/

12

Arxiv

https://arxiv.org/pdf/1710.09461

13

Image-ppubs

https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8732222

14

Arxiv

https://arxiv.org/pdf/1312.0451

15

Arxiv

https://arxiv.org/pdf/2608.14326

16

Stat

https://www.stat.cmu.edu/~larry/=sml/Bayes.pdf

17

Introduction to Bayesian Search - A Simple 1D Example — Stone Soup 1.8 documentation

https://stonesoup.readthedocs.io/en/v1.8/auto_examples/sensormanagement/bayesian_search_example_1.html

18

Bayesian search: A simple rule to find stuff you've lost

https://bigthink.com/smart-skills/bayesian-search-find-stuff-lost/

19

Bayesian Search Models | R-bloggers

https://www.r-bloggers.com/2014/03/bayesian-search-models/

20

Www2

https://www2.stat.duke.edu/~banks/130-labs.dir/lab10.dir/Lab10_bayesian_search.pdf

This is a good problem to pressure-test. Let me verify the math carefully and check the literature before rendering a verdict.
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
# Referee Report

1. Verification of the formula

Verdict: correct, after I derive it independently rather than trust the claim at face value.

Set up the Bayes posterior explicitly. Candidates 
1
,
…
,
𝑁
1,…,N, expert 
𝐸
E uniform. Test a fixed subset 
𝑆
S, 
∣
𝑆
∣
=
𝑘
∣S∣=k. Non-experts fail i.i.d. with probability 
𝑓
f; the expert never fails. Suppose 
𝑚
m of the 
𝑘
k tested candidates pass.

Any tested candidate who failed has posterior probability exactly 0 (expert never fails) — this part is trivial and uncontroversial.
For a tested candidate who passed, the likelihood of the data given they are the expert is 
(
1
−
𝑓
)
𝑚
−
1
𝑓
𝑘
−
𝑚
(1−f)
m−1
f
k−m
 (the other 
𝑚
−
1
m−1 passers are lucky non‑experts).
For an untested candidate, the likelihood of the data given they are the expert is 
(
1
−
𝑓
)
𝑚
𝑓
𝑘
−
𝑚
(1−f)
m
f
k−m
 (all 
𝑚
m passers among 
𝑆
S are now lucky non‑experts).

Since 
(
1
−
𝑓
)
𝑚
−
1
>
(
1
−
𝑓
)
𝑚
(1−f)
m−1
>(1−f)
m
, every passer in 
𝑆
S strictly dominates every untested candidate in posterior mass — so the Bayes‑optimal rule is: if anyone passed, guess uniformly among the passers; if everyone failed, guess uniformly among the untested pool.

Computing accuracy under this rule by splitting on whether the true expert was in 
𝑆
S:

If expert 
∈
𝑆
∈S (prob 
𝑘
/
𝑁
k/N): 
𝑚
=
1
+
Bin
(
𝑘
−
1
,
1
−
𝑓
)
m=1+Bin(k−1,1−f), and correctness probability is 
𝐸
[
1
/
𝑚
]
E[1/m]. Using the standard identity 
𝐸
[
1
/
(
𝑌
+
1
)
]
=
1
−
(
1
−
𝑝
)
𝑛
+
1
(
𝑛
+
1
)
𝑝
E[1/(Y+1)]=
(n+1)p
1−(1−p)
n+1
	​

 for 
𝑌
∼
Bin
(
𝑛
,
𝑝
)
Y∼Bin(n,p), this term contributes exactly 
(
1
+
𝑓
+
⋯
+
𝑓
𝑘
−
1
)
/
𝑁
(1+f+⋯+f
k−1
)/N.
If expert 
∉
𝑆
∈
/
S (prob 
(
𝑁
−
𝑘
)
/
𝑁
(N−k)/N): correct only if all 
𝑘
k tested fail (prob 
𝑓
𝑘
f
k
), then guessing uniformly among 
𝑁
−
𝑘
N−k untested gives accuracy 
1
/
(
𝑁
−
𝑘
)
1/(N−k) — and the 
(
𝑁
−
𝑘
)
(N−k) factors cancel exactly, leaving a contribution of 
𝑓
𝑘
/
𝑁
f
k
/N.

Summing: 
𝑃
(
correct
)
=
1
𝑁
(
1
+
𝑓
+
⋯
+
𝑓
𝑘
−
1
+
𝑓
𝑘
)
P(correct)=
N
1
	​

(1+f+⋯+f
k−1
+f
k
), capped at 
𝑘
=
𝑁
−
1
k=N−1 since beyond that there's no untested fallback pool left (at 
𝑘
=
𝑁
k=N, the derivation collapses entirely into the first case and reproduces the same sum up to 
𝑓
𝑁
−
1
f
N−1
). I checked this by hand for 
𝑘
=
1
,
2
,
3
k=1,2,3 and for 
𝑁
=
2
N=2 (both 
𝑘
=
1
k=1 and 
𝑘
=
2
k=2), and all match the closed form. The extreme case 
𝑓
=
1
f=1 (perfect test) gives 
𝑃
=
min
⁡
(
𝑘
+
1
,
𝑁
)
/
𝑁
P=min(k+1,N)/N, i.e. certainty already at 
𝑘
=
𝑁
−
1
k=N−1 — the obvious "last locker" case — which is a useful sanity check that the general claim is just the noisy generalization of an extreme case that's already intuitively obvious.

So: formula verified, contingent on the (reasonable, implicit) tie-breaking convention that ties in posterior are broken uniformly at random among the tied candidates. If you break ties adversarially or using side information, the number shifts — the claim should be stated with that caveat.

2. Cleanest intuitive proof

Don't do the algebra above for intuition — use elimination + a cancellation identity.

Step A (the trivial part, this is not the interesting content): If you've tested 
𝑁
−
1
N−1 candidates and all failed, logic alone (no test needed) certifies the untested $N$th is the expert — and since they are the expert, testing them would return "pass" with probability 1, so the test is deterministically uninformative in this branch. This is the ordinary "last locker" fact and is not surprising.

Step B (the actual content): The surprising part is that this zero-information branch exactly cancels what you'd otherwise think is new information in the other branch. If at least one of the first 
𝑁
−
1
N−1 passed, you already point at the (tied) set of passers. Testing the $N$th candidate now either (i) reveals they're a non-expert (prob 
𝑓
f), costing nothing since you already weren't going to guess an untested wildcard over an actual passer, or (ii) reveals they pass (prob 
1
−
𝑓
1−f), which could be the real expert now newly caught — a gain — but if the real expert was already among the earlier passers, adding a tied rival to the passer pool dilutes your chance of pointing at the correct one by exactly the same amount. The identity 
𝑁
−
𝑘
𝑁
⋅
1
𝑁
−
𝑘
=
1
𝑁
N
N−k
	​

⋅
N−k
1
	​

=
N
1
	​

 is the compact statement of why "ignorance about 
𝑈
U exchangeable candidates" always contributes exactly 
1
/
𝑁
1/N times the probability that this branch occurs (times 
𝑓
𝑘
f
k
), independent of 
𝑈
U itself — so the fallback-certainty mechanism contributes identically whether 
𝑈
=
1
U=1 or 
𝑈
=
37
U=37; it is only killed off entirely, with no replacement, when 
𝑈
U hits 
0
0 (testing the very last one). That exact cancellation — not the elimination logic itself — is the non-obvious engine of the result.

3. Is this already known?

I searched specifically for this, and I'll be straight with you: I did not find a source giving this exact closed-form result (geometric-sum accuracy, with the last term contributing exactly zero, for one-sided-error candidate testing). What I can say honestly:

The "last box" / elimination principle (if you've eliminated all-but-one location, the last is free) is folklore in logic and goes back implicitly to classical search-theory and detection-theory treatments, e.g. the "object hidden in one of 
𝑛
n boxes" framework studied by Koopman and formalized via Bayesian updating in Bayesian search theory, where 
2
a stationary object is hidden in one of n boxes (locations) and probabilities are revised via 
2
Bayes' theorem as searches come up empty. But classical search theory (Koopman onward) almost always assumes a symmetric overlook/false-negative probability — 
6
detection may be imperfect, so that there is a certain probability that a target may not be found when a box is searched, even when it is there — which is the opposite error structure from your one-sided model (your "expert" box can never be missed; the noise is all on the false-positive side). I don't know of a standard search-theory paper with exactly your error structure and this exact geometric-series identity.
Kadane's classical paper on discrete search with "overlook probability" 
𝛼
𝑘
α
k
	​

 per box is the closest classical framework in spirit (sequential testing, Bayes-optimal ordering, cost per search) but again uses symmetric miss probabilities, not a guaranteed-pass expert.
I am not aware of this exact "every test helps except the last one, by exactly zero" statement appearing named in the literature on 20-questions-with-liars, group testing, or multi-armed bandits — group testing (Dorfman-style) typically pools multiple candidates per test and optimizes test count for guaranteed identification, which is a different objective than your Bayes-optimal single-guess accuracy.
It smells structurally like a Bloom-filter-style one-sided-error argument (guaranteed true positive, possible false positive) combined with a conservation-of-probability-mass identity, which is a flavor one sees in Bayesian "value of information" arguments (the general theorem that a Bayes-rational agent's expected posterior accuracy is a specific martingale), but I don't have a named citation for the specific closed form.

Bottom line for task 3: I cannot honestly attribute this exact formula to a specific named result or paper. The elimination logic is old and folkloric; the precise geometric-series accuracy formula with an exact zero at step 
𝑁
N for a noisy one-sided test looks to me like a fresh (if not deep) derivation, and you should treat any claim that it's "well known" with skepticism unless someone produces a citation. I'd welcome being proven wrong, but I won't manufacture a reference I can't verify.

4. How counterintuitive, 1–5

4/5. The reason it's not a 5: once you say the phrase "if everyone else failed, you already know who's left," most people immediately agree with Step A. The reason it's not a 2 or 3: almost nobody immediately buys that this cancels the apparent new Bayesian evidence exactly, to the penny, even when the test is noisy and even when the n-th test passes (which "feels" like it should always be at least weakly informative). People have a very strong prior that "any test with 
𝑓
>
0
f>0 must have positive marginal value," because under naive intuition a noisy signal always shifts beliefs. The fact that the marginal value is a clean, provable exact zero at a predictable, fixed index (
𝑘
=
𝑁
k=N, not asymptotically) rather than merely "small" is the part that trips up practiced Bayesians, not just laypeople.

Act as a harsh referee. Claim: N candidates, exactly one 'expert' uniformly at random. A test has one-sided error: the expert always passes, each non-expert passes independently with probability 1-f. If you test k candidates and then choose Bayes-optimally, P(correct) = (1/N)(1 + f + f^2 + ... + f^min(k,N-1)). Hence every additional test helps (by f^k/N) EXCEPT the last one, which adds exactly zero even though the test is noisy. Equivalently: you may secretly give one candidate a cheat sheet (guaranteed pass) at zero cost to accuracy, but helping two costs f^(N-1)/N. Tasks: (1) verify or refute the formula; (2) give the cleanest intuitive proof; (3) is this result already known (search theory with overlook probability, group testing, Bayesian search, 'last box' arguments, Monty Hall protected door)? Name precise sources if you know them, and say honestly if you don't; (4) rate how counterintuitive it is for ordinary people, 1-5.

A лучше
Оба хорошие
Оба плохие
B лучше

Battle

Battle ModeBattle 2 anonymous models
Agent ModeBuilt for complex tasks
Side by SideCompare 2 models of your choice
DirectChat with 1 model at a time
Web Search

Inputs are processed by third-party AI and responses may be inaccurate.
