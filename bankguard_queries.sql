-- BankGuard: SQLite schema and analytical queries
-- Dataset is synthetic and intended for academic demonstration.

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    transaction_datetime TEXT,
    customer_id TEXT,
    transaction_type TEXT,
    amount_inr REAL,
    location TEXT,
    channel TEXT,
    device_status TEXT,
    is_fraud INTEGER,
    transaction_date TEXT,
    hour INTEGER,
    high_value_flag INTEGER,
    new_device_flag INTEGER,
    night_transaction_flag INTEGER,
    risk_score INTEGER,
    risk_category TEXT
);

-- Import bank_transactions_synthetic.csv into this table using DB Browser for SQLite
-- or Python's pandas.to_sql().

-- 1. Transaction volume and value by type
SELECT transaction_type, COUNT(*) AS txn_count,
       ROUND(SUM(amount_inr),2) AS total_value_inr,
       ROUND(AVG(amount_inr),2) AS average_amount
FROM transactions
GROUP BY transaction_type
ORDER BY txn_count DESC;

-- 2. Fraud cases and rate by transaction type
SELECT transaction_type, COUNT(*) AS total_txns,
       SUM(is_fraud) AS fraud_cases,
       ROUND(100.0*SUM(is_fraud)/COUNT(*),2) AS fraud_rate_pct
FROM transactions
GROUP BY transaction_type
ORDER BY fraud_rate_pct DESC;

-- 3. High-value transactions
SELECT transaction_id, customer_id, amount_inr, transaction_datetime, location
FROM transactions
WHERE high_value_flag = 1
ORDER BY amount_inr DESC
LIMIT 100;

-- 4. Risk category distribution
SELECT risk_category, COUNT(*) AS txn_count
FROM transactions
GROUP BY risk_category
ORDER BY txn_count DESC;

-- 5. Customers with most flagged transactions
SELECT customer_id, COUNT(*) AS total_txns,
       SUM(is_fraud) AS labelled_fraud_cases,
       ROUND(SUM(amount_inr),2) AS total_amount_inr
FROM transactions
GROUP BY customer_id
HAVING SUM(is_fraud) > 0
ORDER BY labelled_fraud_cases DESC
LIMIT 20;

-- 6. Night-time transaction analysis
SELECT night_transaction_flag, COUNT(*) AS txn_count,
       SUM(is_fraud) AS fraud_cases,
       ROUND(100.0*SUM(is_fraud)/COUNT(*),2) AS fraud_rate_pct
FROM transactions
GROUP BY night_transaction_flag;

-- 7. Device status analysis
SELECT device_status, COUNT(*) AS txn_count,
       SUM(is_fraud) AS fraud_cases,
       ROUND(100.0*SUM(is_fraud)/COUNT(*),2) AS fraud_rate_pct
FROM transactions
GROUP BY device_status;

-- 8. Monthly transaction trend
SELECT substr(transaction_datetime,1,7) AS month,
       COUNT(*) AS txn_count,
       ROUND(SUM(amount_inr),2) AS total_value_inr
FROM transactions
GROUP BY month
ORDER BY month;

-- 9. Location-wise risk
SELECT location, COUNT(*) AS txn_count,
       SUM(is_fraud) AS fraud_cases,
       ROUND(AVG(risk_score),2) AS avg_risk_score
FROM transactions
GROUP BY location
ORDER BY avg_risk_score DESC;

-- 10. Potential alert queue (rule-based, not a fraud verdict)
SELECT transaction_id, customer_id, amount_inr, risk_score, risk_category,
       high_value_flag, new_device_flag, night_transaction_flag
FROM transactions
WHERE risk_category = 'High'
ORDER BY risk_score DESC, amount_inr DESC;