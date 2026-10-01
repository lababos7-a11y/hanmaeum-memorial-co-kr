"""
Playwright 검증 스크립트 — 양평자연장 갤러리 (16개 항목)
sync API 버전 (yangju 패턴 동일)
"""
import sys
from playwright.sync_api import sync_playwright

BASE  = "http://localhost:3000"
TOTAL = 8
REGION = "yangpyeong"

PASS = []
FAIL = []

def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"  ✅ PASS  {name}")
    else:
        FAIL.append(name)
        print(f"  ❌ FAIL  {name}" + (f"  ({detail})" if detail else ""))

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ── 1. 데스크톱 1280px ─────────────────────────────────
        print(f"\n[Desktop 1280px] /natural-burial/{REGION}/")
        ctx_d = browser.new_context(viewport={"width": 1280, "height": 800})
        page_d = ctx_d.new_page()

        console_errors = []
        image_404 = []

        def on_console(msg):
            if msg.type == "error":
                text = msg.text
                # MIME 오류는 common.js 누락 문제 (기존 사이트 공통) — 갤러리 무관, 필터링
                if "MIME" in text or "application/octet-stream" in text:
                    return
                console_errors.append(text)

        def on_response(resp):
            url = resp.url
            if any(ext in url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                if resp.status == 404:
                    image_404.append(url)

        page_d.on("console", on_console)
        page_d.on("response", on_response)
        page_d.goto(BASE + f"/natural-burial/{REGION}/", wait_until="networkidle", timeout=20000)

        # 1. 갤러리 존재
        gallery = page_d.query_selector(f"#yangpyeong-gallery")
        check("갤러리 #yangpyeong-gallery 존재", gallery is not None)

        # 2. 슬라이드 8장
        slides = page_d.query_selector_all(".yangpyeong-gallery__slide")
        check(f"슬라이드 {TOTAL}장", len(slides) == TOTAL, f"실제={len(slides)}")

        # 3. 썸네일 8개
        thumbs = page_d.query_selector_all(".yangpyeong-gallery__thumb")
        check(f"썸네일 {TOTAL}개", len(thumbs) == TOTAL, f"실제={len(thumbs)}")

        # 4. 카운터 1/8
        cur = page_d.query_selector(".yangpyeong-gallery__counter-cur")
        tot = page_d.query_selector(".yangpyeong-gallery__counter-tot")
        cur_val = cur.inner_text().strip() if cur else "?"
        tot_val = tot.inner_text().strip() if tot else "?"
        check(f"카운터 초기 1/{TOTAL}", cur_val == "1" and tot_val == str(TOTAL),
              f"실제={cur_val}/{tot_val}")

        # 5. next 클릭 → 2/8
        btn_next = page_d.query_selector(".yangpyeong-gallery__arrow--next")
        if btn_next:
            btn_next.click()
            page_d.wait_for_timeout(400)
            cur_val2 = page_d.query_selector(".yangpyeong-gallery__counter-cur").inner_text().strip()
            check(f"next 클릭 후 카운터 2/{TOTAL}", cur_val2 == "2", f"실제={cur_val2}")
        else:
            check(f"next 클릭 후 카운터 2/{TOTAL}", False, "next 버튼 없음")

        # 6. prev 클릭 → 1/8
        btn_prev = page_d.query_selector(".yangpyeong-gallery__arrow--prev")
        if btn_prev:
            btn_prev.click()
            page_d.wait_for_timeout(400)
            cur_val3 = page_d.query_selector(".yangpyeong-gallery__counter-cur").inner_text().strip()
            check(f"prev 클릭 후 카운터 1/{TOTAL}", cur_val3 == "1", f"실제={cur_val3}")
        else:
            check(f"prev 클릭 후 카운터 1/{TOTAL}", False, "prev 버튼 없음")

        # 7. 썸네일 4번째 클릭 → 4/8
        if len(thumbs) >= 4:
            thumbs[3].click()
            page_d.wait_for_timeout(400)
            cur_val4 = page_d.query_selector(".yangpyeong-gallery__counter-cur").inner_text().strip()
            check(f"썸네일 4번 클릭 후 카운터 4/{TOTAL}", cur_val4 == "4", f"실제={cur_val4}")
        else:
            check(f"썸네일 4번 클릭 후 카운터 4/{TOTAL}", False, "썸네일 부족")

        # 8. 갤러리 이미지 다른 지역 혼입 없음
        gallery_imgs = page_d.query_selector_all(
            ".yangpyeong-gallery__img, .yangpyeong-gallery__thumb img"
        )
        other_region = [
            img.get_attribute("src") for img in gallery_imgs
            if img.get_attribute("src") and REGION not in img.get_attribute("src")
        ]
        check("갤러리 이미지 다른 지역 혼입 0", len(other_region) == 0,
              f"혼입={other_region[:3]}")

        # 9. 가로 overflow 없음
        overflow = page_d.evaluate("() => document.body.scrollWidth <= window.innerWidth")
        check("가로 overflow 없음 (데스크톱)", overflow,
              f"scrollWidth={page_d.evaluate('document.body.scrollWidth')}")

        # 10. 하단 section.py-14 left ≈ 0
        section_left = page_d.evaluate("""() => {
            const s = document.querySelector('section.py-14');
            if (!s) return null;
            return s.getBoundingClientRect().left;
        }""")
        check("하단 section.py-14 left==0", section_left is not None and abs(section_left) < 2,
              f"left={section_left}")

        # 11. 이미지 404 == 0
        check("이미지 404 == 0", len(image_404) == 0, f"404={image_404}")

        # 12. console error == 0 (MIME 제외)
        check("console error == 0", len(console_errors) == 0, f"errors={console_errors[:3]}")

        ctx_d.close()

        # ── 2. 모바일 390px ───────────────────────────────────
        print(f"\n[Mobile 390px] /natural-burial/{REGION}/")
        ctx_m = browser.new_context(viewport={"width": 390, "height": 844})
        page_m = ctx_m.new_page()
        page_m.goto(BASE + f"/natural-burial/{REGION}/", wait_until="networkidle", timeout=20000)

        # 13. 가로 overflow 없음 (모바일)
        overflow_m = page_m.evaluate("() => document.body.scrollWidth <= window.innerWidth")
        check("가로 overflow 없음 (모바일 390px)", overflow_m,
              f"scrollWidth={page_m.evaluate('document.body.scrollWidth')}")

        # 14. 모바일 갤러리 존재 + swipe
        gallery_m = page_m.query_selector("#yangpyeong-gallery")
        check("갤러리 존재 (모바일)", gallery_m is not None)

        # swipe: TouchEvent dispatchEvent 방식
        slides_el = page_m.query_selector(".yangpyeong-gallery__slides")
        if slides_el:
            box = slides_el.bounding_box()
            if box:
                mid_y   = box["y"] + box["height"] / 2
                start_x = box["x"] + box["width"] * 0.75
                end_x   = box["x"] + box["width"] * 0.25
                page_m.evaluate(f"""() => {{
                    var el = document.querySelector('.yangpyeong-gallery__main');
                    if (!el) return;
                    function mkTouch(x, y) {{
                        return new Touch({{identifier: 1, target: el, clientX: x, clientY: y,
                                          screenX: x, screenY: y, pageX: x, pageY: y}});
                    }}
                    el.dispatchEvent(new TouchEvent('touchstart', {{
                        bubbles: true, cancelable: true,
                        touches: [mkTouch({start_x}, {mid_y})],
                        changedTouches: [mkTouch({start_x}, {mid_y})]
                    }}));
                    el.dispatchEvent(new TouchEvent('touchend', {{
                        bubbles: true, cancelable: true,
                        touches: [],
                        changedTouches: [mkTouch({end_x}, {mid_y})]
                    }}));
                }}""")
                page_m.wait_for_timeout(500)
                mcur = page_m.query_selector(".yangpyeong-gallery__counter-cur")
                mcur_val = mcur.inner_text().strip() if mcur else "?"
                check("모바일 swipe → 다음 슬라이드 2", mcur_val == "2",
                      f"카운터={mcur_val}")
            else:
                check("모바일 swipe → 다음 슬라이드 2", False, "bounding_box 없음")
        else:
            check("모바일 swipe → 다음 슬라이드 2", False, "slides 없음")

        ctx_m.close()

        # ── 3. /natural-burial/ 양평 카드 확인 ────────────────
        print(f"\n[Desktop 1280px] /natural-burial/ 양평 카드 이미지")
        ctx_c = browser.new_context(viewport={"width": 1280, "height": 800})
        page_c = ctx_c.new_page()
        card_404 = []

        def on_resp_c(resp):
            if REGION in resp.url and resp.status == 404:
                card_404.append(resp.url)

        page_c.on("response", on_resp_c)
        page_c.goto(BASE + "/natural-burial/", wait_until="networkidle", timeout=20000)

        # 15. 카드 이미지 src 확인
        card_src = page_c.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="yangpyeong"]');
            for (const a of links) {
                const img = a.querySelector('img');
                if (img) return img.getAttribute('src');
            }
            return null;
        }""")
        check("양평 카드 이미지 src=yangpyeong-01.jpg",
              card_src is not None and "yangpyeong-01" in str(card_src),
              f"src={card_src}")

        # 16. 카드 이미지 404 없음
        check("양평 카드 이미지 404 없음", len(card_404) == 0, f"404={card_404}")

        ctx_c.close()
        browser.close()

    # ── 최종 결과 ──────────────────────────────────────────────
    print(f"\n{'='*55}")
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
