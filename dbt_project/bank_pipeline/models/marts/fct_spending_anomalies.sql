-- fct_spending_anomalies.sql
-- Mart layer: flags individual transactions that are unusually large relative to
-- that specific customer's own typical spending behavior (not a fixed dollar threshold).
-- Uses each customer's average and standard deviation (from the intermediate layer)
-- to define "unusual" relative to their personal baseline.

with transactions as (

    select * from {{ ref('stg_transactions') }}

),

customer_stats as (

    select
        account_id,
        avg_transaction_amount,
        stddev_transaction_amount

    from {{ ref('int_customer_transaction_stats') }}

),

joined as (

    select
        t.transaction_id,
        t.account_id,
        t.transaction_amount,
        t.transaction_date,
        t.transaction_type,
        t.channel,
        c.avg_transaction_amount,
        c.stddev_transaction_amount,

        -- How many standard deviations above this customer's own average is this transaction?
        (t.transaction_amount - c.avg_transaction_amount) / nullif(c.stddev_transaction_amount, 0)
            as z_score

    from transactions t
    left join customer_stats c
        on t.account_id = c.account_id

),

flagged as (

    select
        *,
        case
            when z_score > 2 then true
            else false
        end as is_anomaly

    from joined

)

select * from flagged
where is_anomaly = true
order by z_score desc
