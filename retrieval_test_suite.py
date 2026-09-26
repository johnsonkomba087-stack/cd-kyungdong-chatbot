"""Hybrid retrieval evaluation for KDU chatbot.

Run:
    python retrieval_test_suite.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import load_knowledge_base


@dataclass
class RetrievalTestCase:
    name: str
    query: str
    expected_sources: List[str]
    expected_categories: List[str]
    expected_terms: List[str]


TEST_CASES: List[RetrievalTestCase] = [
    RetrievalTestCase(
        name="bachelor_programs",
        query="list all bachelor programs at kdu global",
        expected_sources=["Academics", "Admissions: General Guidelines"],
        expected_categories=["academics", "admissions"],
        expected_terms=["bachelor", "undergraduate", "program"],
    ),
    RetrievalTestCase(
        name="admission_documents",
        query="what documents are required for undergraduate application",
        expected_sources=["Admissions: Documents Required"],
        expected_categories=["admissions"],
        expected_terms=["application form", "passport", "transcript"],
    ),
    RetrievalTestCase(
        name="application_process",
        query="explain application process step by step",
        expected_sources=["Admissions: Application Process"],
        expected_categories=["admissions"],
        expected_terms=["offer letter", "certificate of admission", "visa application"],
    ),
    RetrievalTestCase(
        name="scholarship_requirements",
        query="scholarship requirements for international students",
        expected_sources=["Admissions: Scholarships and Fees"],
        expected_categories=["fees"],
        expected_terms=["ielts", "scholarship", "tuition"],
    ),
    RetrievalTestCase(
        name="tuition_fees",
        query="tuition fee per semester for international students",
        expected_sources=["Admissions: Scholarships and Fees"],
        expected_categories=["fees"],
        expected_terms=["tuition", "$4,000", "$5,000"],
    ),
    RetrievalTestCase(
        name="dormitory_fees",
        query="dormitory fees and housing costs",
        expected_sources=["Campus Life: Student Housing", "Admissions: Scholarships and Fees"],
        expected_categories=["campus_life", "fees"],
        expected_terms=["dormitory", "housing", "$1,100"],
    ),
    RetrievalTestCase(
        name="visa_support",
        query="visa and immigration support for students",
        expected_sources=["Student Services", "Career Development Center"],
        expected_categories=["student_services"],
        expected_terms=["visa", "immigration", "arc"],
    ),
    RetrievalTestCase(
        name="part_time_job",
        query="part-time job requirements and documents",
        expected_sources=["Part-time Job Support"],
        expected_categories=["student_services"],
        expected_terms=["part-time", "passport", "alien residence card"],
    ),
    RetrievalTestCase(
        name="student_services",
        query="what student services are available for international students",
        expected_sources=["Student Services"],
        expected_categories=["student_services"],
        expected_terms=["airport", "counselling", "support"],
    ),
    RetrievalTestCase(
        name="campus_facilities",
        query="what campus facilities and dorm amenities are available",
        expected_sources=["Campus Life: Campus Facilities", "Campus Life: Student Housing"],
        expected_categories=["campus_life"],
        expected_terms=["wifi", "cafeteria", "gym"],
    ),
]


def evaluate_case(bot: KyungdongRAGChatbot, case: RetrievalTestCase, k: int = 5) -> dict:
    docs = bot.retrieve_documents(case.query, top_k=k, score_threshold=0.1)

    source_hit = False
    category_hit = False
    term_hit = False

    observed_sources = [doc.source for doc in docs]
    observed_categories = [doc.category for doc in docs]
    observed_snippet = "\n".join(doc.content.lower() for doc in docs)

    for source_hint in case.expected_sources:
        if any(source_hint.lower() in src.lower() for src in observed_sources):
            source_hit = True
            break

    for category in case.expected_categories:
        if category in observed_categories:
            category_hit = True
            break

    for term in case.expected_terms:
        if term.lower() in observed_snippet:
            term_hit = True
            break

    overall_hit = source_hit or category_hit or term_hit
    top_score = round(docs[0].relevance_score, 4) if docs else 0.0

    return {
        "name": case.name,
        "query": case.query,
        "hit": overall_hit,
        "source_hit": source_hit,
        "category_hit": category_hit,
        "term_hit": term_hit,
        "top_score": top_score,
        "top_sources": observed_sources,
    }


def build_report(results: List[dict], output_path: Path) -> None:
    total = len(results)
    hits = sum(1 for result in results if result["hit"])
    hit_rate = (hits / total) if total else 0.0

    lines = [
        "# Retrieval Hit-Rate Report",
        "",
        f"Generated at: {datetime.utcnow().isoformat()} UTC",
        f"Total test cases: {total}",
        f"Hits: {hits}",
        f"Hit rate: {hit_rate:.1%}",
        "",
        "## Per-Case Results",
        "",
        "| Case | Hit | Source Hit | Category Hit | Term Hit | Top Score | Top Sources |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    for result in results:
        lines.append(
            "| {name} | {hit} | {source_hit} | {category_hit} | {term_hit} | {top_score:.2f} | {sources} |".format(
                name=result["name"],
                hit="Y" if result["hit"] else "N",
                source_hit="Y" if result["source_hit"] else "N",
                category_hit="Y" if result["category_hit"] else "N",
                term_hit="Y" if result["term_hit"] else "N",
                top_score=result["top_score"],
                sources=", ".join(result["top_sources"][:3]),
            )
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    project_root = Path(__file__).resolve().parent
    cache_dir = project_root / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    documents = load_knowledge_base(force_refresh=False)
    bot = KyungdongRAGChatbot(groq_api_key="")
    bot.add_documents(documents)

    results = [evaluate_case(bot, case, k=5) for case in TEST_CASES]

    report_markdown_path = project_root / "retrieval_hit_rate_report.md"
    report_json_path = cache_dir / "retrieval_hit_rate_report.json"

    build_report(results, report_markdown_path)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "hits": sum(1 for result in results if result["hit"]),
        "hit_rate": (sum(1 for result in results if result["hit"]) / max(len(results), 1)),
        "results": results,
    }
    report_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved markdown report: {report_markdown_path}")
    print(f"Saved JSON report: {report_json_path}")
    print(f"Hit rate: {payload['hit_rate']:.1%} ({payload['hits']}/{payload['total']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
