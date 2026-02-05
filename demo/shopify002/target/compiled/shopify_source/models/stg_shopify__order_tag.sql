with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_tag_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    index
    
 as 
    
    index
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    value
    
 as 
    
    value
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        order_id,
        index,
        value,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

    from fields
)

select *
from final