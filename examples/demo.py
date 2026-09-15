from advanced_string_algorithms import (
    exact_match,
    approximate_match,
    lcp_array,
    rabin_karp_match,
)

text = "bananabanana"
pattern = "ana"

print("Z-style exact matches:", exact_match(text, pattern))
print("Rabin-Karp matches:", rabin_karp_match(text, pattern))
print("LCP array for 'banana':", lcp_array("banana"))
print("BWT distance<=1 matches:", approximate_match("banena", "banana"))
