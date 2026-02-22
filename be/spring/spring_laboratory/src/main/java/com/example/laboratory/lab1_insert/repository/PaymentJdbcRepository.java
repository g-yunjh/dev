package com.example.laboratory.lab1_insert.repository;

import com.example.laboratory.lab1_insert.entity.Payment;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.util.List;

@Repository
@RequiredArgsConstructor
public class PaymentJdbcRepository {
    private final JdbcTemplate jdbcTemplate;

    public void batchInsert(List<Payment> payments, int batchSize) {
        String sql = "INSERT INTO payment (transaction_id, merchant_id, amount, created_at, id) " +
                "VALUES (?, ?, ?, ?, nextval('payment_seq'))";

        jdbcTemplate.batchUpdate(sql, payments, batchSize, (PreparedStatement ps, Payment p) -> {
            ps.setString(1, p.getTransactionId());
            ps.setLong(2, p.getMerchantId());
            ps.setDouble(3, p.getAmount());
            ps.setObject(4, p.getCreatedAt());
        });
    }
}