# Algorithm notes

This repository focuses on four advanced string-processing techniques.

## 1. Z-suffix / right-to-left exact matching

The matcher preprocesses the pattern with a Z-derived suffix structure and a
bad-character shift table. Search proceeds from right to left and keeps a
Galil-style skip frontier so already verified suffix characters do not need to
be compared again.

## 2. BWT approximate matching

A suffix array and Burrows-Wheeler Transform form an index for backward
search. The recursive search tracks whether its single edit budget has been
spent and branches for:

- substitution;
- insertion;
- deletion; and
- adjacent transposition.

Once the edit budget is consumed, the remaining prefix must match exactly.

## 3. Ukkonen suffix tree and LCP extraction

The suffix tree uses Ukkonen's online construction with:

- an active point;
- suffix links;
- skip/count traversal;
- a shared leaf end;
- edge labels stored as index pairs into the original string.

A lexicographic DFS then emits the LCP array by carrying the string depth of
the branch point between neighbouring suffixes.

## 4. Rabin-Karp with generated prime modulus

The matcher combines:

- repeated-squaring modular exponentiation;
- Miller-Rabin probabilistic primality testing;
- random prime generation;
- Horner polynomial hashing; and
- constant-time rolling hash updates.

Hash collisions are verified by direct character comparison.

## Scope

The code is intended as an algorithms portfolio and educational reference.
It is not a replacement for a production-grade suffix-array/FM-index library.
