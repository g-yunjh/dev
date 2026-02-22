package com.example.laboratory.lab1_insert;

import com.example.laboratory.lab1_insert.entity.Payment;
import com.example.laboratory.lab1_insert.service.InsertBenchmarkService;
import net.datafaker.Faker;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;

@SpringBootTest
class Lab01InsertTest {

    @Autowired
    private InsertBenchmarkService benchmarkService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    @DisplayName("10만건 데이터 Insert 성능 실험: JPA vs JDBC")
    void runExperiment() {
        jdbcTemplate.execute("TRUNCATE TABLE payment");

        int totalCount = 100_000;
        Faker faker = new Faker();
        List<Payment> payments = createFakePayments(totalCount, faker);

        System.out.println("\n>>> 실험 1: JPA vs JDBC 성능 비교 (10만 건) <<<");
        long jdbcTime = benchmarkService.insertByJdbc(payments);
        System.out.println("[RESULT] JDBC Batch Insert: " + jdbcTime + " ms");

        jdbcTemplate.execute("TRUNCATE TABLE payment");
        long jpaTime = benchmarkService.insertByJpa(payments);
        System.out.println("[RESULT] JPA saveAll Insert: " + jpaTime + " ms");

        double speedUp = (double) jpaTime / jdbcTime;
        System.out.printf(">>> JDBC가 JPA보다 약 %.2f배 빠릅니다.%n", speedUp);
    }

    @Test
    @DisplayName("배치 사이즈별 JPA vs JDBC 성능 비교 실험")
    void batchSizeComparisonExperiment() {
        int totalCount = 100_000;
        List<Integer> batchSizes = List.of(10, 100, 500, 1000, 2000, 5000);
        Faker faker = new Faker();

        System.out.println("\n=== [LAB-01] 배치 사이즈별 성능 비교 (총 10만 건) ===");
        System.out.println("| Batch Size | JDBC (ms) | JPA (ms) | Diff (Ratio) |");
        System.out.println("|------------|-----------|----------|--------------|");

        for (int size : batchSizes) {
            List<Payment> dataForJdbc = createFakePayments(totalCount, faker);
            List<Payment> dataForJpa = createFakePayments(totalCount, faker);

            jdbcTemplate.execute("TRUNCATE TABLE payment");
            long jdbcTime = benchmarkService.insertByJdbc(dataForJdbc, size);

            jdbcTemplate.execute("TRUNCATE TABLE payment");
            long jpaTime = benchmarkService.insertByJpaManualBatch(dataForJpa, size);

            double ratio = (double) jpaTime / jdbcTime;
            System.out.printf("| %10d | %9d | %8d | %11.2fx |\n", size, jdbcTime, jpaTime, ratio);
        }
    }

    private List<Payment> createFakePayments(int count, Faker faker) {
        return IntStream.range(0, count)
                .mapToObj(i -> Payment.builder()
                        .transactionId(UUID.randomUUID().toString())
                        .merchantId(faker.number().numberBetween(1L, 1000L))
                        .amount(faker.number().randomDouble(2, 10, 5000))
                        .createdAt(LocalDateTime.now())
                        .build())
                .toList();
    }
}