

with transactions as (
    select 
        *,
        md5(cast(coalesce(cast(source_relation as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(transaction_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as transactions_unique_id
    from "shopify"."main_stg_shopify"."stg_shopify__transaction"

    

), tender_transactions as (

    select *
    from "shopify"."main_stg_shopify"."stg_shopify__tender_transaction"

), joined as (
    select 
        transactions.*,
        tender_transactions.payment_method,
        parent_transactions.created_timestamp as parent_created_timestamp,
        parent_transactions.kind as parent_kind,
        parent_transactions.amount as parent_amount,
        parent_transactions.status as parent_status
    from transactions
    left join tender_transactions
        on transactions.transaction_id = tender_transactions.transaction_id
        and transactions.source_relation = tender_transactions.source_relation
    left join transactions as parent_transactions
        on transactions.parent_id = parent_transactions.transaction_id
        and transactions.source_relation = parent_transactions.source_relation

), exchange_rate as (

    select
        *
    from joined

)

select *
from exchange_rate