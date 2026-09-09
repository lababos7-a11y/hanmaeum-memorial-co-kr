/**
 * 한마음추모공원 han-maum.co.kr
 * 공통 스크립트 (메뉴 토글, TOP 버튼, 네비 활성화)
 */
(function() {
  'use strict';

  // ── 모바일 메뉴 토글 ──
  const menuBtn = document.getElementById('menuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', isOpen);
      const icon = menuBtn.querySelector('i');
      if (icon) {
        icon.className = isOpen ? 'fas fa-times text-xl' : 'fas fa-bars text-xl';
      }
    });
    // 메뉴 외부 클릭 닫기
    document.addEventListener('click', (e) => {
      if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
        const icon = menuBtn.querySelector('i');
        if (icon) icon.className = 'fas fa-bars text-xl';
      }
    });
  }

  // ── TOP 버튼 ──
  const topBtn = document.getElementById('topBtn');
  if (topBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        topBtn.classList.remove('hidden');
        topBtn.classList.add('flex');
      } else {
        topBtn.classList.add('hidden');
        topBtn.classList.remove('flex');
      }
    });
    topBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── 현재 페이지 네비 활성화 ──
  const path = location.pathname.replace(/\/+$/, '') || '/';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = (link.getAttribute('href') || '').replace(/\/+$/, '') || '/';
    if (href === '/' && path === '/') {
      link.classList.add('active');
    } else if (href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── FAQ 아코디언 ──
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const answer = btn.nextElementSibling;
      const icon = btn.querySelector('.faq-icon');
      if (!answer) return;
      const isOpen = answer.classList.toggle('faq-open');
      if (icon) icon.style.transform = isOpen ? 'rotate(180deg)' : '';
      btn.setAttribute('aria-expanded', isOpen);
    });
  });
})();
