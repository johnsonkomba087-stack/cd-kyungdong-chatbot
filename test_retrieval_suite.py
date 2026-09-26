"""Regression checks for retrieval hit-rate.

Run:
    python test_retrieval_suite.py
"""

from __future__ import annotations

from retrieval_test_suite import TEST_CASES, evaluate_case
from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base


def main() -> int:
    docs = load_knowledge_base(force_refresh=False)
    bot = KyungdongRAGChatbot(groq_api_key="")
    bot.add_documents(docs)

    results = [evaluate_case(bot, case, k=5) for case in TEST_CASES]
    total = len(results)
    hits = sum(1 for result in results if result["hit"])
    hit_rate = hits / max(total, 1)

    min_required_hit_rate = 0.70
    print(f"Retrieval regression: {hits}/{total} ({hit_rate:.1%})")

    failed = [result for result in results if not result["hit"]]
    if failed:
        print("Failed cases:")
        for item in failed:
            print(f"- {item['name']}: {item['query']}")

    if hit_rate < min_required_hit_rate:
        raise AssertionError(
            f"Hit rate {hit_rate:.1%} is below threshold {min_required_hit_rate:.0%}."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
