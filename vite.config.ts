import { defineConfig } from 'vite'
import { resolve } from 'path'
import { copyFileSync, mkdirSync, readdirSync, statSync } from 'fs'

// 디렉토리 재귀 복사 헬퍼
function copyDirSync(src: string, dest: string) {
  mkdirSync(dest, { recursive: true })
  for (const entry of readdirSync(src)) {
    const srcPath  = `${src}/${entry}`
    const destPath = `${dest}/${entry}`
    if (statSync(srcPath).isDirectory()) {
      copyDirSync(srcPath, destPath)
    } else {
      copyFileSync(srcPath, destPath)
    }
  }
}

// static 파일 복사 플러그인
function copyStaticPlugin() {
  return {
    name: 'copy-static',
    closeBundle() {
      // robots.txt 복사
      copyFileSync('public/robots.txt', 'dist/robots.txt')
      console.log('✓ robots.txt copied')
      // sitemap.xml 복사
      copyFileSync('public/sitemap.xml', 'dist/sitemap.xml')
      console.log('✓ sitemap.xml copied')
      // _redirects 복사 (Cloudflare Pages 301 redirect 규칙)
      copyFileSync('public/_redirects', 'dist/_redirects')
      console.log('✓ _redirects copied')
      // 메인 히어로 슬라이드 이미지 복사
      copyDirSync('public/images/main', 'dist/images/main')
      console.log('✓ images/main/ copied')
      // 일산 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/ilsan', 'dist/images/natural-burial/ilsan')
      console.log('✓ images/natural-burial/ilsan/ copied')
      // 남양주 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/namyangju', 'dist/images/natural-burial/namyangju')
      console.log('✓ images/natural-burial/namyangju/ copied')
      // 곤지암 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/gonjiam', 'dist/images/natural-burial/gonjiam')
      console.log('✓ images/natural-burial/gonjiam/ copied')
      // 김포 청솔수목장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/gimpo/cheongsol', 'dist/images/natural-burial/gimpo/cheongsol')
      console.log('✓ images/natural-burial/gimpo/cheongsol/ copied')
      // 김포 애기봉자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/gimpo/aegibong', 'dist/images/natural-burial/gimpo/aegibong')
      console.log('✓ images/natural-burial/gimpo/aegibong/ copied')
      // 양주 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/yangju', 'dist/images/natural-burial/yangju')
      console.log('✓ images/natural-burial/yangju/ copied')
      // 양평 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/yangpyeong', 'dist/images/natural-burial/yangpyeong')
      console.log('✓ images/natural-burial/yangpyeong/ copied')
      // 화성 자연장 실사 이미지 복사
      copyDirSync('public/images/natural-burial/hwaseong', 'dist/images/natural-burial/hwaseong')
      console.log('✓ images/natural-burial/hwaseong/ copied')
    }
  }
}

