"""Analyze completed first answers; never replace blanks with wrong answers."""
import csv
import sys
from pathlib import Path
from fractions import Fraction as F
from corrected_chest_pilot_20261021 import binomial_tail, clopper_pearson


def main():
    root = Path(__file__).resolve().parents[1]/'research/pilot-chest-40'
    path = Path(sys.argv[1]) if len(sys.argv)>1 else root/'responses.csv'
    with (root/'assignment.csv').open(encoding='utf-8-sig', newline='') as stream:
        assignments = {r['participant_id']:r['version'] for r in csv.DictReader(stream)}
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    seen = set()
    data = {'A':[], 'B':[]}
    for row in rows:
        pid = row['participant_id']
        if pid in seen or pid not in assignments or assignments[pid] != row['version']:
            raise ValueError(f'Duplicate, unassigned ID or changed version: {pid}')
        seen.add(pid)
        choice = row['choice'].strip()
        if not choice:
            continue
        if choice not in {'own','other','equal','unknown'}:
            raise ValueError(f'Invalid choice: {pid}')
        row['choice'] = choice
        confidence = row['confidence'].strip()
        row['confidence_value'] = float(confidence) if confidence else None
        if row['confidence_value'] is not None and not 0 <= row['confidence_value'] <= 100:
            raise ValueError(f'Invalid confidence: {pid}')
        data[row['version']].append(row)
    counts = {v:len(group) for v,group in data.items()}
    print('Completed first answers:', counts)
    if counts != {'A':20, 'B':20}:
        print('Pilot incomplete. No interim significance test; blank responses are missing.')
        return
    for version, group in data.items():
        choices = {c:sum(r['choice']==c for r in group) for c in ('own','other','equal','unknown')}
        print(version, choices)
    k = sum(r['choice']=='other' for r in data['A'])
    print('Primary predicted error in A:', k, '/20; 95% exact interval:', clopper_pearson(20,k))
    print('One-sided exact p, preselected H0:p<=.25:', float(binomial_tail(20,k,F(1,4))))
    high = sum(r['choice']=='other' and r['confidence_value'] is not None and r['confidence_value']>=80 for r in data['A'])
    missing_confidence = sum(r['confidence_value'] is None for r in data['A'])
    print('High-confidence predicted errors in A:', high, '/20; missing confidence:', missing_confidence)
    correct_control = sum(r['choice']=='other' for r in data['B'])
    print('Correct control B:', correct_control, '/20')
    delta = sum(r['choice']=='own' for r in data['A'])/20-sum(r['choice']=='own' for r in data['B'])/20
    print('Exploratory own-choice difference A-B:', delta)
    for version, group in data.items():
        subset = [r for r in group if r['comprehension']=='correct' and r['familiar']=='no' and r['assistance']=='none']
        print('Exploratory understood/unfamiliar/unassisted subset', version, 'n=',len(subset),
              'other=',sum(r['choice']=='other' for r in subset))
    print('Explanation coding and interpretation remain separate; no automatic causal diagnosis.')


if __name__ == '__main__':
    main()
