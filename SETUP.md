# 1회성 셋업 가이드

총 소요 시간: **약 5분.** 아래 4단계를 한 번만 수행하면 이후 매일 자동 배포됩니다.

---

## 1단계 — GitHub repo 생성 (1분)

1. https://github.com/new 접속
2. **Repository name**: `briefing-archive` (원하는 이름으로 변경 가능)
3. **Public** 선택 (GitHub Pages 무료 사용 조건)
4. **나머지는 전부 비움** — README, .gitignore, license 추가하지 말 것 (중복 방지)
5. `Create repository` 클릭

---

## 2단계 — Personal Access Token (PAT) 발급 (1분)

1. https://github.com/settings/tokens?type=beta 접속 (Fine-grained tokens)
2. `Generate new token` 클릭
3. 설정:
   - **Token name**: `briefing-archive-deploy`
   - **Expiration**: `1 year` (매년 갱신)
   - **Repository access**: `Only select repositories` → 방금 만든 `briefing-archive` 선택
   - **Repository permissions** → `Contents`: **Read and write**
4. `Generate token` → 나타난 토큰(`github_pat_...`) **복사 후 보관**
   - ⚠️ 이 페이지를 닫으면 다시 볼 수 없습니다
   - 채팅창 같은 곳에 붙여넣지 마세요

---

## 3단계 — 셋업 스크립트 실행 (30초)

Claude에게 이렇게 말하세요 (토큰은 직접 입력):

```
아래 명령으로 setup.sh 실행해줘:
bash /sessions/intelligent-gifted-turing/mnt/Scheduled/briefing-archive/scripts/setup.sh <github사용자명> briefing-archive <PAT토큰>
```

예시:
```
bash /sessions/intelligent-gifted-turing/mnt/Scheduled/briefing-archive/scripts/setup.sh hyunmyung briefing-archive ghp_xxxxxxxxxxxxxxxxxxxxxxxx
```

성공하면 `✓ Setup complete.` 메시지와 함께 repo URL이 표시됩니다.

---

## 4단계 — GitHub Pages 활성화 (1분, 마지막 수동 단계)

1. `https://github.com/<사용자명>/briefing-archive/settings/pages` 접속
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` / `(root)` → `Save`
4. 약 1분 후 `https://<사용자명>.github.io/briefing-archive/` 에서 확인 가능

---

## 이후 자동화 동작

- 매일 09:10·09:20·09:30에 기존 스케줄 태스크가 HTML 생성
- 평일 10:00에 `daily-briefing-archive-deploy` 태스크가 `deploy.sh` 호출
- 당일 생성된 HTML들을 카테고리 폴더로 복사 → 인덱스 재생성 → GitHub push
- 수 분 내 Pages URL 업데이트

## 문제 발생 시

**토큰 만료**: 2단계 반복 후 아래 실행
```bash
cd /sessions/intelligent-gifted-turing/mnt/Scheduled/briefing-archive
git remote set-url origin https://<사용자명>:<새_PAT>@github.com/<사용자명>/briefing-archive.git
```

**수동 배포 트리거**:
```bash
bash /sessions/intelligent-gifted-turing/mnt/Scheduled/briefing-archive/scripts/deploy.sh
```

**특정 날짜 재배포**:
```bash
TODAY_OVERRIDE=2026-04-20 bash .../deploy.sh
```
