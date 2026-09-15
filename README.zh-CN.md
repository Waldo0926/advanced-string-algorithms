# Python 高级字符串算法

[![状态](https://img.shields.io/badge/状态-作品集项目-475569?style=for-the-badge)]()
[![测试](https://img.shields.io/badge/测试-pytest-2ea44f?style=for-the-badge)]()
[![许可证](https://img.shields.io/badge/许可证-MIT-1e5eff?style=for-the-badge)](LICENSE)

[English](README.md) · **中文**

这是一个面向求职作品集整理的高级字符串算法项目，使用纯 Python 实现：
**基于 Z 算法的精确匹配、基于 BWT 的近似匹配、Ukkonen 后缀树与 LCP
数组生成，以及结合 Miller-Rabin 素性测试的 Rabin-Karp 匹配**。

本仓库由已经完成的高级算法课程代码重新整理和重构而来。为了适合作为公开 GitHub 项目，仓库**不包含**作业题目、评分反馈、报告、学号、复习资料、课程 PDF 或其他内部课程资源。

## 为什么值得做成项目

这个项目比普通的“数据结构练习”更能体现算法能力，因为其中涉及：

- 字符串预处理与索引；
- 后缀结构；
- BWT backward search；
- Ukkonen 在线后缀树构建；
- suffix link 与 skip/count；
- 概率素性测试；
- rolling hash；
- 状态空间剪枝；
- 时间与空间复杂度分析。

## 包含的算法

| 模块 | 算法 | 主要技术点 |
| --- | --- | --- |
| `z_match.py` | Z-suffix + 反向精确匹配 | shift table、Galil 风格跳过已验证后缀 |
| `bwt_approx.py` | BWT 近似匹配 | 支持一次替换、插入、删除、相邻换位 |
| `suffix_tree_lcp.py` | Ukkonen 后缀树 | active point、suffix links、skip/count、LCP |
| `rabin_karp_prime.py` | Rabin-Karp | Miller-Rabin、快速模幂、rolling hash |

## 快速运行

```bash
git clone https://github.com/Waldo0926/advanced-string-algorithms.git
cd advanced-string-algorithms

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"
pytest -q
python examples/demo.py
```

## 项目结构

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
└── README.md
```

## 复杂度说明

- **Z 风格匹配器：**当前版本使用 `O(m²)` shift table 预处理，同时通过
skip frontier 避免重复比较已经确认匹配的后缀。
- **BWT 匹配器：**Occurrence table 构建完成后，单次 backward extension
为常数时间；为了突出 BWT 搜索逻辑，本项目中的 suffix array 构建器保持简单实现，并非生产级优化版本。
- **后缀树：**使用 Ukkonen 算法、suffix links 与 skip/count；LCP 数组通过对完成后的树进行线性 DFS 得到。
- **Rabin-Karp：**窗口滑动后的 rolling hash 更新为 `O(1)`，hash 相同时再进行字符级验证。

更多细节见 [ALGORITHMS.md](ALGORITHMS.md)。

## 测试

测试覆盖：

- 精确字符串匹配；
- BWT 匹配中的替换、插入、删除和相邻换位；
- Miller-Rabin 的素数 / 合数判断；
- Rabin-Karp rolling hash；
- 后缀树生成的 LCP 与朴素参考实现交叉验证。

```bash
pytest -q
```

## 课程来源说明

这些算法的最初实现来自已经完成的大学课程作业，之后被重新组织成独立的作品集项目。本仓库不会公开作业题面、官方材料、评分文件或其他课程内部资料。

它的目的，是展示个人的算法实现、复杂度意识和代码组织能力，而不是公开课程评估材料。

## License

MIT
