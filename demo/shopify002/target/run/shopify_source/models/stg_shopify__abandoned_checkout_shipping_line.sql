
  
  create view "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_shipping_line__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_shipping_line_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    carrier_identifier
    
 as 
    
    carrier_identifier
    
, 
    
    
    checkout_id
    
 as 
    
    checkout_id
    
, 
    
    
    code
    
 as 
    
    code
    
, 
    
    
    delivery_category
    
 as 
    
    delivery_category
    
, 
    
    
    delivery_expectation_range
    
 as 
    
    delivery_expectation_range
    
, 
    
    
    delivery_expectation_range_max
    
 as 
    
    delivery_expectation_range_max
    
, 
    
    
    delivery_expectation_range_min
    
 as 
    
    delivery_expectation_range_min
    
, 
    
    
    delivery_expectation_type
    
 as 
    
    delivery_expectation_type
    
, 
    
    
    discounted_price
    
 as 
    
    discounted_price
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    index
    
 as 
    
    index
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    price
    
 as 
    
    price
    
, 
    
    
    requested_fulfillment_service_id
    
 as 
    
    requested_fulfillment_service_id
    
, 
    
    
    source
    
 as 
    
    source
    
, 
    
    
    title
    
 as 
    
    title
    




        


, cast('' as TEXT) as source_relation



        
    from base
),

final as (
    
    select 
        id as abandoned_checkout_shipping_line_id,
        checkout_id,
        index,
        carrier_identifier,
        code as shipping_code,
        delivery_category,
        delivery_expectation_range,
        delivery_expectation_range_max,
        delivery_expectation_range_min,
        delivery_expectation_type,
        discounted_price,
        phone,
        price,
        requested_fulfillment_service_id,
        source,
        title,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

    from fields
)

select *
from final
  );
