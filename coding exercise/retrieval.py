#!/usr/bin/env python3
"""
Cosine Top-K Retrieval + a mini evaluation

Part 1  cosine(a, b) -> float
    Cosine similarity of two equal-length vectors: dot(a, b) / (|a| * |b|).
    Range is -1.0 .. 1.0. Convention: if either vector has length 0, return 0.0.

Part 2  top_k(query, docs, k) -> list[int]
    Indices of the k docs most similar to query, highest similarity first.
    Ties: smaller index first. If k > len(docs) return all indices; k == 0 -> [].
    Target: O(n log k) with a heap of size k, not O(n log n) by sorting everything.

Part 3  precision_recall_at_k(retrieved, relevant, k) -> (float, float)
    Look only at the first k retrieved indices.
        precision@k = hits / k                (of what I showed, how much was right)
        recall@k    = hits / len(relevant)    (of what was right, how much did I show)
    Conventions: the precision denominator is k even if fewer than k were retrieved;
    if relevant is empty, recall is 0.0.

Part 4  evaluate_retrieval(query, docs, relevant, k) -> (float, float)
    Run top_k, then score it with part 3. End-to-end.

Run the tests:  python3 test_retrieval.py        (all parts)
                python3 test_retrieval.py 2      (part 2 only)
or just run this file (F5 in VS Code).
"""
import heapq
import math


def cosine(a: list[float], b: list[float]) -> float:
    dot_product = sum(a[i] * b[i] for i in range(len(a)))
    a_length = math.sqrt(sum(a[i] * a[i] for i in range(len(a))))
    b_length = math.sqrt(sum(b[i] * b[i] for i in range(len(b))))
    if a_length == 0 or b_length == 0:
        return 0.0
    else:
        return dot_product / (a_length * b_length)


def top_k(query: list[float], docs: list[list[float]], k: int) -> list[int]:
    res = []
    for index, doc in enumerate(docs):
        sim_score = cosine(query, doc)
        heapq.heappush(res, (-sim_score, index))
    
    output = []
    for i in range(min(k, len(docs))):
        output.append(heapq.heappop(res)[1])
    return output


def precision_recall_at_k(retrieved: list[int], relevant: set[int], k: int) -> tuple[float, float]:
    correct = relevant.intersection(retrieved[:k])
    precision = len(correct) / k
    recall = len(correct) / len(relevant) if len(relevant) else 0
    return (precision, recall)


def evaluate_retrieval(query: list[float], docs: list[list[float]], relevant: set[int], k: int) -> tuple[float, float]:
    top_k_list = top_k(query, docs, k)
    return precision_recall_at_k(top_k_list, relevant, k)


if __name__ == "__main__":
    from test_retrieval import main
    main()
