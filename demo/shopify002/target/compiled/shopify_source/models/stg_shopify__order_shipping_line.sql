with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_shipping_line_tmp"
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
    
    
    code
    
 as 
    
    code
    
, 
    
    
    delivery_category
    
 as 
    
    delivery_category
    
, 
    
    
    discounted_price
    
 as 
    
    discounted_price
    
, 
    
    
    discounted_price_set
    
 as 
    
    discounted_price_set
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    price
    
 as 
    
    price
    
, 
    
    
    price_set
    
 as 
    
    price_set
    
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
        id as order_shipping_line_id,
        order_id,
        carrier_identifier,
        code,
        delivery_category,
        discounted_price,
        discounted_price_set,
        phone,
        price,
        price_set,
        requested_fulfillment_service_id is not null as is_third_party_required,
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