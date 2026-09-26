"""Knowledge base loader backed by official Kyungdong University Global pages."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache"
CACHE_FILE = CACHE_DIR / "official_knowledge_base.json"
DEFAULT_CACHE_TTL_HOURS = 12
HTTP_TIMEOUT_SECONDS = 20
USER_AGENT = "Mozilla/5.0 (compatible; KDUChatbot/1.0; +https://global.kduniv.ac.kr/)"


@dataclass(frozen=True)
class OfficialPage:
    title: str
    url: str
    category: str


@dataclass(frozen=True)
class OfficialSocialSource:
    platform: str
    label: str
    url: str
    source_page: str


OFFICIAL_PAGE_SOURCES = [
    OfficialPage("About KDU", "https://global.kduniv.ac.kr/global/index.php?pCode=1636357850", "overview"),
    OfficialPage("Why KDU Global", "https://global.kduniv.ac.kr/global/index.php?pCode=1637029989", "overview"),
    OfficialPage("Admissions: General Guidelines", "https://global.kduniv.ac.kr/global/index.php?pCode=1636097085", "admissions"),
    OfficialPage("Admissions: Application Process", "https://global.kduniv.ac.kr/global/index.php?pCode=1434967568", "admissions"),
    OfficialPage("Admissions: Documents Required", "https://global.kduniv.ac.kr/global/index.php?pCode=1434967575", "admissions"),
    OfficialPage("Admissions: Scholarships and Fees", "https://global.kduniv.ac.kr/global/index.php?pCode=1636097108", "fees"),
    OfficialPage("Academics", "https://global.kduniv.ac.kr/global/index.php?pCode=1466580676", "academics"),
    OfficialPage("Campus Life: Student Events", "https://global.kduniv.ac.kr/global/index.php?pCode=1434967668", "campus_life"),
    OfficialPage("Campus Life: Student Clubs and Labs", "https://global.kduniv.ac.kr/global/index.php?pCode=1716343145", "campus_life"),
    OfficialPage("Campus Life: Student Housing", "https://global.kduniv.ac.kr/global/index.php?pCode=1742277701", "campus_life"),
    OfficialPage("Campus Life: Campus Facilities", "https://global.kduniv.ac.kr/global/index.php?pCode=1441076111", "campus_life"),
    OfficialPage("Student Services", "https://global.kduniv.ac.kr/global/index.php?pCode=1742272248", "student_services"),
    OfficialPage("Part-time Job Support", "https://global.kduniv.ac.kr/global/index.php?pCode=1742272258", "student_services"),
    OfficialPage("Career Development Center", "https://global.kduniv.ac.kr/global/index.php?pCode=1742272266", "student_services"),
    OfficialPage("Counselling and Human Rights Center", "https://global.kduniv.ac.kr/global/index.php?pCode=1742272273", "student_services"),
]

OFFICIAL_SOCIAL_SOURCES = [
    OfficialSocialSource(
        platform="facebook",
        label="KDU Global Facebook",
        url="https://www.facebook.com/prof.john.k.lee",
        source_page="https://global.kduniv.ac.kr/global/",
    ),
    OfficialSocialSource(
        platform="youtube",
        label="KDU Global YouTube",
        url="https://www.youtube.com/@kduglobal9167",
        source_page="https://global.kduniv.ac.kr/global/",
    ),
]

FALLBACK_DOCUMENTS = [
    {
        "id": "fallback_contact_001",
        "content": "Kyungdong University Global Campus is located at 46 Bongpo 4-gil, Goseong-gun, Gangwon State 24764, and admissions inquiries can be sent to info@kduniv.ac.kr.",
        "source": "Kyungdong University Global",
        "category": "overview",
        "url": "https://global.kduniv.ac.kr/global/",
        "title": "Official Contact Information",
    }
]


def _normalize_text(text: str) -> str:
    text = unescape(text).replace("\xa0", " ").replace("\u200b", " ")
    lines = []
    seen = set()

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip(" \t\r\n-•")
        if not line:
            continue
        if line in {"PRINT", "+", "-", "HOME", "SITEMAP", "LANGUAGE"}:
            continue
        if line.startswith("Kyungdong University Global:") or line == "Apply Now":
            continue
        marker = line.lower()
        if marker in seen:
            continue
        seen.add(marker)
        lines.append(line)

    return "\n\n".join(lines)


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    content_root = None
    for selector in ("#cont .contOutput", ".contOutput", "#cont", "#contents", "main"):
        content_root = soup.select_one(selector)
        if content_root is not None:
            break

    if content_root is None:
        content_root = soup.body or soup

    for selector in (
        "script",
        "style",
        "noscript",
        "iframe",
        "img",
        "svg",
        "button",
        ".cont_btn",
        ".cont_navi",
        ".cont_tit",
        "#cont_top",
        "header",
        "footer",
        "nav",
        "form",
    ):
        for tag in content_root.select(selector):
            tag.decompose()

    return _normalize_text(content_root.get_text("\n", strip=True))


def _split_large_paragraph(paragraph: str, chunk_size: int) -> List[str]:
    if len(paragraph) <= chunk_size:
        return [paragraph]

    segments = []
    buffer = ""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    for sentence in sentences:
        candidate = f"{buffer} {sentence}".strip()
        if buffer and len(candidate) > chunk_size:
            segments.append(buffer)
            buffer = sentence.strip()
        else:
            buffer = candidate

    if buffer:
        segments.append(buffer)

    final_segments = []
    for segment in segments:
        if len(segment) <= chunk_size:
            final_segments.append(segment)
            continue
        words = segment.split()
        word_buffer = []
        for word in words:
            candidate = " ".join(word_buffer + [word])
            if word_buffer and len(candidate) > chunk_size:
                final_segments.append(" ".join(word_buffer))
                word_buffer = [word]
            else:
                word_buffer.append(word)
        if word_buffer:
            final_segments.append(" ".join(word_buffer))

    return final_segments


def _build_document(page: OfficialPage, content: str, index: int) -> dict:
    digest = hashlib.sha1(f"{page.url}:{index}:{content}".encode("utf-8")).hexdigest()[:16]
    return {
        "id": f"{page.category}_{digest}",
        "content": content,
        "source": page.title,
        "category": page.category,
        "url": page.url,
        "title": page.title,
    }


def _chunk_text(page: OfficialPage, text: str, chunk_size: int = 900) -> List[dict]:
    paragraphs = []
    for paragraph in text.split("\n\n"):
        clean = paragraph.strip()
        if clean:
            paragraphs.extend(_split_large_paragraph(clean, chunk_size))

    documents = []
    current_parts = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)
        if current_parts and current_length + paragraph_length + 2 > chunk_size:
            documents.append(_build_document(page, "\n\n".join(current_parts), len(documents)))
            current_parts = [paragraph]
            current_length = paragraph_length
        else:
            current_parts.append(paragraph)
            current_length += paragraph_length + (2 if len(current_parts) > 1 else 0)

    if current_parts:
        documents.append(_build_document(page, "\n\n".join(current_parts), len(documents)))

    return documents


def _fetch_page_documents(page: OfficialPage) -> List[dict]:
    response = requests.get(
        page.url,
        timeout=HTTP_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    text = _extract_text_from_html(response.text)
    if not text:
        raise ValueError(f"No content extracted from {page.url}")
    return _chunk_text(page, text)


def _load_cache() -> List[dict]:
    if not CACHE_FILE.exists():
        return []
    try:
        payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload.get("documents", [])


def _save_cache(documents: Iterable[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": int(time.time()),
        "documents": list(documents),
    }
    CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_official_source_pages() -> List[dict]:
    return [{"title": page.title, "url": page.url, "category": page.category} for page in OFFICIAL_PAGE_SOURCES]


def get_official_social_sources() -> List[dict]:
    return [
        {
            "platform": source.platform,
            "label": source.label,
            "url": source.url,
            "source_page": source.source_page,
        }
        for source in OFFICIAL_SOCIAL_SOURCES
    ]


def load_knowledge_base(force_refresh: bool = False, cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS) -> List[dict]:
    """Load the university knowledge base from the official KDU Global website."""
    cache_ttl_seconds = max(cache_ttl_hours, 1) * 3600

    if not force_refresh and CACHE_FILE.exists():
        cache_age = time.time() - CACHE_FILE.stat().st_mtime
        if cache_age <= cache_ttl_seconds:
            cached_documents = _load_cache()
            if cached_documents:
                return cached_documents

    documents = []
    for page in OFFICIAL_PAGE_SOURCES:
        try:
            documents.extend(_fetch_page_documents(page))
        except Exception as exc:
            print(f"Warning: failed to fetch {page.url}: {exc}")

    if documents:
        _save_cache(documents)
        return documents

    cached_documents = _load_cache()
    if cached_documents:
        return cached_documents

    return FALLBACK_DOCUMENTS.copy()