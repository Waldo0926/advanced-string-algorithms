"""Burrows-Wheeler-transform based approximate pattern matching.

Supports a single edit: substitution, insertion, deletion, or adjacent
transposition. The suffix-array builder is intentionally simple because this
repository focuses on the BWT search logic rather than suffix-array engineering.
"""

TERM = "$"

def build_sa(s):
    """
    Pair every suffix with its start index, then sort these pairs.
    sa[i] = start index of the i-th smallest suffix.

    Time : O(n^2 log n)
    Space: O(n^2)
    """
    n = len(s)
    # tuples sort by first element (the suffix), which is what we want
    pairs = [(s[i:], i) for i in range(n)]
    pairs.sort()
    return [p[1] for p in pairs]


def build_bwt(s, sa):
    """
    BWT[i] = char that cyclically precedes the i-th sorted suffix.
        (1) sa[i] >  0, s[sa[i] - 1]
        (2) sa[i] == 0, s[n-1] (cyclic wrap, which is '$' here)

    Time : O(n)
    Space: O(n)
    """
    n = len(s)
    out = []
    for i in range(n):
        if sa[i] == 0:
            out.append(s[n - 1])  # wrap around
        else:
            out.append(s[sa[i] - 1])
    return ''.join(out)


def build_rank(bwt):
    """
    rank[c] stores where character c first appears in the sorted first column F.
    Since F is just the sorted BWT column, I only count the characters in BWT
    and then take cumulative counts in ASCII order.
    '$' comes before all input characters because the input alphabet starts at
    ASCII 37, while '$' is ASCII 36.

    Time : O(n + sigma log sigma)

    Space: O(sigma)
    """
    cnt = {}
    for c in bwt:
        cnt[c] = cnt.get(c, 0) + 1

    alpha = sorted(cnt.keys())  # sigma in ASCII order

    rank = {}
    cum = 0
    for c in alpha:
        rank[c] = cum
        cum += cnt[c]
    return rank, alpha


def build_nocc(bwt, alpha):
    """
    nocc[i][cidx] = number of times alpha[cidx] occurs in BWT[0..i-1]
    (exclusive of position i). Rows go i = 0..n, total n+1 rows.

    With this convention the LF-mapping update used here lecture reads:
        (1) sp' = rank[x] + nocc[sp][cidx]
        (2) ep' = rank[x] + nocc[ep + 1][cidx] - 1

    Time : O(n * sigma)
    Space: O(n * sigma)
    """
    n = len(bwt)
    sigma = len(alpha)
    c2i = {c: i for i, c in enumerate(alpha)}

    # (n+1) x sigma matrix
    nocc = [[0] * sigma for _ in range(n + 1)]

    for i in range(n):
        prev = nocc[i]
        curr = nocc[i + 1]
        # copy previous row, then bump BWT[i]
        for k in range(sigma):
            curr[k] = prev[k]
        curr[c2i[bwt[i]]] += 1

    return nocc, c2i


def lf_extend(sp, ep, x, rank, nocc, c2i):
    """
    Prepend x to the matched string and return the new suffix-array range.
    If x is not in the BWT alphabet, or the range collapses, return an empty
    range (sp > ep) so the caller can prune this branch.

    Time: O(1)
    """
    if x not in c2i or x not in rank:
        return 1, 0  # sp > ep means empty
    ci = c2i[x]
    new_sp = rank[x] + nocc[sp][ci]
    new_ep = rank[x] + nocc[ep + 1][ci] - 1
    return new_sp, new_ep


