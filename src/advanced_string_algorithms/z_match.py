"""Right-to-left exact pattern matching with Z-suffix preprocessing.

This module is adapted from a completed advanced-algorithms coursework
implementation and refactored as a standalone educational library.
"""

_ASCII_MIN = 37
_SIGMA = 90

def z_algorithm(s):
    """
    Compute the Z-array for string s.
    Z[i] = length of the longest substring starting at s[i] that matches a prefix of s.
    Z[0] = len(s) by convention.

    Keep track of the rightmost Z-box [l, r].
    A. if i > r (outside box): compare from scratch (Case 1)
    B. if i <= r (inside box): use mirror position k = i - l (Case 2)
        1.if Z[k] < r-i+1  then Z[i] = Z[k], done
        2.if Z[k] > r-i+1 then Z[i] = r-i+1, done
        3.if Z[k] == r-i+1 then extend past r manually

    O(n) time, O(n) space.
    """
    n = len(s)
    Z = [0] * n
    Z[0] = n

    l, r = 0, 0  # current rightmost Z-box

    for i in range(1, n):
        if i > r:
            # Case 1: i is outside the box, do naive comparison from scratch
            j = 0
            while i + j < n and s[j] == s[i + j]:
                j += 1
            Z[i] = j
            if j > 0:
                l, r = i, i + j - 1
        else:
            # Case 2: i is inside the box, try to reuse Z[mirror]
            k = i - l           # mirror position in the prefix
            box_rem = r - i + 1  # characters remaining in box from i

            if Z[k] < box_rem:
                Z[i] = Z[k]      # Case 2a: mirror fits inside box, copy directly
            elif Z[k] > box_rem:
                Z[i] = box_rem   # Case 2b.1: mirror exceeds box, cap at boundary
            else:
                # Case 2b.2: mirror hits boundary exactly, extend from r+1
                j = box_rem
                while i + j < n and s[j] == s[i + j]:
                    j += 1
                Z[i] = j
                l, r = i, i + j - 1

    return Z


def compute_zsuf(pat):
    """
    Compute zsuf for pat, where:
    zsuf[i] = length of the longest substring ending at pat[i] that equals some suffix of pat.

    Method used here Lab Q8:
      1. rev  = reverse of pat
      2. zrev = z_algorithm(rev)
      3. zsuf[m-1-j] = zrev[j]

    Example to clarify the reverse-to-suffix mapping:
    pat = "abab", so rev = "baba"
    zrev = [4,0,2,0] (why zrev[0]=4=len(rev)? By the Z-array convention, can not be used for matching)
    j=2: zrev[2]=2, rev[2..3]="ba" matches rev[0..1]="ba"
    as zsuf[m-1-j] = zrev[j], so zsuf[4-1-2]=zsuf[1]=2
    so pat[0..1]="ab" matches the last 2 chars of pat "ab".

    O(m) time, O(m) space.
    """
    m = len(pat)
    rev = pat[::-1]
    zrev = z_algorithm(rev)

    zsuf = [0] * m
    for j in range(m):
        zsuf[m - 1 - j] = zrev[j]
    return zsuf


def build_shift_table(pat, zsuf, m):
    """
    For each mismatch position k and bad character c, precompute the leftmost p in [k+2, m]
    satisfying:
      Cond 1: pat[k+1 .. k+m-p] == pat[p .. m-1]   (beta substring matches)
      Cond 2: pat[p-1] == c                          (bad char can connect)

    Reparameterise with L = m - p (length of beta):
      Cond 1 : L == 0 or zsuf[k+L] >= L
      Cond 2 : pat[m-L-1] == c
    Leftmost p = largest L, so iterate L from Lmax = m-k-2 downward.
    For each L where C1 holds, it is a valid answer for char pat[m-L-1].
    Since we go large L first, the first hit recorded per char is the leftmost p.

    table[k+1][ord(c) - 37] = leftmost p, or m+1 as the fallback sentinel.

    k ranges from -1 to m-2 (k=-1 handles the full-match-then-shift case).
    
    Time: O(m^2), since for each of the O(m) k's we iterate through O(m) L's.
    Space: O(m * 90) for the table.
    """
    FALLBACK = m + 1
    # rows: k+1 for k in {-1, 0, ..., m-1}, then  m+1 rows total
    table = [[FALLBACK] * _SIGMA for _ in range(m + 1)]

    for k in range(-1, m - 1):
        Lmax = m - k - 2   # p in [k+2, m], then  L in [0, m-k-2]
        for L in range(Lmax, -1, -1):
            # C1: beta matches some suffix of pat
            if L >= 1 and zsuf[k + L] < L:
                continue
            # C1 holds for this L; record the answer for char pat[m-L-1] (C2)
            c_idx = ord(pat[m - L - 1]) - _ASCII_MIN
            if table[k + 1][c_idx] == FALLBACK:
                table[k + 1][c_idx] = m - L   # first hit = largest L = leftmost p

    return table


def search(txt, pat):
    """
    Right-to-left Boyer-Moore style search (mirror BM).
    Start with pat's right edge aligned to txt's right edge, shift left each time.
    Each alignment scans right-to-left.
    Uses a skip frontier, similar to Galil's optimisation, to avoid re-checking
    a suffix that is already known to match.

    Preprocessing:
      compute_zsuf: O(m)
      build_shift_table: O(m^2)
    
    Search loop: O(n) using the skip-frontier argument explained in the report.
    Overall time: O(m^2 + n), with O(m^2) preprocessing from the shift table.

    Returns the discovered match positions together with an internal alignment trace.
    """
    n = len(txt)
    m = len(pat)

    if m == 0 or m > n:
        return [], []

    zsuf  = compute_zsuf(pat)
    table = build_shift_table(pat, zsuf, m)

    matches = []
    trace = []

    j = n - m   # first alignment: right edges aligned

    # sf = Galil skip frontier
    # pat[sf..m-1] is already verified to match, so next scan starts at sf-1
    
    sf = m # means nothing is pre-verified yet (scan from m-1 normally)

    while j >= 0:

        # scan right-to-left; skip verified suffix if sf < m
        k = sf - 1 if sf < m else m - 1

        while k >= 0:
            if pat[k] != txt[j + k]:
                break
            k -= 1
        # k == -1: full match; k >= 0: mismatch at position k

        if k == -1:
            matches.append(j + 1)  # store as 1-based

        # if j+k < 0, we've gone past the left end of txt, no more shifts possible
        if j + k < 0:
            break

        x     = txt[j + k]                        # bad character
        idx = ord(x) - _ASCII_MIN
        p_out = table[k + 1][idx] if 0 <= idx < _SIGMA else m + 1

        if p_out == m + 1:
            # No valid p found. Use the fallback shift.
            # Moves the current bad-character position out of the next alignment.
            shift   = m - k
            next_sf = m     # nothing pre-verified next round
        else:
            shift   = p_out - k - 1
            # Galil: after shift, pat[p_out-1..m-1] is guaranteed to match txt,
            # so next scan only needs to go up to index p_out-2
            next_sf = p_out - 1

        trace.append((j, k + 1, p_out))

        sf  = next_sf
        j  -= shift

    return matches, trace

def exact_match(text: str, pattern: str) -> list[int]:
    """Return 0-based exact-match positions in ascending order."""
    if pattern == "":
        return list(range(len(text) + 1))
    matches, _ = search(text, pattern)
    return sorted(pos - 1 for pos in matches)
