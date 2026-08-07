#!/usr/bin/env python3
"""Capture KAYAK 1-adult cheapest open-jaw: NYC in / Chicago out."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "flight_screenshots_nyc_in_chi_out"
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
ROUTE_LABEL = "뉴욕인·시카고아웃"


def fmt_md(iso: str) -> str:
    _y, m, d = iso.split("-")
    return f"{int(m)}월{int(d)}일"


def kayak_url(ret: str) -> str:
    # Open-jaw: SEL→NYC outbound, ORD→SEL return
    return (
        f"https://www.kayak.co.kr/flights/SEL-NYC/{OUTBOUND}/ORD-SEL/{ret}"
        f"/1adults?sort=price_a"
    )


def dismiss_overlays(page) -> None:
    for _ in range(3):
        clicked = page.evaluate(
            """() => {
          const buttons = [...document.querySelectorAll('button, [role="button"]')];
          const target = buttons.find(el => {
            const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
            return /^(동의합니다|모두 동의|Accept all|Accept|Agree)$/i.test(t);
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
          /항공|Air|United|Delta|Korean|Asiana|에어|알래스카|델타|대한|아시아나|에바|아메리칸|터키|캐세이|프론티어|캐나다|제트블루|ANA|JAL/i.test(l)
        ) || '';
        return {
          price: pm[1].replace(/,/g, ''),
          priceText: pm[1] + '원',
          carrier,
          selfTransfer: b.includes('자가 환승'),
        };
      }
      // Fallback: some open-jaw layouts omit the jump link
      const m = text.match(/([\\d,]+)원/);
      if (!m) return null;
      return {
        price: m[1].replace(/,/g, ''),
        priceText: m[1] + '원',
        carrier: '',
        selfTransfer: text.includes('자가 환승'),
      };
    }"""
    )


def wait_results(page, timeout_s: float = 55) -> dict | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        dismiss_overlays(page)
        info = extract_cheapest(page)
        body = page.inner_text("body")
        if info and info.get("price") and ("결과" in body or "완료" in body):
            return info
        time.sleep(0.8)
    return extract_cheapest(page)


def set_badge(page, price_text: str, ret: str) -> None:
    page.evaluate(
        """({ outLabel, retLabel, priceText, routeLabel }) => {
      let badge = document.getElementById('capture-date-badge');
      if (!badge) {
        badge = document.createElement('div');
        badge.id = 'capture-date-badge';
        Object.assign(badge.style, {
          position: 'fixed', top: '8px', left: '8px', right: '8px', zIndex: '2147483647',
          background: 'rgba(20,20,20,0.9)', color: '#fff',
          padding: '10px 12px', borderRadius: '10px',
          font: '600 14px/1.35 \"Noto Sans KR\", \"Segoe UI\", sans-serif',
          boxShadow: '0 4px 16px rgba(0,0,0,.25)', textAlign: 'center'
        });
        document.body.appendChild(badge);
      }
      badge.textContent =
        `${routeLabel} · 1인 ${priceText} · 출국 ${outLabel} · 귀국 ${retLabel}`;
    }""",
        {
            "outLabel": fmt_md(OUTBOUND),
            "retLabel": fmt_md(ret),
            "priceText": price_text,
            "routeLabel": ROUTE_LABEL,
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
        if ((t.includes('ICN') || t.includes('SEL') || t.includes('NYC') || t.includes('JFK') || t.includes('EWR') || t.includes('LGA') || t.includes('ORD'))
            && card.offsetHeight >= 120) break;
      }
      card.scrollIntoView({ block: 'center' });
    }""",
        price_text,
    )
    page.wait_for_timeout(400)
    page.screenshot(path=str(path), full_page=False)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
            print(f"\n=== {ROUTE_LABEL} | {OUTBOUND} → {ret} ===")
            print(url)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeout:
                print("navigation timeout, continuing")
            page.wait_for_timeout(2500)
            dismiss_overlays(page)
            info = wait_results(page)
            dismiss_overlays(page)
            if not info:
                print("FAILED: no price found")
                debug = OUT_DIR / f"FAIL_출국{fmt_md(OUTBOUND)}_귀국{fmt_md(ret)}.png"
                page.screenshot(path=str(debug), full_page=False)
                continue

            fname = f"{info['price']}_출국{fmt_md(OUTBOUND)}_귀국{fmt_md(ret)}.png"
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
