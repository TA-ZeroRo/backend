# Zero Seoul RPA 자동화 가이드

## 🎯 개요
Zero Seoul 챌린지 제출을 완전 자동화하는 RPA 스크립트입니다.

## 📋 기능
1. ✅ 자동 로그인
2. ✅ 챌린지 참여 버튼 클릭
3. ✅ 폼 작성 (제목, 이미지, 내용)
4. ✅ 자동 제출
5. ✅ 제출 확인
6. ✅ 자동 종료

## 🚀 실행 방법

### 1. 이미지 준비
대나무 숲 이미지를 다음 위치에 저장:
```
C:\Projects\TAZeroro1\test_images\bamboo_forest.jpg
```

### 2. 스크립트 실행
```powershell
python tests/manual/test_zeroseoul_final.py
```

### 3. 결과 확인
- 브라우저가 자동으로 열리고 전체 과정이 실행됩니다
- 5초 후 자동으로 종료됩니다
- 스크린샷은 `logs/screenshots/` 폴더에 저장됩니다

## 📸 스크린샷
- `01_before_challenge_click.png` - 챌린지 버튼 클릭 전
- `02_modal_opened.png` - 폼 열림
- `03_before_submit.png` - 제출 전
- `05_after_submit.png` - 제출 후
- `06_submission_list.png` - 제출 목록
- `07_found_submission.png` - 제출 항목 확인

## ⚙️ 설정 변경

### 계정 정보 변경
`test_zeroseoul_final.py` 파일의 `main()` 함수에서:
```python
credentials = {
    "username": "your_id",
    "password": "your_password"
}
```

### 제출 내용 변경
```python
submission_data = {
    "title": "제목",
    "content": "내용"
}
```

### 이미지 경로 변경
```python
image_path = r"C:\path\to\your\image.jpg"
```

## 🛠️ 트러블슈팅

### 이미지가 업로드되지 않음
- 이미지 경로가 올바른지 확인
- 이미지 파일이 실제로 존재하는지 확인
- 파일 형식이 JPG, PNG인지 확인 (최대 5MB)

### 로그인 실패
- 계정 정보가 올바른지 확인
- Zero Seoul 사이트가 정상 작동하는지 확인

### 제출 버튼을 찾을 수 없음
- 페이지가 완전히 로드될 때까지 대기 시간 증가
- `slow_mo` 값을 증가 (현재 500ms)

## 📝 참고사항
- 브라우저가 보이는 모드로 실행됩니다 (`headless=False`)
- 각 단계마다 500ms 딜레이가 있습니다 (`slow_mo=500`)
- 에러 발생 시 10초간 브라우저가 열려있습니다
- 성공 시 5초 후 자동 종료됩니다
