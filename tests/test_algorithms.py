from advanced_string_algorithms import (
    exact_match,
    approximate_match,
    lcp_array,
    rabin_karp_match,
    miller_rabin,
    mod_exp,
)


def naive_lcp_array(text: str) -> list[int]:
    s = text + "$"
    suffixes = sorted(range(len(s)), key=lambda i: s[i:])
    out = [0]
    for a, b in zip(suffixes, suffixes[1:]):
        k = 0
        while a + k < len(s) and b + k < len(s) and s[a + k] == s[b + k]:
            k += 1
        out.append(k)
    return out


def test_z_exact_match():
    assert exact_match("bananabanana", "ana") == [1, 3, 7, 9]
    assert exact_match("abcdef", "xyz") == []
    assert exact_match("abc", "") == [0, 1, 2, 3]
    assert exact_match("abc", "abcd") == []


def test_rabin_karp():
    assert rabin_karp_match("abracadabra", "abra") == [0, 7]
    assert rabin_karp_match("aaaaa", "aa") == [0, 1, 2, 3]


def test_mod_exp_and_miller_rabin():
    assert mod_exp(7, 128, 13) == pow(7, 128, 13)
    for p in [2, 3, 5, 97, 7919]:
        assert miller_rabin(p, 20)
    for n in [4, 9, 21, 561, 1105]:
        assert not miller_rabin(n, 20)


def test_suffix_tree_lcp():
    for text in ["banana", "mississippi", "aaaa", "abcab"]:
        assert lcp_array(text) == naive_lcp_array(text)


def test_bwt_exact_and_single_edit_cases():
    exact = approximate_match("the quick brown fox", "quick")
    assert exact.get(4) == 0

    substitution = approximate_match("the quack brown fox", "quick")
    assert substitution.get(4) == 1

    insertion = approximate_match("the quiick brown fox", "quick")
    assert insertion.get(4) == 1

    deletion = approximate_match("the quck brown fox", "quick")
    assert deletion.get(4) == 1

    transposition = approximate_match("the qiuck brown fox", "quick")
    assert transposition.get(4) == 1
