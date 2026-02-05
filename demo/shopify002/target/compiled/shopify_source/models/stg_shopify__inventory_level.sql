with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__inventory_level_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    available
    
 as 
    
    available
    
, 
    
    
    inventory_item_id
    
 as 
    
    inventory_item_id
    
, 
    
    
    location_id
    
 as 
    
    location_id
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        inventory_item_id,
        location_id,
        available as available_quantity,
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