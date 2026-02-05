
  
  create view "shopify"."main_stg_shopify"."stg_shopify__tender_transaction__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__tender_transaction_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    amount
    
 as 
    
    amount
    
, 
    
    
    currency
    
 as 
    
    currency
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    payment_method
    
 as 
    
    payment_method
    
, 
    
    
    processed_at
    
 as 
    
    processed_at
    
, 
    
    
    remote_reference
    
 as 
    
    remote_reference
    
, 
    
    
    test
    
 as 
    
    test
    
, 
    
    
    user_id
    
 as 
    
    user_id
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as transaction_id,
        order_id,
        amount,
        currency,
        payment_method,
        remote_reference,
        user_id,
        cast(
    cast(cast(processed_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as processed_at,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

    from fields
    where not coalesce(test, false)
)

select *
from final
  );
