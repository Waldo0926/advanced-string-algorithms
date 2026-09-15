"""Ukkonen suffix-tree construction and LCP-array extraction."""

TERM = "$"

class Node:
    def __init__(self, node_id, start, end, is_leaf):
        self.id = node_id        # creation order, root is Node 1
        self.start = start       # first char of the incoming edge (0-based)
        self.end = end           # internal: fixed end index; leaf: unused
        self.is_leaf = is_leaf
        self.children = {}       # keyed by first char of the child edge
        self.link = None         # suffix link
        self.suffix_id = -1


def edge_length(node, leaf_end):
    """Length of the edge entering node
       a leaf uses the global end as its right end."""
    last = leaf_end if node.is_leaf else node.end
    return last - node.start + 1


def build_suffix_tree(s):
    """
    Build the suffix tree online with Ukkonen's algorithm. The active point is (active_node, active_edge, active_length)
    and remaining is how many suffixes still owe an explicit extension this phase.
    Returns the root node and a construction trace.
    """
    n = len(s)
    log = []
    log.append("Root Node 1")

    root = Node(1, -1, -1, False)
    root.link = root
    node_count = 1            # last id handed out, root already took 1

    # active point starts at the root with nothing matched
    active_node = root
    active_edge = -1
    active_length = 0
    remaining = 0
    leaf_end = -1             # global end shared by all leaves

    # logging helpers
    def emit(level, text):
        log.append("    " * level + text)

    def remainder_text():
        if active_length == 0:
            return "EMPTY"
        x = active_edge + 1
        y = active_edge + active_length
        return f"S[{x}...{y}]"

    def log_active():
        emit(1, f"Active Node = Node {active_node.id} "
                f"(suffix link to Node {active_node.link.id}); "
                f"Remainder = {remainder_text()}")

    for pos in range(n):
        leaf_end = pos                # Rule 1 extends every open leaf for free
        remaining += 1
        pending = None                # internal node still waiting for its suffix link

        emit(0, "")
        first_extn = pos - remaining + 2
        emit(0, f"Phase {pos + 1} starts from Extn {first_extn}")

        while remaining > 0:
            if active_length == 0:
                active_edge = pos     # nothing buffered, so the active edge is the new char

            cur = s[active_edge]
            extn = pos - remaining + 2  # 1-based number of this extension

            if cur not in active_node.children:
                # Rule 2 (alternate): no edge from the active node starts with cur
                emit(1, f"Extn {extn} applies Rule 2 (alternate)")
                log_active()
                node_count += 1
                leaf = Node(node_count, pos, None, True)
                leaf.suffix_id = extn
                active_node.children[cur] = leaf
                emit(2, f"Node {leaf.id} created: Leaf node!")
                if pending is not None:
                    pending.link = active_node
                    emit(2, f"Linking Node {pending.id} to Node {active_node.id}")
                    pending = None

            else:
                nxt = active_node.children[cur]
                length = edge_length(nxt, leaf_end)

                if active_length >= length:
                    # skip/count: hop onto the child and retry
                    active_edge += length
                    active_length -= length
                    active_node = nxt
                    continue

                if s[nxt.start + active_length] == s[pos]:
                    # Rule 3: cur already continues along this edge, so stop the phase
                    emit(1, f"Extn {extn} applies Rule 3")
                    log_active()
                    if pending is not None:
                        pending.link = active_node
                        emit(2, f"Linking Node {pending.id} to Node {active_node.id}")
                        pending = None
                    active_length += 1
                    break

                # Rule 2 (regular): mismatch inside the edge, split it
                emit(1, f"Extn {extn} applies Rule 2 (regular)")
                log_active()
                node_count += 1
                split = Node(node_count, nxt.start, nxt.start + active_length - 1, False)
                split.link = root
                active_node.children[cur] = split
                node_count += 1
                leaf = Node(node_count, pos, None, True)
                leaf.suffix_id = extn
                split.children[s[pos]] = leaf
                nxt.start += active_length        # old node keeps the tail of the edge
                split.children[s[nxt.start]] = nxt
                emit(2, f"Node {split.id} created: Internal node!")
                emit(2, f"Node {leaf.id} created: Leaf node!")
                if pending is not None:
                    pending.link = split
                    emit(2, f"Linking Node {pending.id} to Node {split.id}")
                pending = split

            # active point update after a real extension (Rule 3 already broke out)
            remaining -= 1
            if active_node is root and active_length > 0:
                active_length -= 1
                active_edge = pos - remaining + 1
            elif active_node is not root:
                active_node = active_node.link

    return root, log


def lcp_from_tree(root, n):
    """
    Read the LCP array off the finished tree. Visiting children in sorted order
    of first character makes the DFS emit leaves in suffix array order, and the
    LCP of two neighbours is the string depth of the node where the walk last
    switched children. I carry that depth in pending_lcp, and use an explicit
    stack instead of recursion so a string like "aaaa...$" cannot hit the limit.
    """
    lcp = []
    pending_lcp = 0

    # frame: [node, sorted child keys, next child index, string depth]
    root_keys = sorted(root.children.keys())
    stack = [[root, root_keys, 0, 0]]

    while stack:
        frame = stack[-1]
        node, keys, k, depth = frame
        if k >= len(keys):
            stack.pop()
            continue
        frame[2] += 1                 # advance to the next child for when we return

        if k > 0:
            pending_lcp = depth       # new sibling, so the divergence is at this node

        child = node.children[keys[k]]
        if child.is_leaf:
            lcp.append(pending_lcp)   # leaf reached, its LCP is the current carry
        else:
            child_depth = depth + edge_length(child, n - 1)
            stack.append([child, sorted(child.children.keys()), 0, child_depth])

    return lcp

def lcp_array(text: str) -> list[int]:
    """Build a suffix tree with Ukkonen's algorithm and return the LCP array."""
    if TERM in text:
        raise ValueError("Input must not contain the terminal symbol '$'.")
    indexed = text + TERM
    root, _log = build_suffix_tree(indexed)
    return lcp_from_tree(root, len(indexed))
