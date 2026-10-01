-- stg_transactions.sql
-- Staging layer: clean, rename, and type-cast the raw transactions table.
-- No business logic here yet -- just making the raw data trustworthy and consistent.

with source as (

    select * from raw.transactions

),

renamed as (

    select
        -- Identifiers
        trim(TransactionID)          as transaction_id,
        trim(AccountID)               as account_id,
        trim(DeviceID)                 as device_id,
        trim(MerchantID)               as merchant_id,
        trim("IP Address")             as ip_address,

        -- Transaction details
        cast(TransactionAmount as decimal(12, 2))  as transaction_amount,
        cast(TransactionDate as timestamp)          as transaction_date,
        cast(PreviousTransactionDate as timestamp)  as previous_transaction_date,
        lower(trim(TransactionType))                as transaction_type,
        lower(trim(Channel))                        as channel,
        trim(Location)                               as location,

        -- Customer details
        cast(CustomerAge as integer)       as customer_age,
        lower(trim(CustomerOccupation))    as customer_occupation,

        -- Numeric / behavioral fields
        cast(TransactionDuration as integer)  as transaction_duration_seconds,
        cast(LoginAttempts as integer)        as login_attempts,
        cast(AccountBalance as decimal(12, 2)) as account_balance

    from source

)

select * from renamed