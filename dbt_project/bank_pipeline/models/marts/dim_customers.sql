-- dim_customers.sql
-- Mart layer: final, polished customer dimension table.
-- One row per customer, combining demographics with their aggregated transaction behavior.
-- This is a "dimension" table (dim_) in star-schema terms: it describes an entity (the customer),
-- not an event. Compare to fct_ tables, which describe events/measurements.

with customer_stats as (

    select * from {{ ref('int_customer_transaction_stats') }}

),

final as (

    select
        account_id,
        customer_age,
        customer_occupation,

        -- Simple age bucket for easier grouping in dashboards/reports
        case
            when customer_age < 25 then 'Under 25'
            when customer_age between 25 and 40 then '25-40'
            when customer_age between 41 and 60 then '41-60'
            else 'Over 60'
        end as age_group,

        total_transactions,
        total_transaction_amount,
        avg_transaction_amount,
        stddev_transaction_amount,
        most_common_channel,
        current_account_balance,
        first_transaction_date,
        most_recent_transaction_date

    from customer_stats

)

select * from final
