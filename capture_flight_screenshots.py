#!/usr/bin/env python3
"""Capture KAYAK 1-adult cheapest flight cards with airline + price."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "flight_screenshots"
USER_DATA_DIR = ROOT / ".browser_profile_capture"
OUTBOUND = "2026-09-24"
RETURN_DATES = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]


def fmt_md(iso: str) -> str:
    _y, m, d = iso.split("-")
    return f"{int(m)}월{int(d)}일"


def kayak_url(ret: str) -> str:
    return (
        f"https://www.kayak.co.kr/flights/SEL-ORD/{OUTBOUND}/{ret}/1adults?sort=price_a"
    )


def dismiss_overlays(page) -> None:
    for _ in range(3):
        clicked = page.evaluate(
            """() => {
          const buttons = [...document.querySelectorAll('button, [role="button"], a')];
          const target = buttons.find(el => {
            const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
            return /동의합니다|모두 동의|Accept all|Accept|Agree|확인|닫기/.test(t);
          });
          if (target) { target.click(); return target.innerText.trim().slice(0, 40); }
          return null;
        }"""
        )
        if not clicked:
            break
        print(f"  dismissed: {clicked}")
        page.wait_for_timeout(700)


def extract_cheapest(page) -> dict | None:
    return page.evaluate(
        """() => {
      const text = document.body.innerText || '';
      const blocks = text.split('다음 검색 결과로 이동').slice(1);
      for (const b of blocks) {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) continue;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l =>
          /항공|Air|United|Delta|Korean|Asiana|에어|알래스카|델타|대한|아시아나|에바|아메리칸|터키|캐세이|프론티어|캐나다/i.test(l)
        ) || '';
        return {
          price: pm[1].replace(/,/g, ''),
          priceText: pm[1] + '원',
          carrier,
          selfTransfer: b.includes('자가 환승'),
        };
      }
      return null;
    }"""
    )


def wait_results(page, timeout_s: float = 50) -> dict | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        dismiss_overlays(page)
        info = extract_cheapest(page)
        if info and info.get("price"):
            body = page.inner_text("body")
            if "동의합니다" in body and body.count("동의합니다") > 0:
                # still overlaying; keep trying dismiss
                dismiss_overlays(page)
            return info
        time.sleep(0.7)
    return extract_cheapest(page)


def screenshot_result(page, path: Path, price_text: str) -> None:
    dismiss_overlays(page)
    page.wait_for_timeout(500)
    # Hide leftover cookie / privacy dialogs if any remain.
    page.evaluate(
        """() => {
      [...document.querySelectorAll('div,section,aside')].forEach(el => {
        const t = el.innerText || '';
        if (t.includes('동의합니다') && t.includes('쿠키') && el.offsetHeight > 80) {
          el.style.display = 'none';
        }
      });
      [...document.querySelectorAll('*')].forEach(el => {
        const t = el.textContent || '';
        if ((t.includes('Visit the USA') || t.includes('미국, 세상')) &&
            el.offsetHeight > 120 && el.offsetHeight < 600 && el.children.length < 30) {
          el.style.display = 'none';
        }
      });
    }"""
    )

    # Prefer clipping a card that includes airline + price; include nearby header dates.
    clip = page.evaluate(
        """(priceText) => {
      const leaves = [...document.querySelectorAll('div,span,p')].filter(e =>
        e.textContent && e.textContent.trim() === priceText && e.children.length === 0
      );
      if (!leaves.length) return null;
      let card = leaves[0];
      for (let i = 0; i < 16; i++) {
        if (!card.parentElement) break;
        card = card.parentElement;
        const t = card.innerText || '';
        if (t.includes('ICN') && t.includes('ORD') && card.offsetHeight >= 140) break;
      }
      card.scrollIntoView({ block: 'center', inline: 'nearest' });
      const r = card.getBoundingClientRect();
      // Expand upward a bit to catch date chips if nearby
      const y = Math.max(0, r.y - 70);
      const height = Math.min(window.innerHeight - y - 8, r.height + 90);
      const x = Math.max(0, r.x - 6);
      const width = Math.min(window.innerWidth - x - 6, r.width + 12);
      return { x, y, width, height };
    }""",
        price_text,
    )
    page.wait_for_timeout(300)

    # Also capture the date text into a small overlay so filename dates are visible in image.
    page.evaluate(
        """({ outLabel, retLabel, priceText }) => {
      let badge = document.getElementById('capture-date-badge');
      if (!badge) {
        badge = document.createElement('div');
        badge.id = 'capture-date-badge';
        Object.assign(badge.style, {
          position: 'fixed', top: '8px', left: '8px', zIndex: '2147483647',
          background: 'rgba(20,20,20,0.88)', color: '#fff',
          padding: '10px 12px', borderRadius: '10px',
          font: '600 14px/1.35 \"Noto Sans KR\", sans-serif',
          boxShadow: '0 4px 16px rgba(0,0,0,.25)'
        });
        document.body.appendChild(badge);
      }
      badge.textContent = `1인 ${priceText} · 출국 ${outLabel} · 귀국 ${retLabel}`;
    }""",
        {
            "outLabel": fmt_md(OUTBOUND),
            "retLabel": path.stem.split("_귀국")[-1].replace(".png", "")
            if False
            else "",
            "priceText": price_text,
        },
    )


def set_badge(page, price_text: str, ret: str) -> None:
    page.evaluate(
        """({ outLabel, retLabel, priceText }) => {
      let badge = document.getElementById('capture-date-badge');
      if (!badge) {
        badge = document.createElement('div');
        badge.id = 'capture-date-badge';
        Object.assign(badge.style, {
          position: 'fixed', top: '8px', left: '8px', right: '8px', zIndex: '2147483647',
          background: 'rgba(20,20,20,0.9)', color: '#fff',
          padding: '10px 12px', borderRadius: '10px',
          font: '600 15px/1.35 \"Noto Sans KR\", \"Segoe UI\", sans-serif',
          boxShadow: '0 4px 16px rgba(0,0,0,.25)', textAlign: 'center'
        });
        document.body.appendChild(badge);
      }
      badge.textContent = `1인 ${priceText} · 출국 ${outLabel} · 귀국 ${retLabel}`;
    }""",
        {
            "outLabel": fmt_md(OUTBOUND),
            "retLabel": fmt_md(ret),
            "priceText": price_text,
        },
    )


def screenshot_result_clean(page, path: Path, price_text: str, ret: str) -> None:
    dismiss_overlays(page)
    page.evaluate(
        """() => {
      [...document.querySelectorAll('div,section,aside')].forEach(el => {
        const t = el.innerText || '';
        if (t.includes('동의합니다') && (t.includes('쿠키') || t.includes('개인정보')) && el.offsetHeight > 80) {
          el.style.display = 'none';
        }
      });
      [...document.querySelectorAll('*')].forEach(el => {
        const t = el.textContent || '';
        if ((t.includes('Visit the USA') || t.includes('미국, 세상')) &&
            el.offsetHeight > 120 && el.offsetHeight < 600 && el.children.length < 30) {
          el.style.display = 'none';
        }
      });
    }"""
    )
    set_badge(page, price_text, ret)

    # Scroll price into view then take viewport screenshot so badge + card are both visible.
    page.evaluate(
        """(priceText) => {
      const leaf = [...document.querySelectorAll('div,span,p')].find(e =>
        e.textContent && e.textContent.trim() === priceText && e.children.length === 0
      );
      if (!leaf) return;
      let card = leaf;
      for (let i = 0; i < 16; i++) {
        if (!card.parentElement) break;
        card = card.parentElement;
        const t = card.innerText || '';
        if (t.includes('ICN') && t.includes('ORD') && card.offsetHeight >= 140) break;
      }
      card.scrollIntoView({ block: 'center' });
    }""",
        price_text,
    )
    page.wait_for_timeout(400)
    page.screenshot(path=str(path), full_page=False)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clear previous captures so we only keep clean ones.
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    saved: list[str] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 430, "height": 920},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        for ret in RETURN_DATES:
            url = kayak_url(ret)
            print(f"\n=== {OUTBOUND} → {ret} ===")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeout:
                print("navigation timeout, continuing")
            page.wait_for_timeout(2000)
            dismiss_overlays(page)
            info = wait_results(page)
            dismiss_overlays(page)
            if not info:
                print("FAILED: no price found")
                debug = OUT_DIR / f"FAIL_출국{fmt_md(OUTBOUND)}_귀국{fmt_md(ret)}.png"
                page.screenshot(path=str(debug), full_page=False)
                continue

            price = info["price"]
            fname = f"{price}_출국{fmt_md(OUTBOUND)}_귀국{fmt_md(ret)}.png"
            path = OUT_DIR / fname
            screenshot_result_clean(page, path, info["priceText"], ret)
            print(
                f"saved {path.name} | {info.get('priceText')} | {info.get('carrier')} "
                f"| selfTransfer={info.get('selfTransfer')}"
            )
            saved.append(path.name)

        context.close()

    print("\nDone:")
    for name in saved:
        print(" -", name)
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
