
  
  create view "shopify"."main_stg_shopify"."stg_shopify__fulfillment__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    location_id
    
 as 
    
    location_id
    
, 
    
    
    name
    
 as 
    
    name
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    service
    
 as 
    
    service
    
, 
    
    
    shipment_status
    
 as 
    
    shipment_status
    
, 
    
    
    status
    
 as 
    
    status
    
, 
    
    
    tracking_company
    
 as 
    
    tracking_company
    
, 
    
    
    tracking_number
    
 as 
    
    tracking_number
    
, 
    
    
    tracking_numbers
    
 as 
    
    tracking_numbers
    
, 
    
    
    tracking_urls
    
 as 
    
    tracking_urls
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as fulfillment_id,
        location_id,
        order_id,
        name,
        service,
        shipment_status,
        lower(status) as status,
        tracking_company,
        tracking_number,
        tracking_numbers,
        tracking_urls,
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
)

select *
from final
  );