def bwt_search_d1(pat, sa, bwt, rank, nocc, c2i, alpha):
    """
    Search for matches with edit distance at most 1 using the BWT index.
    It starts from the full suffix-array range [0, n-1]. The search is still
    a normal backward search, but I keep one extra flag for whether the
    single edit has already been used.

    State used in dfs(i, sp, ep, errs, ext):
        i      next pattern index to match, moving from right to left
        sp, ep current suffix-array range for the string matched so far
        errs   number of edits already used, either 0 or 1
        ext    number of text characters matched so far

    When no edit has been used yet, the recursion also tries the four
    distance-1 cases: substitution, insertion, deletion and adjacent
    transposition. After one edit is used, the remaining characters must
    match exactly.

    The ext value is only used to avoid recording the empty match that can
    happen when m == 1 and the only pattern character is deleted.

    Returns a dictionary mapping 0-based text positions to the best distance
    found at that position.


    """
    n = len(bwt)         # length of (text + '$')
    m = len(pat)
    found = {}

    # helper: record SA[sp..ep] positions with this distance
    def record(sp, ep, d):
        if sp > ep:
            return
        for k in range(sp, ep + 1):
            pos = sa[k]
            if pos == n - 1:
                continue  # the lone '$' suffix, not a real text position
            old = found.get(pos)
            if old is None or d < old:
                found[pos] = d

    # recursion
    def dfs(i, sp, ep, errs, ext):
        if sp > ep:
            return  # range gone, prune

        # base case: walked past the left end of pat
        if i < 0:
            if ext >= 1:                  # drop the m==1 deletion degenerate
                record(sp, ep, errs)

            # spare budget can be used as a "leftmost insertion": text has
            # one extra char to the left of where pat was placed.
            if errs == 0:
                for x in alpha:
                    if x == TERM:
                        continue
                    nsp, nep = lf_extend(sp, ep, x, rank, nocc, c2i)
                    if nsp <= nep:
                        record(nsp, nep, 1)
            return

        c = pat[i]

        # A: exact extension with pat[i], always allowed
        nsp, nep = lf_extend(sp, ep, c, rank, nocc, c2i)
        dfs(i - 1, nsp, nep, errs, ext + 1)

        # edit budget has been used, so only exact extension is allowed
        if errs >= 1:
            return

        # B: substitution at i, try every other alphabet char
        for x in alpha:
            if x == c or x == TERM:
                continue
            nsp, nep = lf_extend(sp, ep, x, rank, nocc, c2i)
            dfs(i - 1, nsp, nep, 1, ext + 1)

        # C: insertion, text has 1 extra char here
        # extend by some x but keep pat index unchanged
        for x in alpha:
            if x == TERM:
                continue
            nsp, nep = lf_extend(sp, ep, x, rank, nocc, c2i)
            dfs(i, nsp, nep, 1, ext + 1)

        # D: deletion, drop pat[i], no extension 
        dfs(i - 1, sp, ep, 1, ext)

        # E: transposition of pat[i-1] and pat[i] (adjacent, distinct)
        # reading the matched text right to left we should now see pat[i-1]
        # at position i and pat[i] at position i-1, so left extend by
        # pat[i-1] first then pat[i], then jump to i-2.
        if i >= 1 and pat[i] != pat[i - 1]:
            sp1, ep1 = lf_extend(sp, ep, pat[i - 1], rank, nocc, c2i)
            if sp1 <= ep1:
                sp2, ep2 = lf_extend(sp1, ep1, pat[i], rank, nocc, c2i)
                dfs(i - 2, sp2, ep2, 1, ext + 2)

    dfs(m - 1, 0, n - 1, 0, 0)
    return found

def approximate_match(text: str, pattern: str) -> dict[int, int]:
    """Return {0-based text position: distance} for matches with distance <= 1."""
    if TERM in text or TERM in pattern:
        raise ValueError("Input must not contain the terminal symbol '$'.")
    indexed = text + TERM
    sa = build_sa(indexed)
    bwt = build_bwt(indexed, sa)
    rank, alpha = build_rank(bwt)
    nocc, c2i = build_nocc(bwt, alpha)
    return bwt_search_d1(pattern, sa, bwt, rank, nocc, c2i, alpha)
