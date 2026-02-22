package com.example.laboratory.lab1_insert.repository;

import com.example.laboratory.lab1_insert.entity.Payment;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface PaymentRepository extends JpaRepository<Payment, Long> {

    List<Payment> findByMerchantId(Long merchantId);

    Optional<Payment> findByTransactionId(String transactionId);
}