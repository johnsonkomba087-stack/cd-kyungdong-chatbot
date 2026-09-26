"""Knowledge base loader backed by official Kyungdong University Global pages."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache"
CACHE_FILE = CACHE_DIR / "official_knowledge_base.json"
SOCIAL_CACHE_FILE = CACHE_DIR / "official_social_knowledge_base.json"
DEFAULT_CACHE_TTL_HOURS = 12
DEFAULT_SOCIAL_CACHE_TTL_HOURS = 3
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

OPTIONAL_SOCIAL_SOURCES = [
    ("instagram", "KDU Global Instagram", "KDU_GLOBAL_INSTAGRAM_URL"),
    ("tiktok", "KDU Global TikTok", "KDU_GLOBAL_TIKTOK_URL"),
    ("kakaotalk", "KDU Global KakaoTalk", "KDU_GLOBAL_KAKAOTALK_URL"),
    ("facebook", "KDU Global Facebook (Configured)", "KDU_GLOBAL_FACEBOOK_URL"),
    ("youtube", "KDU Global YouTube (Configured)", "KDU_GLOBAL_YOUTUBE_URL"),
]

SOCIAL_ALLOWED_DOMAINS = {
    "facebook": {"facebook.com", "www.facebook.com", "m.facebook.com", "fb.watch"},
    "instagram": {"instagram.com", "www.instagram.com"},
    "tiktok": {"tiktok.com", "www.tiktok.com"},
    "youtube": {"youtube.com", "www.youtube.com", "youtu.be"},
    "kakaotalk": {"kakao.com", "www.kakao.com", "open.kakao.com"},
    "kakao": {"kakao.com", "www.kakao.com", "open.kakao.com"},
}

KDU_GLOBAL_MARKERS = {
    "kdu",
    "kyungdong",
    "kyungdong university",
    "global campus",
    "kdu global",
    "global.kduniv.ac.kr",
    "goseong",
    "gangwon",
}

TARGET_TOPIC_MARKERS = {
    "tuition",
    "fee",
    "fees",
    "scholarship",
    "scholarships",
    "financial aid",
    "dorm",
    "dormitory",
    "housing",
    "accommodation",
    "visa",
    "immigration",
    "residence",
    "admission",
    "admissions",
    "apply",
    "application",
    "documents",
}

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


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme:
        return ""
    return parsed.geturl().rstrip("/")


def _is_allowed_social_url(platform: str, url: str) -> bool:
    normalized = _normalize_url(url)
    if not normalized:
        return False

    parsed = urlparse(normalized)
    hostname = (parsed.hostname or "").lower()
    allowed_domains = SOCIAL_ALLOWED_DOMAINS.get(platform.lower()) or SOCIAL_ALLOWED_DOMAINS.get(platform.lower().replace("talk", ""))
    if not allowed_domains:
        return False

    return hostname in allowed_domains


def _get_effective_social_sources() -> List[OfficialSocialSource]:
    combined = list(OFFICIAL_SOCIAL_SOURCES)
    for platform, label, env_name in OPTIONAL_SOCIAL_SOURCES:
        value = os.getenv(env_name, "").strip()
        if not value:
            continue
        if not _is_allowed_social_url(platform, value):
            continue
        combined.append(
            OfficialSocialSource(
                platform=platform,
                label=label,
                url=value,
                source_page="https://global.kduniv.ac.kr/global/",
            )
        )

    deduped: List[OfficialSocialSource] = []
    seen_urls = set()
    for source in combined:
        normalized = _normalize_url(source.url)
        if not normalized or normalized in seen_urls:
            continue
        seen_urls.add(normalized)
        deduped.append(source)
    return deduped


def _is_kdu_global_relevant_text(text: str) -> bool:
    lowered = text.lower()
    marker_hits = sum(1 for marker in KDU_GLOBAL_MARKERS if marker in lowered)
    return marker_hits >= 2


def _is_target_topic_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in TARGET_TOPIC_MARKERS)


def _infer_social_category(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["tuition", "fee", "fees", "scholarship", "financial aid"]):
        return "fees"
    if any(token in lowered for token in ["dorm", "dormitory", "housing", "accommodation", "facility"]):
        return "campus_life"
    if any(token in lowered for token in ["visa", "immigration", "residence", "arc"]):
        return "student_services"
    if any(token in lowered for token in ["admission", "admissions", "apply", "application", "documents"]):
        return "admissions"
    return "overview"


def _build_social_document(source: OfficialSocialSource, content: str, index: int, category: str) -> dict:
    digest = hashlib.sha1(f"{source.url}:{category}:{index}:{content}".encode("utf-8")).hexdigest()[:16]
    return {
        "id": f"social_{source.platform}_{digest}",
        "content": content,
        "source": f"{source.label} (Official Social)",
        "category": category,
        "url": source.url,
        "title": source.label,
    }


def _extract_social_snippets(text: str, max_items: int = 8) -> List[str]:
    snippets: List[str] = []
    seen = set()

    for paragraph in text.split("\n\n"):
        clean = paragraph.strip()
        if len(clean) < 35 or len(clean) > 950:
            continue

        lowered = clean.lower()
        if lowered in seen:
            continue
        if not _is_kdu_global_relevant_text(clean):
            continue
        if not _is_target_topic_text(clean):
            continue

        seen.add(lowered)
        snippets.append(clean)
        if len(snippets) >= max_items:
            break

    return snippets


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


def _load_cache(cache_file: Path = CACHE_FILE) -> List[dict]:
    if not cache_file.exists():
        return []
    try:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload.get("documents", [])


def _save_cache(documents: Iterable[dict], cache_file: Path = CACHE_FILE) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": int(time.time()),
        "documents": list(documents),
    }
    cache_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_social_documents(force_refresh: bool = False, cache_ttl_hours: int = DEFAULT_SOCIAL_CACHE_TTL_HOURS) -> List[dict]:
    cache_ttl_seconds = max(cache_ttl_hours, 1) * 3600

    if not force_refresh and SOCIAL_CACHE_FILE.exists():
        cache_age = time.time() - SOCIAL_CACHE_FILE.stat().st_mtime
        if cache_age <= cache_ttl_seconds:
            cached_documents = _load_cache(SOCIAL_CACHE_FILE)
            if cached_documents:
                return cached_documents

    documents: List[dict] = []
    for source in _get_effective_social_sources():
        try:
            response = requests.get(
                source.url,
                timeout=HTTP_TIMEOUT_SECONDS,
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            text = _extract_text_from_html(response.text)
            if not text or not _is_kdu_global_relevant_text(text):
                continue

            snippets = _extract_social_snippets(text)
            for index, snippet in enumerate(snippets):
                category = _infer_social_category(snippet)
                documents.append(_build_social_document(source, snippet, index, category))
        except Exception as exc:
            print(f"Warning: failed to fetch social source {source.url}: {exc}")

    if documents:
        _save_cache(documents, SOCIAL_CACHE_FILE)
        return documents

    cached_documents = _load_cache(SOCIAL_CACHE_FILE)
    if cached_documents:
        return cached_documents

    return []


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
        for source in _get_effective_social_sources()
    ]


def load_knowledge_base(
    force_refresh: bool = False,
    cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS,
    include_social: bool = True,
    social_cache_ttl_hours: int = DEFAULT_SOCIAL_CACHE_TTL_HOURS,
) -> List[dict]:
    """Load the university knowledge base from official KDU Global web and verified social channels."""
    cache_ttl_seconds = max(cache_ttl_hours, 1) * 3600

    if not force_refresh and CACHE_FILE.exists():
        cache_age = time.time() - CACHE_FILE.stat().st_mtime
        if cache_age <= cache_ttl_seconds:
            cached_documents = _load_cache()
            if cached_documents:
                if include_social:
                    social_documents = _load_social_documents(force_refresh=False, cache_ttl_hours=social_cache_ttl_hours)
                    return cached_documents + social_documents
                return cached_documents

    documents = []
    for page in OFFICIAL_PAGE_SOURCES:
        try:
            documents.extend(_fetch_page_documents(page))
        except Exception as exc:
            print(f"Warning: failed to fetch {page.url}: {exc}")

    if documents:
        _save_cache(documents)
        if include_social:
            social_documents = _load_social_documents(force_refresh=force_refresh, cache_ttl_hours=social_cache_ttl_hours)
            return documents + social_documents
        return documents

    cached_documents = _load_cache()
    if cached_documents:
        if include_social:
            social_documents = _load_social_documents(force_refresh=False, cache_ttl_hours=social_cache_ttl_hours)
            return cached_documents + social_documents
        return cached_documents

    fallback_documents = FALLBACK_DOCUMENTS.copy()
    if include_social:
        social_documents = _load_social_documents(force_refresh=force_refresh, cache_ttl_hours=social_cache_ttl_hours)
        return fallback_documents + social_documents
    return fallback_documents