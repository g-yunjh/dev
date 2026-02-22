package com.example.laboratory.lab2_search;

import com.example.laboratory.lab1_insert.entity.Payment;
import com.example.laboratory.lab1_insert.repository.PaymentRepository;
import com.example.laboratory.lab1_insert.service.InsertBenchmarkService; // 추가
import com.example.laboratory.lab2_search.service.SearchBenchmarkService;
import net.datafaker.Faker;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;

@SpringBootTest
class Lab02SearchTest {

    @Autowired private SearchBenchmarkService searchService;
    @Autowired private PaymentRepository paymentRepository;
    @Autowired private InsertBenchmarkService insertService; // 데이터 삽입용

    @BeforeEach
    void setUp() {
        if (paymentRepository.count() == 0) {
            System.out.println(">>> 데이터가 없습니다. 실험용 데이터 10만 건을 생성합니다. <<<");
            Faker faker = new Faker();
            List<Payment> dummyData = IntStream.range(0, 100_000)
                    .mapToObj(i -> Payment.builder()
                            .transactionId(UUID.randomUUID().toString())
                            .merchantId(faker.number().numberBetween(1L, 1000L))
                            .amount(faker.number().randomDouble(2, 10, 5000))
                            .createdAt(LocalDateTime.now())
                            .build())
                    .toList();
            insertService.insertByJdbc(dummyData); // 가장 빠른 JDBC로 삽입
            System.out.println(">>> 데이터 준비 완료 <<<");
        }
    }

    @Test
    @DisplayName("조회 지연 시간 비교: Full Scan vs Index vs Redis")
    void runSearchExperiment() {
        // 1. 테스트 대상 선정
        Payment target = paymentRepository.findAll().stream().findFirst()
                .orElseThrow(() -> new RuntimeException("데이터 생성 실패"));

        String txId = target.getTransactionId();
        Long mId = target.getMerchantId();

        // 2. Redis 캐싱
        searchService.cacheToRedis(txId, target.getAmount().toString());

        int iterations = 100;

        // --- Case 1: Full Scan (No Index) ---
        long startNoIndex = System.nanoTime();
        for(int i=0; i<iterations; i++) searchService.searchByNonIndexedField(mId);
        long avgNoIndex = (System.nanoTime() - startNoIndex) / iterations;

        // --- Case 2: Index Scan ---
        long startIndex = System.nanoTime();
        for(int i=0; i<iterations; i++) searchService.searchByIndexedField(txId);
        long avgIndex = (System.nanoTime() - startIndex) / iterations;

        // --- Case 3: Redis (Cache) ---
        long startRedis = System.nanoTime();
        for(int i=0; i<iterations; i++) searchService.searchByRedis(txId);
        long avgRedis = (System.nanoTime() - startRedis) / iterations;

        System.out.println("\n=== [LAB-02] 조회 평균 지연 시간 (100회 반복 측정) ===");
        System.out.printf("| Full Scan (DB)   | %12d ns |\n", avgNoIndex);
        System.out.printf("| Index Scan (DB)  | %12d ns |\n", avgIndex);
        System.out.printf("| Redis Cache      | %12d ns |\n", avgRedis);
    }
}