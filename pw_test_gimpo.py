import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        errors = []
        img404 = []
        
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        
        async def handle_response(response):
            if response.status == 404:
                url = response.url
                if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    img404.append(url)
        
        page.on("response", handle_response)
        
        await page.goto("http://localhost:3000/natural-burial/gimpo/", wait_until="networkidle")
        
        # 1. 두 갤러리 존재 확인
        cheongsol = await page.query_selector("#cheongsol-gallery")
        aegibong  = await page.query_selector("#aegibong-gallery")
        print(f"청솔 갤러리 존재: {cheongsol is not None}")
        print(f"애기봉 갤러리 존재: {aegibong is not None}")
        
        # 2. 슬라이드 수
        cs_slides = await page.query_selector_all(".cheongsol-gallery__slide")
        ab_slides = await page.query_selector_all(".aegibong-gallery__slide")
        print(f"청솔 슬라이드 수: {len(cs_slides)}")
        print(f"애기봉 슬라이드 수: {len(ab_slides)}")
        
        # 3. 썸네일 수
        cs_thumbs = await page.query_selector_all(".cheongsol-gallery__thumb")
        ab_thumbs = await page.query_selector_all(".aegibong-gallery__thumb")
        print(f"청솔 썸네일 수: {len(cs_thumbs)}")
        print(f"애기봉 썸네일 수: {len(ab_thumbs)}")
        
        # 4. 카운터 초기값
        cs_counter = await page.text_content(".cheongsol-gallery__counter-cur")
        cs_total   = await page.text_content(".cheongsol-gallery__counter-tot")
        ab_counter = await page.text_content(".aegibong-gallery__counter-cur")
        ab_total   = await page.text_content(".aegibong-gallery__counter-tot")
        print(f"청솔 카운터: {cs_counter}/{cs_total}")
        print(f"애기봉 카운터: {ab_counter}/{ab_total}")
        
        # 5. 청솔 next 클릭 → 청솔만 변경
        await page.click(".cheongsol-gallery__arrow--next")
        await page.wait_for_timeout(400)
        cs_after = await page.text_content(".cheongsol-gallery__counter-cur")
        ab_after = await page.text_content(".aegibong-gallery__counter-cur")
        print(f"청솔 클릭 후 청솔: {cs_after} (기대: 2)")
        print(f"청솔 클릭 후 애기봉: {ab_after} (기대: 1 - 변화 없어야)")
        
        # 6. 애기봉 next 클릭 → 애기봉만 변경
        await page.click(".aegibong-gallery__arrow--next")
        await page.wait_for_timeout(400)
        cs_after2 = await page.text_content(".cheongsol-gallery__counter-cur")
        ab_after2 = await page.text_content(".aegibong-gallery__counter-cur")
        print(f"애기봉 클릭 후 청솔: {cs_after2} (기대: 2 - 변화 없어야)")
        print(f"애기봉 클릭 후 애기봉: {ab_after2} (기대: 2)")
        
        # 7. 이미지 src 혼합 검사
        cs_srcs = await page.eval_on_selector_all(".cheongsol-gallery__img", "imgs => imgs.map(i => i.src)")
        ab_srcs = await page.eval_on_selector_all(".aegibong-gallery__img", "imgs => imgs.map(i => i.src)")
        mix_cs = any("aegibong" in s for s in cs_srcs)
        mix_ab = any("cheongsol" in s for s in ab_srcs)
        print(f"청솔 갤러리 aegibong 혼입: {mix_cs} (기대: False)")
        print(f"애기봉 갤러리 cheongsol 혼입: {mix_ab} (기대: False)")
        
        # 8. 가로 overflow (데스크탑)
        body_width = await page.evaluate("() => document.body.scrollWidth")
        print(f"body scrollWidth: {body_width} / viewport: 1280 / overflow: {body_width > 1280}")
        
        # 9. 하단 section 정렬 (py-14)
        bottom_left = await page.eval_on_selector("section.py-14", "el => Math.round(el.getBoundingClientRect().left)")
        print(f"하단 section left: {bottom_left}px (기대: 0)")
        
        # 10. FAQ h2 정렬
        try:
            faq_left = await page.eval_on_selector(".bg-white.border.border-gray-200 h2", "el => Math.round(el.getBoundingClientRect().left)")
            print(f"FAQ H2 left: {faq_left}px")
        except:
            print("FAQ H2: not found")
        
        # 11. console error, 이미지 404
        print(f"console error 수: {len(errors)}", errors[:3] if errors else "")
        print(f"이미지 404 수: {len(img404)}", img404[:3] if img404 else "")
        
        # 12. 모바일 가로 overflow
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(300)
        mobile_width = await page.evaluate("() => document.body.scrollWidth")
        print(f"모바일 body scrollWidth: {mobile_width} / viewport: 390 / overflow: {mobile_width > 390}")
        
        # 13. 썸네일 가로 스크롤 여부
        cs_scroll = await page.eval_on_selector(".cheongsol-gallery__thumbs", "el => el.scrollWidth > el.clientWidth")
        ab_scroll = await page.eval_on_selector(".aegibong-gallery__thumbs", "el => el.scrollWidth > el.clientWidth")
        print(f"청솔 썸네일 가로스크롤: {cs_scroll}")
        print(f"애기봉 썸네일 가로스크롤: {ab_scroll}")
        
        await browser.close()
        print("--- 검증 완료 ---")

asyncio.run(main())
