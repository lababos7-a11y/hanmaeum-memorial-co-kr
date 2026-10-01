const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  const img404 = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('response', r => { if (r.status() === 404 && r.url().match(/\.(jpg|jpeg|png|webp)/i)) img404.push(r.url()); });

  await page.goto('http://localhost:3000/natural-burial/gimpo/', { waitUntil: 'networkidle' });

  // 1. 두 갤러리 존재 확인
  const cheongsol = await page.$('#cheongsol-gallery');
  const aegibong  = await page.$('#aegibong-gallery');
  console.log('청솔 갤러리 존재:', !!cheongsol);
  console.log('애기봉 갤러리 존재:', !!aegibong);

  // 2. 슬라이드 수
  const csSlides = await page.$$('.cheongsol-gallery__slide');
  const abSlides = await page.$$('.aegibong-gallery__slide');
  console.log('청솔 슬라이드 수:', csSlides.length);
  console.log('애기봉 슬라이드 수:', abSlides.length);

  // 3. 썸네일 수
  const csThumbs = await page.$$('.cheongsol-gallery__thumb');
  const abThumbs = await page.$$('.aegibong-gallery__thumb');
  console.log('청솔 썸네일 수:', csThumbs.length);
  console.log('애기봉 썸네일 수:', abThumbs.length);

  // 4. 카운터 초기값
  const csCounter = await page.textContent('.cheongsol-gallery__counter-cur');
  const csTotal   = await page.textContent('.cheongsol-gallery__counter-tot');
  const abCounter = await page.textContent('.aegibong-gallery__counter-cur');
  const abTotal   = await page.textContent('.aegibong-gallery__counter-tot');
  console.log('청솔 카운터:', csCounter + '/' + csTotal);
  console.log('애기봉 카운터:', abCounter + '/' + abTotal);

  // 5. 청솔 next 클릭 → 청솔만 변경, 애기봉 그대로
  await page.click('.cheongsol-gallery__arrow--next');
  await page.waitForTimeout(400);
  const csCounterAfter = await page.textContent('.cheongsol-gallery__counter-cur');
  const abCounterAfter = await page.textContent('.aegibong-gallery__counter-cur');
  console.log('청솔 클릭 후 청솔:', csCounterAfter, '(기대: 2)');
  console.log('청솔 클릭 후 애기봉:', abCounterAfter, '(기대: 1 - 변화 없어야)');

  // 6. 애기봉 next 클릭 → 애기봉만 변경
  await page.click('.aegibong-gallery__arrow--next');
  await page.waitForTimeout(400);
  const csCounterAfter2 = await page.textContent('.cheongsol-gallery__counter-cur');
  const abCounterAfter2 = await page.textContent('.aegibong-gallery__counter-cur');
  console.log('애기봉 클릭 후 청솔:', csCounterAfter2, '(기대: 2 - 변화 없어야)');
  console.log('애기봉 클릭 후 애기봉:', abCounterAfter2, '(기대: 2)');

  // 7. 이미지 src 혼합 검사
  const csImgSrcs = await page.$$eval('.cheongsol-gallery__img', imgs => imgs.map(i => i.src));
  const abImgSrcs = await page.$$eval('.aegibong-gallery__img', imgs => imgs.map(i => i.src));
  const mixCS = csImgSrcs.some(s => s.includes('aegibong'));
  const mixAB = abImgSrcs.some(s => s.includes('cheongsol'));
  console.log('청솔 갤러리 aegibong 혼입:', mixCS, '(기대: false)');
  console.log('애기봉 갤러리 cheongsol 혼입:', mixAB, '(기대: false)');

  // 8. 가로 overflow
  const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
  const vpWidth = 1280;
  console.log('body scrollWidth:', bodyWidth, '/ viewport:', vpWidth, '/ overflow:', bodyWidth > vpWidth);

  // 9. 하단 section 정렬 (py-14)
  const bottomSection = await page.$eval('section.py-14', el => {
    const r = el.getBoundingClientRect();
    return { left: Math.round(r.left), width: Math.round(r.width) };
  });
  console.log('하단 section left:', bottomSection.left + 'px', '(기대: 0)');

  // 10. FAQ h2 정렬 확인
  const faqH2 = await page.$eval('.bg-white.border.border-gray-200 h2', el => {
    const r = el.getBoundingClientRect();
    return { left: Math.round(r.left) };
  }).catch(() => null);
  console.log('FAQ H2 left:', faqH2 ? faqH2.left + 'px' : 'not found');

  // 11. console error, 이미지 404
  console.log('console error 수:', errors.length, errors.length > 0 ? JSON.stringify(errors.slice(0,3)) : '');
  console.log('이미지 404 수:', img404.length, img404.length > 0 ? JSON.stringify(img404.slice(0,3)) : '');

  // 12. 모바일 가로 overflow
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(300);
  const mobileBodyWidth = await page.evaluate(() => document.body.scrollWidth);
  console.log('모바일 body scrollWidth:', mobileBodyWidth, '/ viewport: 390 / overflow:', mobileBodyWidth > 390);

  // 13. 썸네일 가로 스크롤 가능 여부 (overflow-x: auto)
  const csThumbsScroll = await page.$eval('.cheongsol-gallery__thumbs', el => el.scrollWidth > el.clientWidth);
  const abThumbsScroll = await page.$eval('.aegibong-gallery__thumbs', el => el.scrollWidth > el.clientWidth);
  console.log('청솔 썸네일 가로스크롤:', csThumbsScroll);
  console.log('애기봉 썸네일 가로스크롤:', abThumbsScroll);

  await browser.close();
  console.log('--- 검증 완료 ---');
})();
