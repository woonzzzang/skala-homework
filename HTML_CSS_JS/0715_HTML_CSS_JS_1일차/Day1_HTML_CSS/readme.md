# 0715 Day 1 종합실습 (HTML/CSS)

## TODO
1. Web Workflow (01_web_workflow)
2. 나의 소개 페이지 (02_my_intro_page)
3. 바로가기 (03_shortcut_links)
4. 회원가입 & 결과 페이지
5. 여행지 소개 페이지

## 학습 목표
- [ ] HTML 기본 구조 설명  
- [ ] a, img, form, input, button 사용  
- [ ] class/id 차이, margin/padding/border 구분  

### 1. Web Workflow
- 개념 : 인터넷, www, HTTP(요청 → 응답), HTML의 head(안 보임)/body(보임) 구조
- 실습 : index.html 열기 → body 문구 한 줄 수정 → 새로고침 확인

### 2. 나의 소개 페이지
- 개념 : 제목(h1~h6) 위계, 문단(p), 목록(ul/ol), 링크(a href)
- 실습 : h1 이름 변경 → 목록 항목 추가 → 링크 주소 변경

### 3. 바로가기
- 개념 : 링크 목적지(href), 새 탭 열기(target=_blank), 링크 목록 구성
- 실습 : 링크 이름, 주소 변경 → 항목 추가 → 새 탭 동작 확인 

### 4. 회원가입 & 결과 페이지
- 개념 : form, label, input type, button, label은 이름표, submit은 전송
- 실습 : type text → email 변경 → label 수정 → 체크박스 항목 추가 

- 회원가입 폼(다양한 input, 유효성 검증)을 만들고, 제출 시 입력값을 표로 보여주는 결과 페이지로 이동하는 과제 (난이도 중상)

##### 기본 학습 목표
- [ ] Form/Input 요소와 주요 속성(name, placeholder, value) 이해
- [ ] text, password, email, tel, date, radio, checkbox, select, textarea 구분 사용
- [ ] required, pattern, minlength, maxlength, min, max로 유효성 검증

##### 심화 학습 목표
- [ ] fieldset/legend로 선택 항목 그룹화
- [ ] CSS Box Model, position(fixed), z-index, 특이도, :focus/:hover 종합 적용

##### 필수 요구사항
- [ ] 필수 항목(이름, 아이디, 비밀번호, 이메일, 약관동의)에 required 적용
- [ ] 아이디는 pattern으로 영문/숫자 4~12자만 허용
- [ ] 비밀번호 minlength=8, 전화번호 010-0000-0000 패턴

##### 세부 요구사항
- [ ] 성별 radio(단일), 관심분야 checkbox(복수), 지역 select 사용
- [ ] 상단 헤더를 position:fixed + z-index로 고정
- [ ] 제출 시 result.html로 이동해 입력값을 table로 표시(복수값 포함)

##### 기본 동작 테스트
- [ ] 빈 필수값 검증 : 아무것도 입력하지 않고 제출 → 브라우저 경고가 뜨며 제출이 차단된다
- [ ] 아이디 패턴 : 아이디 2자 입력 후 제출 → 패턴 위반 경고 (4자 이상이면 통과)
- [ ] 비밀번호 길이 : 비밀번호 3자 입력 → 8자 이상 안내가 표시된다

##### 검증/결과 테스트
- [ ] 복수 선택 : 관심분야 2개 체크 → 결과에 "프론트엔드, 디자인" 함께 표시
- [ ] 정상 제출 : 필수값 정상 입력 → result.html로 이동, 값이 표로 정확히 표시
- [ ] 고정 헤더 : 결과 페이지 스크롤 → 상단 헤더가 계속 고정된다

### 5. 여행지 Hub
- 개념 : img(alt), 시맨틱 태그(header/section), section으로 내용 묶기
- 실습 : 이미지 src, alt 변경 → 섹션 제목 수정 → 섹션 추가 

- 시맨틱 구조의 여행지 소개 페이지를 만든다. 고정 내비게이션의 바로가기 (앵커), 이미지 갤러리, 영상, 팁(aside)을 배치한다. (난이도 중상)

##### 기본 학습 목표
- [ ] header, nav, main, section, article, aside, footer 시맨틱 요소의 의미와 쓰임 이해
- [ ] figure/figcaption, img(alt), video(controls, poster, source) 미디어 요소 사용
- [ ] meta(description, author)와 head 구성 이해

##### 심화 학습 목표
- [ ] 앵커(#id) 링크와 scroll-behavior로 부드러운 페이지 내 이동 구현
- [ ] position(fixed/absolute), z-index, background 겹치기, 결합자 선택자, :hover 적용 

##### 필수 요구사항
- [ ] 전체 구조를 header/nav/main/section/article/aside/footer 시맨틱 요소로 구성
- [ ] 내비게이션을 position:fixed로 고정하고 링크를 섹션 id로 연결

##### 세부 요구사항
- [ ] 명소 갤러리를 figure + figcaption 3개 이상으로 구성
- [ ] 먹거리 섹션은 본문 article + 팁 aside 2단 배치

##### 추가 요구사항
- [ ] video 요소에 controls, poster 적용
- [ ] 히어로 배경은 gradient 오버레이 + 이미지, 카드 hover 시 scale 확대 

##### 필수 확인
- [ ] 시맨틱 요소 : div와 화면상 같지만 역할을 명시 → SEO, 접근성, 가독성 향상, main은 페이지당 하나
- [ ] 미디어 요소 : figure + figcaption으로 이미지와 설명을 묶고, img의 alt, video의 controls/poster/source를 사용
- [ ] 앵커 이동 : a href=#id로 섹션 점프, html { scroll-behavior: smooth } 한 줄로 부드럽게
- [ ] CSS 핵심 : gradient + 이미지 배경 겹치기, position fixed/absolute+transform 중앙정렬, 자손 결합자, hover scale 

##### 기본 테스트
- [ ] 앵커 이동 : 내비의 '먹거리' 클릭 → 해당 섹션으로 부드럽게 스크롤
- [ ] 고정 내비 : 아래로 스크롤 → 상단 내비게이션이 계속 고정

##### 검증 테스트 
- [ ] 이미지 hover : 명소 카드에 마우스 오버 → 이미지가 살짝 확대 (zoom)
- [ ] 맨 위로 : 푸터의 '↑ 맨 위로' 클릭 → 최상단으로 이동

##### 결과 확인 테스트
- [ ] alt 확인 : 이미지 로딩 차단/개발자 도구 → 모든 img에 의미 있는 alt 존재
- [ ] 영상 재생 : 영상 섹션 재생 버튼 → controls로 재생/정지 동작 (인터넷 필요)