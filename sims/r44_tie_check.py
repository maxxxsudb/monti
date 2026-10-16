import ast
import itertools
from pathlib import Path

import numpy as np


if __name__ == '__main__':
    tree = ast.parse(Path(__file__).with_name('r44_vertex_lp.py').read_text(encoding='utf-8'))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'vertices')
    scope = {'np': np, 'itertools': itertools}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<vertices>', 'exec'), scope)
    vertices = scope['vertices']
    equal = vertices([1/3]*3, (0, 1, 2), 0.5, 0)
    assert equal and all(np.allclose(p, [1/3]*3) for _, p in equal)
    assert not vertices([1/3]*3, (0, 1, 2), 0.5, 0.1)
    partial = vertices([0.4, 0.4, 0.2], (0, 1, 2), 0.5, 0)
    assert partial and all(abs(p[0]-p[1]) < 1e-8 and p[0] >= p[2]-1e-8 for _, p in partial)
    strict = vertices([0.5, 0.3, 0.2], (0, 1, 2), 0.5, 0.1)
    assert strict and all(max(p) <= 0.5+1e-8 and p[0]-max(p[1:]) >= 0.1-1e-8 for _, p in strict)
    print('PASS: full and partial naive ties; positive margin infeasibility; strict-prior vertices')
