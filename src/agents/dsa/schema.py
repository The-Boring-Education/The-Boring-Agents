"""Canonical DSA schema constants aligned with TBE-Web."""

from typing import Dict

ALLOWED_DSA_DIFFICULTY = {"EASY", "MEDIUM", "HARD"}

ALLOWED_DSA_DOMAIN = {"FRONTEND", "BACKEND", "GENERAL", "FULLSTACK", "DSA"}

ALLOWED_COMPANY_TYPES = {
    "Startup",
    "MidSize",
    "MNC",
    "FAANG",
    "GOOGLE",
    "MICROSOFT",
    "META",
    "AMAZON",
    "AIRBNB",
    "UBER",
}

ALLOWED_DSA_TOPICS = {
    "ARRAY",
    "STRING",
    "HASHMAP",
    "SLIDING_WINDOW",
    "PREFIX_SUM",
    "SORTING",
    "BINARY_SEARCH",
    "MATH",
    "BIT_MANIPULATION",
    "RECURSION",
    "LINKED_LIST",
    "STACK",
    "QUEUE",
    "BINARY_TREE",
    "TREE",
    "BST",
    "HEAP",
    "TRIE",
    "GRAPH",
    "BACKTRACKING",
    "DYNAMIC_PROGRAMMING",
    "GREEDY",
    "UNION_FIND",
    "SIMULATION",
    "DESIGN",
    "MONOTONIC_STACK",
    # accepted extras used by TBE-Web queries
    "TWO_POINTERS",
    "DFS",
    "BFS",
}

TOPIC_ALIAS_MAP: Dict[str, str] = {
    "array": "ARRAY",
    "arrays": "ARRAY",
    "string": "STRING",
    "strings": "STRING",
    "hashmap": "HASHMAP",
    "hash map": "HASHMAP",
    "sliding window": "SLIDING_WINDOW",
    "prefix sum": "PREFIX_SUM",
    "sorting": "SORTING",
    "binary search": "BINARY_SEARCH",
    "math": "MATH",
    "bit manipulation": "BIT_MANIPULATION",
    "recursion": "RECURSION",
    "linked list": "LINKED_LIST",
    "stack": "STACK",
    "queue": "QUEUE",
    "binary tree": "BINARY_TREE",
    "tree": "TREE",
    "bst": "BST",
    "heap": "HEAP",
    "trie": "TRIE",
    "graph": "GRAPH",
    "dfs": "DFS",
    "bfs": "BFS",
    "backtracking": "BACKTRACKING",
    "dynamic programming": "DYNAMIC_PROGRAMMING",
    "dp": "DYNAMIC_PROGRAMMING",
    "greedy": "GREEDY",
    "union find": "UNION_FIND",
    "simulation": "SIMULATION",
    "design": "DESIGN",
    "monotonic stack": "MONOTONIC_STACK",
    "two pointers": "TWO_POINTERS",
}

COMPANY_ALIAS_MAP: Dict[str, str] = {
    "startup": "Startup",
    "mid_size": "MidSize",
    "midsize": "MidSize",
    "mnc": "MNC",
    "faang": "FAANG",
    "google": "GOOGLE",
    "microsoft": "MICROSOFT",
    "meta": "META",
    "amazon": "AMAZON",
    "airbnb": "AIRBNB",
    "uber": "UBER",
}
