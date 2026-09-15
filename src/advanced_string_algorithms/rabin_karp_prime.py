"""Rabin-Karp matching with a randomly generated prime modulus.

Includes repeated-squaring modular exponentiation and Miller-Rabin primality
testing, then uses Horner hashing and O(1) rolling updates.
"""

import random

BETA = 128
MIN_BITS = 32
MR_ROUNDS = 40

def mod_exp(a, b, n):
    """
    a^b mod n by repeated squaring (used here), since the built-in pow is not
    allowed. Walk the bits of b from low to high, keep squaring a running term,
    and fold it into the result whenever the current bit is 1.
    """
    if n == 1:                    # everything is 0 mod 1
        return 0

    current = a % n               # term for the least significant bit
    if b % 2 == 1:
        result = current
    else:
        result = 1
    b = b // 2

    while b > 0:                  # remaining bits, low to high
        current = (current * current) % n
        if b % 2 == 1:
            result = (result * current) % n
        b = b // 2

    return result


def miller_rabin(n, k):
    """
    Miller-Rabin primality test with k random witnesses (used here). Write
    n - 1 = 2^s * t with t odd, then for each witness run Fermat's check and look
    for a square root of 1 other than 1 or n-1. It never rejects a real prime; a
    composite gets through with probability at most 4^(-k).
    """
    if n == 2 or n == 3:          # small primes
        return True
    if n % 2 == 0:                # any other even number
        return False

    # n - 1 = 2^s * t, t odd
    s = 0
    t = n - 1
    while t % 2 == 0:
        s += 1
        t = t // 2

    for _ in range(k):
        a = random.randint(2, n - 2)

        # x_0 = a^t, then square repeatedly to reach x_s = a^(n-1)
        seq = [mod_exp(a, t, n)]
        for _j in range(s):
            seq.append((seq[-1] * seq[-1]) % n)

        if seq[s] != 1:           # Fermat check fails, so composite
            return False

        # a 1 whose predecessor is not 1 or n-1 is a bad square root of 1
        for j in range(1, s + 1):
            if seq[j] == 1 and seq[j - 1] != 1 and seq[j - 1] != n - 1:
                return False

    return True


def generate_prime(num_bits, k):
    """
    Sample random num_bits-bit integers (top bit always set) and return the first
    that passes Miller-Rabin. By the prime number theorem only about num_bits
    candidates are needed on average.
    """
    low = 2 ** (num_bits - 1)
    high = 2 ** num_bits - 1
    while True:
        candidate = random.randint(low, high)
        if miller_rabin(candidate, k):
            return candidate


def matches_at(txt, pat, j):
    """
    Check pat == txt[j .. j+m-1] one character at a time. This verifies hash hits because distinct substrings can share the same residue.
    """
    for k in range(len(pat)):
        if txt[j + k] != pat[k]:
            return False
    return True


def find_matches(txt, pat):
    """
    Rabin-Karp search. Pick a prime p, hash the pattern and the
    first window with Horner's rule, then slide the window updating its hash in
    O(1) and only do a real character check when the hashes match. The rolling update follows the polynomial-hash recurrence. Returns the 1-based match positions.
    """
    n = len(txt)
    m = len(pat)

    if m > n:                     # pattern longer than text, nothing can match
        return []

    # prime modulus over t = max(32, m) bits
    t = MIN_BITS if m < MIN_BITS else m
    p = generate_prime(t, MR_ROUNDS)

    # r(pat) by Horner's rule
    pat_hash = 0
    for c in pat:
        pat_hash = (pat_hash * BETA + ord(c)) % p

    # weight of the leading digit, beta^(m-1) mod p
    high_pow = mod_exp(BETA, m - 1, p)

    # hash of the first window txt[0 .. m-1]
    window_hash = 0
    for k in range(m):
        window_hash = (window_hash * BETA + ord(txt[k])) % p

    matches = []

    # j is the 0-based window start, valid range 0 .. n-m
    for j in range(n - m + 1):
        if j > 0:
            # roll: drop txt[j-1], shift up one digit, add txt[j+m-1]
            removed = (ord(txt[j - 1]) * high_pow) % p
            window_hash = ((window_hash - removed) * BETA + ord(txt[j + m - 1])) % p

        # equal hashes are only a hint, so verify the characters
        if window_hash == pat_hash and matches_at(txt, pat, j):
            matches.append(j + 1)     # 1-based position

    return matches

def rabin_karp_match(text: str, pattern: str) -> list[int]:
    """Return 0-based exact-match positions."""
    if pattern == "":
        return list(range(len(text) + 1))
    return [p - 1 for p in find_matches(text, pattern)]
