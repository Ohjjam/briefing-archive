# Briefing Archive

매일 자동 생성되는 브리핑 아카이브입니다.

- **AI** — GPT / Gemini / Claude / Meta / xAI / Mistral 업데이트 (매일 09:20)
- **Energy·Chem** — 에너지·화학공학 논문·정책·산업 (평일 09:30)
- **World** — 전세계 시사·정치·경제·문화 (매일 09:10)

배포는 평일 10:00에 자동으로 수행되어 GitHub Pages에 공개됩니다.

## 구조

```
.
├── ai/             YYYY-MM-DD.html — AI 브리핑
├── energy-chem/    YYYY-MM-DD.html — 에너지·화학 브리핑
├── world/          YYYY-MM-DD.html — 세계 브리핑
├── index.html      자동 생성 카드형 인덱스
└── scripts/
    ├── setup.sh          1회성 원격 연결 셋업
    ├── deploy.sh         일일 배포 (스케줄 태스크가 호출)
    └── generate_index.py 인덱스 HTML 생성기
```

## 처음 사용하시나요?

`SETUP.md` 참고.
