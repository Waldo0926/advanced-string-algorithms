# Advanced String Algorithms in Python

[![Status](https://img.shields.io/badge/status-portfolio%20project-475569?style=for-the-badge)]()
[![Tests](https://img.shields.io/badge/tests-pytest-2ea44f?style=for-the-badge)]()
[![License](https://img.shields.io/badge/license-MIT-1e5eff?style=for-the-badge)](LICENSE)

**English** · [简体中文](README.zh-CN.md)

A compact portfolio of advanced string-processing algorithms implemented in
pure Python: **Z-based exact matching, BWT-backed approximate matching,
Ukkonen suffix trees with LCP extraction, and Rabin-Karp with Miller-Rabin
prime generation**.

This repository is a cleaned and refactored showcase derived from completed
advanced-algorithms coursework. It intentionally excludes assignment
specifications, marking feedback, reports, student identifiers, revision
materials, and other course resources.

## Why this project

String algorithms are a good way to demonstrate more than basic data
structures. The implementations here exercise preprocessing, indexing,
probabilistic algorithms, recursion/state-space pruning, suffix structures,
rolling hashes, complexity analysis, and careful boundary handling.

## Included algorithms

| Module | Technique | Highlights |
| --- | --- | --- |
| `z_match.py` | Z-suffix + right-to-left exact matching | shift preprocessing, Galil-style skip frontier |
| `bwt_approx.py` | BWT / backward search | distance ≤ 1 via substitution, insertion, deletion, transposition |
| `suffix_tree_lcp.py` | Ukkonen suffix tree | active point, suffix links, skip/count, LCP extraction |
| `rabin_karp_prime.py` | Rabin-Karp | Miller-Rabin, modular exponentiation, rolling hash |

## Quick start

```bash
git clone https://github.com/Waldo0926/advanced-string-algorithms.git
cd advanced-string-algorithms

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"
pytest -q
python examples/demo.py
```

## Example

```python
from advanced_string_algorithms import (
exact_match,
approximate_match,
lcp_array,
rabin_karp_match,
)

print(exact_match("bananabanana", "ana"))
# [1, 3, 7, 9]

print(rabin_karp_match("abracadabra", "abra"))
# [0, 7]

print(lcp_array("banana"))
# LCP array in suffix-array order

print(approximate_match("the quack brown fox", "quick"))
# includes position 4 with edit distance 1
```

## Repository structure

```text
advanced-string-algorithms/
├── src/advanced_string_algorithms/
│ ├── __init__.py
│ ├── z_match.py
│ ├── bwt_approx.py
│ ├── suffix_tree_lcp.py
│ └── rabin_karp_prime.py
├── tests/
│ └── test_algorithms.py
├── examples/
│ └── demo.py
├── ALGORITHMS.md
├── pyproject.toml
└── README.zh-CN.md
```

## Complexity notes

The algorithms intentionally mirror the ideas being demonstrated, rather than
hiding them behind third-party packages.

- **Z-style matcher:** preprocessing includes an `O(m²)` shift table in this
implementation; the search uses a skip frontier to avoid redundant suffix
comparisons.
- **BWT matcher:** BWT backward steps are constant-time after the occurrence
table is built; the showcase uses a deliberately simple suffix-array
constructor, so index construction is not production-optimized.
- **Suffix tree:** Ukkonen construction uses suffix links and skip/count;
LCP extraction is a linear traversal of the finished tree.
- **Rabin-Karp:** rolling-window updates are `O(1)` per shift after hashing,
with direct verification on hash matches.

See [ALGORITHMS.md](ALGORITHMS.md) for the implementation notes.

## Testing

The test suite covers exact matching, all four single-edit cases in the BWT
matcher, Miller-Rabin prime/composite checks, rolling-hash matching, and LCP
results cross-checked against a naive reference implementation.

```bash
pytest -q
```

## Coursework provenance

The underlying ideas and initial implementations originated in completed
university coursework and were later reorganized into this standalone
portfolio repository. No assignment brief, official solution, marking
material, or private course resource is included.

This repository is intended to demonstrate my implementation and algorithmic
reasoning, not to distribute course assessment material.

## License

MIT
