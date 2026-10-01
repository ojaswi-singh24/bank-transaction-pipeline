-- int_customer_transaction_stats.sql
-- Intermediate layer: aggregate transaction-level data up to one row per customer (account_id).
-- This is reusable business logic that our final mart models will build on top of.

with transactions as (

    select * from main.stg_transactions

),

customer_stats as (

    select
        account_id,

        -- Volume metrics
        count(*)                              as total_transactions,
        count(distinct transaction_type)      as distinct_transaction_types,

        -- Monetary metrics
        sum(transaction_amount)               as total_transaction_amount,
        avg(transaction_amount)               as avg_transaction_amount,
        min(transaction_amount)               as min_transaction_amount,
        max(transaction_amount)               as max_transaction_amount,
        stddev(transaction_amount)            as stddev_transaction_amount,

        -- Behavioral metrics
        avg(login_attempts)                   as avg_login_attempts,
        max(login_attempts)                   as max_login_attempts,

        -- Date range
        min(transaction_date)                 as first_transaction_date,
        max(transaction_date)                 as most_recent_transaction_date,

        -- Most recent known account balance (based on latest transaction)
        max_by(account_balance, transaction_date) as current_account_balance,

        -- Most common channel used by this customer
        mode(channel)                         as most_common_channel,

        -- Demographic info (same for every row of a given customer, so max() just picks it)
        max(customer_age)                     as customer_age,
        max(customer_occupation)              as customer_occupation

    from transactions
    group by account_id

)

select * from customer_stats