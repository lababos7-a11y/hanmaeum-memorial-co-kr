"""
Playwright 검증 스크립트 - 남양주자연장 갤러리
확인 항목:
  1. #namyangju-gallery 존재
  2. 슬라이드 8장
  3. 썸네일 8개
  4. 카운터 1/8
  5. next 클릭 → 카운터 2/8
  6. prev 클릭 → 카운터 1/8
  7. 썸네일 4번 클릭 → 카운터 4/8
  8. 이미지 src에 namyangju만 포함 (다른 지역 혼입 = 0)
  9. body scrollWidth == viewport (가로 overflow 없음)
 10. 하단 section.py-14 left == 0px
 11. 이미지 404 == 0
 12. console error == 0 (MIME 오류 제외)
 13. 모바일 390px overflow 없음
 14. /natural-burial/ 남양주 카드 이미지 존재 및 200
"""

import sys
from playwright.sync_api import sync_playwright, Error as PlaywrightError

BASE = "http://localhost:3000"
PASS = []
FAIL = []

def check(label, cond, detail=""):
    if cond:
        PASS.append(label)
        print(f"  PASS  {label}")
    else:
        FAIL.append(label)
        print(f"  FAIL  {label}" + (f"  ({detail})" if detail else ""))

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ── 1. 데스크톱 검증 ──────────────────────────────────────
        print("\n[Desktop 1280px] /natural-burial/namyangju/")
        ctx_d = browser.new_context(viewport={"width": 1280, "height": 800})
        page_d = ctx_d.new_page()

        console_errors = []
        image_404 = []
        image_srcs = []

        def on_console(msg):
            if msg.type == "error":
                text = msg.text
                # MIME 오류(common.js 등)는 로컬 알려진 이슈, 무시
                if "MIME" in text or "application/octet-stream" in text:
                    return
                console_errors.append(text)

        def on_response(resp):
            url = resp.url
            if any(ext in url for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
                image_srcs.append(url)
                if resp.status == 404:
                    image_404.append(url)

        page_d.on("console", on_console)
        page_d.on("response", on_response)

        page_d.goto(BASE + "/natural-burial/namyangju/", wait_until="networkidle", timeout=20000)

        # 1. 갤러리 존재
        gallery = page_d.query_selector("#namyangju-gallery")
        check("갤러리 #namyangju-gallery 존재", gallery is not None)

        # 2. 슬라이드 8장
        slides = page_d.query_selector_all(".namyangju-gallery__slide")
        check("슬라이드 8장", len(slides) == 8, f"실제={len(slides)}")

        # 3. 썸네일 8개
        thumbs = page_d.query_selector_all(".namyangju-gallery__thumb")
        check("썸네일 8개", len(thumbs) == 8, f"실제={len(thumbs)}")

        # 4. 카운터 1/8
        cur = page_d.query_selector(".namyangju-gallery__counter-cur")
        tot = page_d.query_selector(".namyangju-gallery__counter-tot")
        cur_val = cur.inner_text().strip() if cur else "?"
        tot_val = tot.inner_text().strip() if tot else "?"
        check("카운터 초기 1/8", cur_val == "1" and tot_val == "8", f"실제={cur_val}/{tot_val}")

        # 5. next 클릭 → 2/8
        btn_next = page_d.query_selector(".namyangju-gallery__arrow--next")
        if btn_next:
            btn_next.click()
            page_d.wait_for_timeout(400)
            cur_val2 = page_d.query_selector(".namyangju-gallery__counter-cur").inner_text().strip()
            check("next 클릭 후 카운터 2/8", cur_val2 == "2", f"실제={cur_val2}")
        else:
            check("next 클릭 후 카운터 2/8", False, "next 버튼 없음")

        # 6. prev 클릭 → 1/8
        btn_prev = page_d.query_selector(".namyangju-gallery__arrow--prev")
        if btn_prev:
            btn_prev.click()
            page_d.wait_for_timeout(400)
            cur_val3 = page_d.query_selector(".namyangju-gallery__counter-cur").inner_text().strip()
            check("prev 클릭 후 카운터 1/8", cur_val3 == "1", f"실제={cur_val3}")
        else:
            check("prev 클릭 후 카운터 1/8", False, "prev 버튼 없음")

        # 7. 썸네일 4번 클릭 → 4/8
        if len(thumbs) >= 4:
            thumbs[3].click()
            page_d.wait_for_timeout(400)
            cur_val4 = page_d.query_selector(".namyangju-gallery__counter-cur").inner_text().strip()
            check("썸네일 4번 클릭 후 카운터 4/8", cur_val4 == "4", f"실제={cur_val4}")
        else:
            check("썸네일 4번 클릭 후 카운터 4/8", False, "썸네일 부족")

        # 8. 이미지 src 다른 지역 혼입 없음
        gallery_imgs = page_d.query_selector_all(".namyangju-gallery__img, .namyangju-gallery__thumb img")
        other_region = [img.get_attribute("src") for img in gallery_imgs
                        if img.get_attribute("src") and "namyangju" not in img.get_attribute("src")]
        check("갤러리 이미지 다른 지역 혼입 0", len(other_region) == 0,
              f"혼입={other_region[:3]}")

        # 9. 가로 overflow 없음
        overflow = page_d.evaluate("""() => {
            return document.body.scrollWidth <= window.innerWidth;
        }""")
        check("가로 overflow 없음 (데스크톱)", overflow,
              f"scrollWidth={page_d.evaluate('document.body.scrollWidth')} innerWidth={page_d.evaluate('window.innerWidth')}")

        # 10. 하단 section.py-14 정렬 (left == 0)
        section_left = page_d.evaluate("""() => {
            const s = document.querySelector('section.py-14');
            if (!s) return null;
            return s.getBoundingClientRect().left;
        }""")
        check("하단 section.py-14 left==0", section_left is not None and abs(section_left) < 2,
              f"left={section_left}")

        # 11. 이미지 404 == 0
        check("이미지 404 == 0", len(image_404) == 0, f"404={image_404}")

        # 12. console error == 0
        check("console error == 0", len(console_errors) == 0, f"errors={console_errors[:3]}")

        ctx_d.close()

        # ── 2. 모바일 390px 검증 ──────────────────────────────────
        print("\n[Mobile 390px] /natural-burial/namyangju/")
        ctx_m = browser.new_context(viewport={"width": 390, "height": 844})
        page_m = ctx_m.new_page()
        page_m.goto(BASE + "/natural-burial/namyangju/", wait_until="networkidle", timeout=20000)

        overflow_m = page_m.evaluate("""() => {
            return document.body.scrollWidth <= window.innerWidth;
        }""")
        check("가로 overflow 없음 (모바일 390px)", overflow_m,
              f"scrollWidth={page_m.evaluate('document.body.scrollWidth')} innerWidth=390")

        # 갤러리 존재 모바일
        gallery_m = page_m.query_selector("#namyangju-gallery")
        check("갤러리 존재 (모바일)", gallery_m is not None)

        ctx_m.close()

        # ── 3. /natural-burial/ 남양주 카드 이미지 확인 ──────────
        print("\n[Desktop 1280px] /natural-burial/ 카드 이미지")
        ctx_c = browser.new_context(viewport={"width": 1280, "height": 800})
        page_c = ctx_c.new_page()
        card_404 = []

        def on_resp_c(resp):
            if "namyangju" in resp.url and resp.status == 404:
                card_404.append(resp.url)

        page_c.on("response", on_resp_c)
        page_c.goto(BASE + "/natural-burial/", wait_until="networkidle", timeout=20000)

        # 남양주 카드 img 존재 및 src
        card_img = page_c.query_selector("a[href*='namyangju'] img, [href*='namyangju'] img")
        if card_img is None:
            # 더 넓게 찾기
            card_img = page_c.evaluate("""() => {
                const links = document.querySelectorAll('a[href*="namyangju"]');
                for (const a of links) {
                    const img = a.querySelector('img');
                    if (img) return img.src;
                }
                return null;
            }""")
            check("남양주 카드 이미지 src 확인", card_img is not None and "namyangju" in str(card_img),
                  f"src={card_img}")
        else:
            src = card_img.get_attribute("src")
            check("남양주 카드 이미지 src 확인", src is not None and "namyangju" in src, f"src={src}")

        check("남양주 카드 이미지 404 없음", len(card_404) == 0, f"404={card_404}")

        ctx_c.close()
        browser.close()

    # ── 최종 결과 ───────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"PASS: {len(PASS)}  /  FAIL: {len(FAIL)}")
    if FAIL:
        print("\n실패 항목:")
        for f in FAIL:
            print(f"  ✗ {f}")
        print("\n결과: FAIL")
        sys.exit(1)
    else:
        print("\n결과: ALL PASS ✅")
        sys.exit(0)

if __name__ == "__main__":
    run()
