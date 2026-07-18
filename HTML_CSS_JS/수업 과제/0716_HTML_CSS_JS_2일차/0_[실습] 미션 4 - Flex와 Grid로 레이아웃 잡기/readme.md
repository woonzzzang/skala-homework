# [실습] 미션 4 - Flex와 Grid로 레이아웃 잡기

🗓️ 수행 날짜 : 2026-07-16    
👤 작성자 : 4기 광주 3반 정다운    
📚 수행 내용  
- 개념 : 제목(h1~h6) 위계, 문단(p), 목록(ul/ol), 링크(a href)
- 실습 : h1 이름 변경 → 목록 항목 추가 → 링크 주소 변경

1. h1 이름 변경
   - `<h1>정다운의 유니버스 🚀</h1>` 를 `<h1>정다운의 우주 👽</h1>` 로 변경
2. 목록 항목 추가
   - `<li><a href="resume.html">이력 사항 (resume)</a></li>` 를 추가
3. 링크 주소 변경
   - 기존 경로를 현재 index.html의 위치에 맞춰서 경로 수정
    ```html
    <li><a href="myProfile.html">소개 (Profile)</a></li>
    <li><a href="myClass.html">수업 시간표 (Class)</a></li>
    <li><a href="myHoliday.html">휴일 계획 (Holiday)</a></li>
    <li><a href="myTrip.html">여행 앨범 (Album)</a></li>
    <li><a href="signUp.html">👤 회원가입 (Sign Up)</a></li>
    ```
    ⬇️  

    ```html
    <li><a href="../../수업 과제/html/myProfile.html">소개 (Profile)</a></li>
    <li><a href="../../수업 과제/html/myClass.html">수업 시간표 (Class)</a></li>
    <li><a href="../../수업 과제/html/myHoliday.html">휴일 계획 (Holiday)</a></li>
    <li><a href="../../수업 과제/html/myTrip.html">여행 앨범 (Album)</a></li>
    <li><a href="../../수업 과제/html/signUp.html">👤 회원가입 (Sign Up)</a></li>
    ```