export default defineConfig({
  root: 'public',
  publicDir: false,
  build: {
    outDir: '../dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'public/index.html'),
        compare: resolve(__dirname, 'public/compare/index.html'),
        'tree-burial': resolve(__dirname, 'public/tree-burial/index.html'),
        ossuary: resolve(__dirname, 'public/ossuary/index.html'),
        cemetery: resolve(__dirname, 'public/cemetery/index.html'),
        funeral: resolve(__dirname, 'public/funeral/index.html'),
        pricing: resolve(__dirname, 'public/pricing/index.html'),
        faq: resolve(__dirname, 'public/faq/index.html'),
        notice: resolve(__dirname, 'public/notice/index.html'),
        'tree-burial-yongin': resolve(__dirname, 'public/tree-burial/yongin/index.html'),
        'tree-burial-namyangju': resolve(__dirname, 'public/tree-burial/namyangju/index.html'),
        'ossuary-ilsan': resolve(__dirname, 'public/ossuary/ilsan/index.html'),
        'ossuary-yangju': resolve(__dirname, 'public/ossuary/yangju/index.html'),
        'cemetery-pocheon': resolve(__dirname, 'public/cemetery/pocheon/index.html'),
        // 신규 카테고리 페이지
        'natural-burial': resolve(__dirname, 'public/natural-burial/index.html'),
        'memorial-hall': resolve(__dirname, 'public/memorial-hall/index.html'),
        'memorial-park': resolve(__dirname, 'public/memorial-park/index.html'),
        // 신규 상세 페이지
        'natural-burial-yongin': resolve(__dirname, 'public/natural-burial/yongin/index.html'),
        'natural-burial-namyangju': resolve(__dirname, 'public/natural-burial/namyangju/index.html'),
        'memorial-hall-ilsan': resolve(__dirname, 'public/memorial-hall/ilsan/index.html'),
        'memorial-hall-yangju': resolve(__dirname, 'public/memorial-hall/yangju/index.html'),
        'memorial-park-pocheon': resolve(__dirname, 'public/memorial-park/pocheon/index.html'),
        // 3차 신규: 자연장 7개
        'natural-burial-anseong': resolve(__dirname, 'public/natural-burial/anseong/index.html'),
        'natural-burial-gimpo': resolve(__dirname, 'public/natural-burial/gimpo/index.html'),
        'natural-burial-gonjiam': resolve(__dirname, 'public/natural-burial/gonjiam/index.html'),
        'natural-burial-hwaseong': resolve(__dirname, 'public/natural-burial/hwaseong/index.html'),
        'natural-burial-ilsan': resolve(__dirname, 'public/natural-burial/ilsan/index.html'),
        'natural-burial-yangju': resolve(__dirname, 'public/natural-burial/yangju/index.html'),
        'natural-burial-yangpyeong': resolve(__dirname, 'public/natural-burial/yangpyeong/index.html'),
        // 3차 신규: 봉안당 12개
        'memorial-hall-anseong': resolve(__dirname, 'public/memorial-hall/anseong/index.html'),
        'memorial-hall-bundang': resolve(__dirname, 'public/memorial-hall/bundang/index.html'),
        'memorial-hall-ganghwa': resolve(__dirname, 'public/memorial-hall/ganghwa/index.html'),
        'memorial-hall-gimpo': resolve(__dirname, 'public/memorial-hall/gimpo/index.html'),
        'memorial-hall-gonjiam': resolve(__dirname, 'public/memorial-hall/gonjiam/index.html'),
        'memorial-hall-namyangju': resolve(__dirname, 'public/memorial-hall/namyangju/index.html'),
        'memorial-hall-paju': resolve(__dirname, 'public/memorial-hall/paju/index.html'),
        'memorial-hall-pocheon': resolve(__dirname, 'public/memorial-hall/pocheon/index.html'),
        'memorial-hall-pyeongtaek': resolve(__dirname, 'public/memorial-hall/pyeongtaek/index.html'),
        'memorial-hall-uiwang': resolve(__dirname, 'public/memorial-hall/uiwang/index.html'),
        'memorial-hall-yangpyeong': resolve(__dirname, 'public/memorial-hall/yangpyeong/index.html'),
        'memorial-hall-yongin': resolve(__dirname, 'public/memorial-hall/yongin/index.html'),
        // 3차 신규: 추모공원 (gapyeong·namyangju 페이지 제거로 input 삭제)
        'memorial-park-yongin': resolve(__dirname, 'public/memorial-park/yongin/index.html'),
        // 6.5차 신규: 누락 지역 5개
        'natural-burial-pyeongtaek': resolve(__dirname, 'public/natural-burial/pyeongtaek/index.html'),
        'memorial-park-yangpyeong': resolve(__dirname, 'public/memorial-park/yangpyeong/index.html'),
        'memorial-park-ilsan': resolve(__dirname, 'public/memorial-park/ilsan/index.html'),
        'memorial-park-bundang': resolve(__dirname, 'public/memorial-park/bundang/index.html'),
        'memorial-park-paldang': resolve(__dirname, 'public/memorial-park/paldang/index.html'),
      }
    }
  },
  plugins: [copyStaticPlugin()]
})
