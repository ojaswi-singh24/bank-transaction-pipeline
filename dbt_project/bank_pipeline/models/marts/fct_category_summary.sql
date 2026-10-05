-- fct_category_summary.sql
-- Mart layer: transaction volume and spending broken down by category (transaction_type x channel).
-- This is a "fact" table (fct_) in star-schema terms: it describes measurable events,
-- aggregated along dimensions, rather than describing a single entity like dim_customers does.

with transactions as (

    select * from {{ ref('stg_transactions') }}

),

category_summary as (

    select
        transaction_type,
        channel,

        count(*)                   as total_transactions,
        sum(transaction_amount)    as total_amount,
        avg(transaction_amount)    as avg_amount,
        min(transaction_amount)    as min_amount,
        max(transaction_amount)    as max_amount,

        -- What share of ALL transactions (across every category) does this one category represent?
        count(*) * 100.0 / sum(count(*)) over ()  as pct_of_total_transactions,

        -- What share of ALL spending does this one category represent?
        sum(transaction_amount) * 100.0 / sum(sum(transaction_amount)) over ()  as pct_of_total_amount

    from transactions
    group by transaction_type, channel

)

select * from category_summary
order by total_amount desc