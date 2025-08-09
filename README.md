# InfoBridge Django Server

Django REST API 서버 for InfoBridge 프로젝트

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/infinithon-2025/django-starter.git
cd django-starter
```

### 2. Python 환경 설정
```bash
# Python 3.12.5 설치 (pyenv 사용)
pyenv install 3.12.5
pyenv local 3.12.5

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements-dev.txt
```

### 4. 환경 변수 설정
```bash
# .env 파일 생성 (필요시)
cp .env.example .env
# 또는 직접 생성
echo "DJANGO_SECRET_KEY=your-secret-key-here" > .env
echo "DJANGO_DEBUG=True" >> .env
echo "DJANGO_ALLOWED_HOSTS=*" >> .env
```

### 5. 데이터베이스 설정
```bash
# 마이그레이션 실행
python manage.py migrate

# 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser
```

### 6. 개발 서버 실행
```bash
python manage.py runserver
# 또는
make dev
```

## 📋 프로젝트 구조

```
django-starter/
├── config/                 # Django 프로젝트 설정
│   ├── settings.py        # 메인 설정 파일
│   ├── urls.py           # URL 라우팅
│   └── ...
├── core/                  # 메인 앱
│   ├── models.py         # 데이터베이스 모델
│   ├── api_views.py      # REST API 뷰
│   ├── serializers.py    # API 직렬화
│   ├── admin.py          # Django Admin 설정
│   └── ...
├── requirements.txt       # 프로덕션 의존성
├── requirements-dev.txt   # 개발 의존성
├── Makefile              # 개발 명령어
└── dummy_data.json       # 테스트 데이터
```

## 🔧 주요 기능

### API 엔드포인트
- **프로젝트 관리**: `/api/projects/`
- **자료 관리**: `/api/project-materials/`
- **콘텐츠 관리**: `/api/items/`, `/api/summaries/`
- **추천 관리**: `/api/recommendations/`
- **AI 관리**: `/api/ai-requests/`
- **외부 데이터 매칭**: `/api/projects/{id}/external_matches_by_keyword/`

### API 문서
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **하이라이트된 API**: http://localhost:8000/api/docs/highlighted/

### Django Admin
- **관리자 페이지**: http://localhost:8000/admin/
- **슈퍼유저 생성**: `python manage.py createsuperuser`

## 🛠️ 개발 도구

### Makefile 명령어
```bash
make dev          # 개발 서버 실행
make migrate      # 데이터베이스 마이그레이션
make superuser    # 슈퍼유저 생성
make api-test     # API 테스트 명령어 출력
make docs         # API 문서 URL 출력
make freeze       # 의존성 업데이트
```

### API 테스트
```bash
# 프로젝트 목록
curl http://localhost:8000/api/projects/

# 아이템 목록
curl http://localhost:8000/api/items/

# 추천 목록
curl http://localhost:8000/api/recommendations/
```

## 📊 데이터베이스 모델

### 주요 모델
- **Project**: 프로젝트 정보
- **ProjectMaterial**: 프로젝트 자료 (GitHub, Slack, Jira, Gmail)
- **Item**: 콘텐츠 아이템
- **Summary**: 요약 정보
- **Recommendation**: 추천 정보
- **AIRequest**: AI 요청 기록

## 🔍 환경 변수

### 필수 환경 변수
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
```

### 선택적 환경 변수
```bash
DATABASE_URL=sqlite:///db.sqlite3  # 기본값
```

## 🐛 문제 해결

### 일반적인 문제들

1. **포트 충돌**
   ```bash
   # 다른 포트 사용
   python manage.py runserver 8001
   ```

2. **의존성 문제**
   ```bash
   # 가상환경 재생성
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **마이그레이션 문제**
   ```bash
   # 마이그레이션 초기화
   python manage.py migrate --fake-initial
   ```

4. **정적 파일 문제**
   ```bash
   python manage.py collectstatic
   ```

## 📝 개발 가이드

### 새로운 API 추가
1. `core/models.py`에 모델 추가
2. `core/serializers.py`에 시리얼라이저 추가
3. `core/api_views.py`에 뷰셋 추가
4. `core/urls.py`에 URL 등록
5. 마이그레이션 생성 및 적용

### 코드 스타일
- Python: PEP 8 준수
- Django: Django 코딩 스타일 가이드 준수
- API: RESTful 설계 원칙 준수

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.
