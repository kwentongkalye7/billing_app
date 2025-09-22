from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from django.conf import settings
from django.template.loader import render_to_string

from .models import BillingStatement


def _relative_to_media(path: Path) -> str:
    media_root = Path(settings.MEDIA_ROOT)
    try:
        return str(path.relative_to(media_root))
    except ValueError:
        return path.name


def render_statement_pdf(statement: BillingStatement, force_refresh: bool = False) -> str:
    """Render an SOA to PDF via Playwright and return its media-relative path."""

    media_root = Path(settings.MEDIA_ROOT)
    base_dir = Path(settings.PLAYWRIGHT_STORAGE_PATH) if settings.PLAYWRIGHT_STORAGE_PATH else media_root / "pdf"
    output_dir = base_dir / "statements"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{statement.number or f'draft-{statement.pk}'}.pdf"
    output_path = output_dir / filename
    if output_path.exists() and not force_refresh:
        return _relative_to_media(output_path)

    context: Dict[str, Any] = {
        "statement": statement,
        "client": statement.client,
        "engagement": statement.engagement,
        "items": statement.items.all(),
        "generated_by": statement.updated_by or statement.created_by,
        "site_name": settings.SITE_NAME,
    }
    html = render_to_string("statements/soa.html", context)

    from playwright.sync_api import sync_playwright  # Lazy import

    with sync_playwright() as p:
        browser = p.chromium.launch(**settings.PLAYWRIGHT_LAUNCH_OPTIONS)
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()

    return _relative_to_media(output_path)
