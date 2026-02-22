package com.example.laboratory.lab1_insert.service;

import com.example.laboratory.lab1_insert.entity.Payment;
import com.example.laboratory.lab1_insert.repository.PaymentJdbcRepository;
import com.example.laboratory.lab1_insert.repository.PaymentRepository;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class InsertBenchmarkService {

    private final PaymentRepository paymentRepository;
    private final PaymentJdbcRepository paymentJdbcRepository;
    private final EntityManager entityManager;

    @Transactional
    public long insertByJpa(List<Payment> payments) {
        long start = System.currentTimeMillis();
        paymentRepository.saveAll(payments);
        paymentRepository.flush();
        return System.currentTimeMillis() - start;
    }

    // JPA 수동 배치 (배치 사이즈 실험용)
    @Transactional
    public long insertByJpaManualBatch(List<Payment> payments, int batchSize) {
        long start = System.currentTimeMillis();
        for (int i = 0; i < payments.size(); i++) {
            entityManager.persist(payments.get(i));
            if (i > 0 && i % batchSize == 0) {
                entityManager.flush();
                entityManager.clear();
            }
        }
        entityManager.flush();
        entityManager.clear();
        return System.currentTimeMillis() - start;
    }

    // JDBC 배치 (기본값 1000 사용)
    @Transactional
    public long insertByJdbc(List<Payment> payments) {
        return insertByJdbc(payments, 1000);
    }

    // JDBC 배치 (배치 사이즈 지정)
    @Transactional
    public long insertByJdbc(List<Payment> payments, int batchSize) {
        long start = System.currentTimeMillis();
        paymentJdbcRepository.batchInsert(payments, batchSize);
        return System.currentTimeMillis() - start;
    }
}