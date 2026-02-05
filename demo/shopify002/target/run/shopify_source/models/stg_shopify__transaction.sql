
  
  create view "shopify"."main_stg_shopify"."stg_shopify__transaction__dbt_tmp" as (
    with base as (

    select * from "shopify"."main_stg_shopify"."stg_shopify__transaction_tmp"

),

fields as (

    select

        
    
    
    id
    
 as 
    
    id
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    refund_id
    
 as 
    
    refund_id
    
, 
    
    
    amount
    
 as 
    
    amount
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    processed_at
    
 as 
    
    processed_at
    
, 
    
    
    device_id
    
 as 
    
    device_id
    
, 
    
    
    gateway
    
 as 
    
    gateway
    
, 
    
    
    source_name
    
 as 
    
    source_name
    
, 
    
    
    message
    
 as 
    
    message
    
, 
    
    
    currency
    
 as 
    
    currency
    
, 
    
    
    location_id
    
 as 
    
    location_id
    
, 
    
    
    parent_id
    
 as 
    
    parent_id
    
, 
    
    
    payment_avs_result_code
    
 as 
    
    payment_avs_result_code
    
, 
    
    
    payment_credit_card_bin
    
 as 
    
    payment_credit_card_bin
    
, 
    
    
    payment_cvv_result_code
    
 as 
    
    payment_cvv_result_code
    
, 
    
    
    payment_credit_card_number
    
 as 
    
    payment_credit_card_number
    
, 
    
    
    payment_credit_card_company
    
 as 
    
    payment_credit_card_company
    
, 
    
    
    kind
    
 as 
    
    kind
    
, 
    
    
    receipt
    
 as 
    
    receipt
    
, 
    
    
    currency_exchange_id
    
 as 
    
    currency_exchange_id
    
, 
    
    
    currency_exchange_adjustment
    
 as 
    
    currency_exchange_adjustment
    
, 
    
    
    currency_exchange_original_amount
    
 as 
    
    currency_exchange_original_amount
    
, 
    
    
    currency_exchange_final_amount
    
 as 
    
    currency_exchange_final_amount
    
, 
    
    
    currency_exchange_currency
    
 as 
    
    currency_exchange_currency
    
, 
    
    
    error_code
    
 as 
    
    error_code
    
, 
    
    
    status
    
 as 
    
    status
    
, 
    
    
    test
    
 as 
    
    test
    
, 
    
    
    user_id
    
 as 
    
    user_id
    
, 
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    cast(null as timestamp) as 
    
    authorization_expires_at
    
 , 
    cast(null as TEXT) as authorization_code 



        


, cast('' as TEXT) as source_relation




    from base

),

final as (

    select 
        id as transaction_id,
        order_id,
        refund_id,
        amount,
        device_id,
        gateway,
        source_name,
        message,
        currency,
        location_id,
        parent_id,
        payment_avs_result_code,
        payment_credit_card_bin,
        payment_cvv_result_code,
        payment_credit_card_number,
        payment_credit_card_company,
        kind,
        receipt,
        currency_exchange_id,
        currency_exchange_adjustment,
        currency_exchange_original_amount,
        currency_exchange_final_amount,
        currency_exchange_currency,
        error_code,
        status,
        user_id,
        authorization_code,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_timestamp,
        cast(
    cast(cast(processed_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as processed_timestamp,
        cast(
    cast(cast(authorization_expires_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as authorization_expires_at,
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
