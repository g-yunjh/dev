# Spring Boot + Kotlin

> 아래 공식 문서의 가이드를 따라가며 직접 만들어본 샘플  
> [Building web applications with Spring Boot and Kotlin](https://spring.io/guides/tutorials/spring-boot-kotlin)

## 기능
- Mustache 뷰로 리스트/상세 페이지
- `/api/article`, `/api/user` REST API
- JPA(H2)로 `Article`, `User` CRUD 기본 흐름

## 스택 & 설정(최소)
- Spring Boot, Kotlin, Gradle
- deps: Web, Mustache, Data JPA, H2, DevTools
- 플러그인: `kotlin-spring`, `kotlin-jpa`
- 컴파일 옵션: `-Xjsr305=strict`
- H2 예약어 회피:  
  `hibernate.globally_quoted_identifiers=true`

## 핵심 코드 조각
- `HtmlController` → 목록/상세 렌더
- `ArticleRepository`, `UserRepository` → 쿼리 메서드
- 확장함수: `String.toSlug()`, `LocalDateTime.format()`
- 초기 데이터: `BlogConfiguration`의 `ApplicationRunner`

## 실행 & 확인
```bash
./gradlew bootRun
````

* 웹: [http://localhost:8080](http://localhost:8080)
* API: `/api/article/`, `/api/user/`

## 메모(느낀 점)

* Kotlin null-safety + 확장함수로 코드 간결
* Spring Boot와 궁합 좋음(설정·테스트 수월)
* Mockk로 WebMvcTest 구성 시 테스트 작성 편리
