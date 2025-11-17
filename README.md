# Mentoai-DE
2025 캡스톤디자인 - MentoAI (Data Engineering)

# Linkareer 공모전 크롤러

- `partial_linkareer.py` : 최신 공모전 일부 페이지만 조회
- `total_linkareer.py`   : 모집 중인 공모전 전체 페이지를 끝까지 크롤링

## 1. 환경 요구사항

- Python 3.8 이상
- 설치 패키지

  pip install requests


## 2. 파일 공통 동작 개요

- 

두 스크립트 모두 Linkareer의 GraphQL 엔드포인트를 호출해서
활동 타입이 공모전(activityTypeID = 3)이고, 모집 상태가 OPEN인 활동들만 가져온다.
	•	요청 URL: https://api.linkareer.com/graphql
	•	공통 헤더:
	•	User-Agent, Origin, Referer, Content-Type 등을 브라우저와 비슷하게 설정
	•	공통 GraphQL 쿼리:
	•	operationName: ActivityList_Activities
	•	filterBy.status: "OPEN"
	•	filterBy.activityTypeID: 3 (공모전)
	•	activityOrder.field: "CREATED_AT"
	•	activityOrder.direction: "DESC" (최신순 정렬)

응답에서 다음 필드를 사용해 출력한다.
	•	title               : 공모전 제목
	•	id                  : 상세 페이지 URL 생성에 사용
	•	recruitCloseAt      : 마감 시각 (밀리초 단위 타임스탬프 → YYYY-MM-DD 포맷으로 변환)
	•	organizationName    : 주최/주관
	•	그 외 필드는 추후 확장용


## 3. 파일 동작 방식

### 3-1. partial_linkareer.py

1 목적

	•	한 페이지만 조회해서, 현재 모집 중인 최신 공모전 대략 몇 개가 있는지 빠르게 확인할 때 사용한다.
	•	페이지 크기는 30개로 고정되어 있으며, 페이징 반복은 하지 않는다.

2 실행 명령어

- python partial_linkareer.py

3 출력 예시

	•	제목
	•	링크(https://linkareer.com/activity/{id})
	•	분야
	•	주최/주관
	•	접수 마감일

### 3-2 total_linkareer.py

1 목적
	•	모집 중인 공모전 전체를 끝까지 크롤링해서 페이지네이션 후 모으는 스크립트
	•	추후 S3 저장, DB 적재, 임베딩 파이프라인 입력으로 사용하기 위한 형태

2 동작 방식
	1.	page = 1부터 시작
	2.	GraphQL API에 요청을 보내서 page_size 만큼 데이터를 가져온다.
	3.	응답의 nodes 리스트를 all_activities에 계속 누적한다.
	4.	가져온 개수가 page_size보다 작아지는 순간 마지막 페이지로 간주하고 종료한다.
	5.	중간에 네트워크 오류나 GraphQL 에러가 발생하면 메시지를 출력하고 종료한다.

3 실행 명령어

- python total_linkareer.py

4 출력 내용
	•	최종적으로 수집한 전체 공모전 개수
	•	제목
	•	링크(https://linkareer.com/activity/{id})
	•	분야
	•	주최/주관
	•	접수 마감일
