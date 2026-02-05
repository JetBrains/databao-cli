
  
  create view "shopify"."main_stg_shopify"."stg_shopify__refund__dbt_tmp" as (
    -- this model will be all NULL until you have made a refund in Shopify

with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__refund_tmp"

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
    
    
    note
    
 as 
    
    note
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    processed_at
    
 as 
    
    processed_at
    
, 
    
    
    restock
    
 as 
    
    restock
    
, 
    
    
    total_duties_set
    
 as 
    
    total_duties_set
    
, 
    
    
    user_id
    
 as 
    
    user_id
    




        


, cast('' as TEXT) as source_relation



        
    from base
),

final as (

    select
        id as refund_id,
        note,
        order_id,
        restock,
        total_duties_set,
        user_id,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_at,
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
)

select * 
from final
  );
