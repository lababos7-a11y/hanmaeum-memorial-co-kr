"""
화성자연장 Playwright 검증 (sync API)
9장 갤러리, IIFE JS, 카드 이미지 포함
"""
from playwright.sync_api import sync_playwright
import sys

BASE = "http://localhost:3000"
TOTAL = 9
results = []
console_errors = []

def check(name, cond, detail=""):
    ok = bool(cond)
    mark = "✅ PASS" if ok else "❌ FAIL"
    msg = f"  {mark}  {name}"
    if detail:
        msg += f"  [{detail}]"
    print(msg)
    results.append((name, ok))
    return ok

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()

    # console error 수집 (MIME 오류 제외)
    def on_console(msg):
        if msg.type == "error" and "MIME" not in msg.text:
            console_errors.append(msg.text)
    page.on("console", on_console)

    # 404 이미지 추적
    img_404 = []
    def on_response(resp):
        if resp.status == 404 and any(ext in resp.url for ext in [".jpg", ".png", ".webp", ".gif"]):
            img_404.append(resp.url)
    page.on("response", on_response)

    # ─── 화성 상세페이지 ───────────────────────────────────
    print("\n[1] /natural-burial/hwaseong/ 페이지")
    page.goto(f"{BASE}/natural-burial/hwaseong/", wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(800)

    # 1. 갤러리 컨테이너
    gallery = page.query_selector("#hwaseong-gallery")
    check("갤러리 컨테이너 #hwaseong-gallery 존재", gallery)

    # 2. 슬라이드 수
    slides = page.query_selector_all(".hwaseong-gallery__slide")
    check(f"슬라이드 수 = {TOTAL}", len(slides) == TOTAL, f"실제={len(slides)}")

    # 3. 썸네일 수
    thumbs = page.query_selector_all(".hwaseong-gallery__thumb")
    check(f"썸네일 수 = {TOTAL}", len(thumbs) == TOTAL, f"실제={len(thumbs)}")

    # 4. 카운터-tot
    tot_el = page.query_selector(".hwaseong-gallery__counter-tot")
    tot_val = tot_el.inner_text().strip() if tot_el else ""
    check(f"카운터 tot = {TOTAL}", tot_val == str(TOTAL), f"실제='{tot_val}'")

    # 5. 카운터-cur 초기값
    cur_el = page.query_selector(".hwaseong-gallery__counter-cur")
    cur_val = cur_el.inner_text().strip() if cur_el else ""
    check("카운터 cur 초기값 = 1", cur_val == "1", f"실제='{cur_val}'")

    # 6. 첫 이미지 eager
    first_img = page.query_selector(".hwaseong-gallery__slide[data-idx='0'] img")
    loading = first_img.get_attribute("loading") if first_img else ""
    check("첫 슬라이드 loading=eager", loading == "eager", f"실제='{loading}'")

    # 7. 이미지 src hwaseong-01 존재 (Vite 해시 변환 허용: hwaseong-01 포함 or /assets/ 경로)
    src = first_img.get_attribute("src") if first_img else ""
    check("첫 슬라이드 src에 hwaseong-01 포함", "hwaseong-01" in src, f"실제='{src}'")

    # 8. 마지막 슬라이드 src=hwaseong-09 (Vite 해시 변환 허용)
    last_img = page.query_selector(f".hwaseong-gallery__slide[data-idx='{TOTAL-1}'] img")
    last_src = last_img.get_attribute("src") if last_img else ""
    check(f"마지막 슬라이드 src에 hwaseong-{TOTAL:02d} 포함", f"hwaseong-{TOTAL:02d}" in last_src, f"실제='{last_src}'")

    # 9. 화살표 prev/next
    btn_prev = page.query_selector(".hwaseong-gallery__arrow--prev")
    btn_next = page.query_selector(".hwaseong-gallery__arrow--next")
    check("화살표 prev 존재", btn_prev)
    check("화살표 next 존재", btn_next)

    # 10. Next 클릭 → cur=2
    if btn_next:
        btn_next.click()
        page.wait_for_timeout(450)
        cur2 = page.query_selector(".hwaseong-gallery__counter-cur")
        cur2_val = cur2.inner_text().strip() if cur2 else ""
        check("Next 클릭 후 cur = 2", cur2_val == "2", f"실제='{cur2_val}'")

    # 11. 썸네일 클릭 → cur=5
    if len(thumbs) >= 5:
        thumbs[4].click()
        page.wait_for_timeout(450)
        cur5 = page.query_selector(".hwaseong-gallery__counter-cur")
        cur5_val = cur5.inner_text().strip() if cur5 else ""
        check("썸네일[4] 클릭 후 cur = 5", cur5_val == "5", f"실제='{cur5_val}'")

    # 12. 스와이프 (TouchEvent evaluate)
    main_area = page.query_selector(".hwaseong-gallery__main")
    if main_area:
        box = main_area.bounding_box()
        if box:
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2
            page.evaluate("""([x, y]) => {
                var el = document.querySelector('.hwaseong-gallery__main');
                if (!el) return;
                el.dispatchEvent(new TouchEvent('touchstart', {
                    touches: [new Touch({identifier:1, target:el, clientX:x+60, clientY:y})],
                    changedTouches: [new Touch({identifier:1, target:el, clientX:x+60, clientY:y})],
                    bubbles:true
                }));
                el.dispatchEvent(new TouchEvent('touchend', {
                    touches: [],
                    changedTouches: [new Touch({identifier:1, target:el, clientX:x-40, clientY:y})],
                    bubbles:true
                }));
            }""", [cx, cy])
            page.wait_for_timeout(450)
            swipe_cur = page.query_selector(".hwaseong-gallery__counter-cur")
            swipe_val = swipe_cur.inner_text().strip() if swipe_cur else ""
            check("스와이프(좌) 후 카운터 변화", swipe_val != "5", f"실제='{swipe_val}'")
        else:
            check("스와이프 - bounding_box 없음", False)
    else:
        check("스와이프 - main 요소 없음", False)

    # 13. 이미지 404 없음
    check(f"이미지 404 = 0", len(img_404) == 0, f"404 목록: {img_404}")

    # 14. console error = 0
    check(f"console error = 0", len(console_errors) == 0, f"에러: {console_errors[:3]}")

    # ─── 카테고리 페이지 ───────────────────────────────────
    print("\n[2] /natural-burial/ 카테고리 페이지 — 화성 카드")
    page.goto(f"{BASE}/natural-burial/", wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(600)

    # 15. 화성 카드 이미지 src (Vite 해시 변환 허용: hwaseong-01 포함)
    hwaseong_card = page.query_selector("a[href='/natural-burial/hwaseong/'] img")
    card_src = hwaseong_card.get_attribute("src") if hwaseong_card else ""
    check("화성 카드 img src에 hwaseong-01 포함", "hwaseong-01" in card_src, f"실제='{card_src}'")

    # 16. 화성 카드 이미지 HTTP 200
    if card_src:
        resp = page.goto(f"{BASE}{card_src}")
        check("화성 카드 이미지 HTTP 200", resp and resp.status == 200, f"status={resp.status if resp else 'None'}")

    browser.close()

# ─── 결과 요약 ───────────────────────────────────────────
print("\n" + "="*50)
print(f"화성자연장 Playwright 검증 결과")
print("="*50)
passed = sum(1 for _, ok in results if ok)
total_tests = len(results)
print(f"  {passed}/{total_tests} PASS")
if passed == total_tests:
    print("  ✅ ALL PASS")
else:
    print("  ❌ 일부 실패:")
    for name, ok in results:
        if not ok:
            print(f"     - {name}")
print("="*50)
sys.exit(0 if passed == total_tests else 1)
