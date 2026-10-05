-- fct_monthly_trends.sql
-- Mart layer: transaction volume and spending aggregated by month, with month-over-month % change.
-- Demonstrates window functions with ordering (lag()) to compare each row to the previous one.

with transactions as (

    select * from {{ ref('stg_transactions') }}

),

monthly_summary as (

    select
        date_trunc('month', transaction_date)  as transaction_month,
        count(*)                               as total_transactions,
        sum(transaction_amount)                as total_amount,
        avg(transaction_amount)                as avg_amount

    from transactions
    group by date_trunc('month', transaction_date)

),

with_prior_month as (

    select
        transaction_month,
        total_transactions,
        total_amount,
        avg_amount,
        lag(total_amount) over (order by transaction_month) as prior_month_amount

    from monthly_summary

),

with_pct_change as (

    select
        *,
        (total_amount - prior_month_amount) * 100.0 / prior_month_amount as pct_change_from_prior_month

    from with_prior_month

)

select * from with_pct_change
order by transaction_month