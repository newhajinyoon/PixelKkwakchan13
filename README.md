# 픽셀꽉찬체13 (PixelKkwakchan13)

![License](https://img.shields.io/badge/License-OFL--1.1-blue) [![Release](https://img.shields.io/github/v/release/newhajinyoon/PixelKkwakchan13)](https://github.com/newhajinyoon/PixelKkwakchan13/releases) [![jsDelivr Hits](https://data.jsdelivr.com/v1/package/gh/newhajinyoon/PixelKkwakchan13/badge)](https://www.jsdelivr.com/package/gh/newhajinyoon/PixelKkwakchan13) [![GitHub Downloads](https://img.shields.io/github/downloads/newhajinyoon/PixelKkwakchan13/total)](https://github.com/newhajinyoon/PixelKkwakchan13/releases)
<br>
13×13 픽셀 그리드 안에 자모를 빈틈없이 꽉 채워 넣은 고정폭/반전각 픽셀 한글 폰트입니다.

<img width="1459" height="969" alt="image" src="https://github.com/user-attachments/assets/2bc7030b-820a-4377-b898-92aa23725dd4" />

## 특징

- 한 글자 `13×13px`(여백 포함 `14×14px`) 크기에 `1px` 두께로 칸을 꽉 채워 그림.
- 한글 완성형 11,172자 전체 및 첫가끝 자모 조합 지원.
- 세로쓰기(`vert`) 시 괄호/마침표(`「」`, `〈〉`, `。` 등)가 세로용 글리프로 자동 치환됨.
- 한글/전각 기호는 `13×13px` 전각, 영문/숫자/기본 기호는 `7×13px` 반각으로 맞춤.

## 지원 문자

| 범위                | 비고                                           |
| ------------------- | ---------------------------------------------- |
| 한글 완성형         | 11,172자 전체 (`U+AC00`–`U+D7A3`)         |
| 호환용 자모         | ㄱ–ㅣ 현대 자모 51자 (`U+3131`–`U+3163`) |
| 첫가끝 자모         | 초/중/종성 및 채움자 (`U+1100`–`U+11C2`)  |
| 영문/숫자/기본 기호 | 반각 `7×13px` (ASCII 전체)                  |
| 전각 영문/숫자/기호 | `13×13px` (`U+FF01`–`U+FF5E`, `￦`)  |
| 특수기호            | 화살표, 도형, 연산기호, 세로쓰기용 부호 등     |

## 크기 안내

글자 `13px`에 여백 `1px`을 더해서 기준 높이가 `14px`입니다.
`14px`, `28px`, `42px`처럼 14의 배수로 쓰면 픽셀이 뭉개지지 않고 딱 떨어집니다.

### 웹 폰트 (CDN)

#### HTML

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/newhajinyoon/PixelKkwakchan13@v1.0.0/font.css">
```

#### CSS

```css
@import url('https://cdn.jsdelivr.net/gh/newhajinyoon/PixelKkwakchan13@v1.0.0/font.css');

body {
  font-family: '픽셀꽉찬체13', monospace;
  font-size: 14px;
  -webkit-font-smoothing: none;
  font-smooth: never;
}
```

## 라이선스

SIL Open Font License 1.1 (OFL-1.1)

Copyright 2026 Hajin Yoon

- 개인적/상업적 용도 및 웹/게임/소프트웨어/영상/인쇄물 등 매체에 관계없이 무료로 자유롭게 사용할 수 있습니다.
- 폰트 수정 및 재배포가 가능하며, 재배포 시 동일한 OFL-1.1 라이선스를 유지해야 합니다.
- 폰트 파일 자체를 단독으로 유료 판매할 수 없습니다.
