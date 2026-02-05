with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__product_tmp"

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
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    handle
    
 as 
    
    handle
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    product_type
    
 as 
    
    product_type
    
, 
    
    
    published_at
    
 as 
    
    published_at
    
, 
    
    
    published_scope
    
 as 
    
    published_scope
    
, 
    
    
    title
    
 as 
    
    title
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    vendor
    
 as 
    
    vendor
    
, 
    cast(null as TEXT) as 
    
    status
    
 



        


, cast('' as TEXT) as source_relation




    from base

),

final as (
    
    select
        id as product_id,
        handle,
        product_type,
        published_scope,
        title,
        vendor,
        status,
        _fivetran_deleted as is_deleted,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_timestamp,
        cast(
    cast(cast(updated_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as updated_timestamp,
        cast(
    cast(cast(published_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as published_timestamp,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

        





from fields

)

select * 
from final