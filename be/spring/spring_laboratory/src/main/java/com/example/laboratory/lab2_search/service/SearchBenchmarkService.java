package com.example.laboratory.lab2_search.service;

import com.example.laboratory.lab1_insert.entity.Payment;
import com.example.laboratory.lab1_insert.repository.PaymentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class SearchBenchmarkService {

    private final PaymentRepository paymentRepository;
    private final StringRedisTemplate redisTemplate;

    @Transactional(readOnly = true)
    public List<Payment> searchByNonIndexedField(Long merchantId) {
        return paymentRepository.findByMerchantId(merchantId);
    }

    @Transactional(readOnly = true)
    public Optional<Payment> searchByIndexedField(String transactionId) {
        return paymentRepository.findByTransactionId(transactionId);
    }

    public String searchByRedis(String transactionId) {
        return redisTemplate.opsForValue().get("payment:" + transactionId);
    }

    public void cacheToRedis(String transactionId, String amount) {
        redisTemplate.opsForValue().set("payment:" + transactionId, amount, Duration.ofMinutes(10));
    }
}