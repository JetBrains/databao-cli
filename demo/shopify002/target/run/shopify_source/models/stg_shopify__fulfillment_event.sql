
  
  create view "shopify"."main_stg_shopify"."stg_shopify__fulfillment_event__dbt_tmp" as (
    

with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment_event_tmp"
),

fields as (

    select
        
    
    
    _fivetran_deleted
    
 as 
    
    _fivetran_deleted
    
, 
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    address_1
    
 as 
    
    address_1
    
, 
    
    
    city
    
 as 
    
    city
    
, 
    
    
    country
    
 as 
    
    country
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    estimated_delivery_at
    
 as 
    
    estimated_delivery_at
    
, 
    
    
    fulfillment_id
    
 as 
    
    fulfillment_id
    
, 
    
    
    happened_at
    
 as 
    
    happened_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    latitude
    
 as 
    
    latitude
    
, 
    
    
    longitude
    
 as 
    
    longitude
    
, 
    
    
    message
    
 as 
    
    message
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    province
    
 as 
    
    province
    
, 
    
    
    shop_id
    
 as 
    
    shop_id
    
, 
    
    
    status
    
 as 
    
    status
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    zip
    
 as 
    
    zip
    



        
        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as fulfillment_event_id,
        fulfillment_id,
        shop_id,
        order_id,
        status,
        message,
        cast(
    cast(cast(estimated_delivery_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as estimated_delivery_at,
        cast(
    cast(cast(happened_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as happened_at,
        address_1,
        city,
        province,
        country,
        zip,
        latitude,
        longitude,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_at,
        cast(
    cast(cast(updated_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as updated_at,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

    from fields

    where not coalesce(_fivetran_deleted, false)
)

select *
from final
  );
