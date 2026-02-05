
  
  create view "shopify"."main_stg_shopify"."stg_shopify__product_image__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__product_image_tmp"
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
    
    
    height
    
 as 
    
    height
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    position
    
 as 
    
    position
    
, 
    
    
    product_id
    
 as 
    
    product_id
    
, 
    
    
    src
    
 as 
    
    src
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    variant_ids
    
 as 
    
    variant_ids
    
, 
    
    
    width
    
 as 
    
    width
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as product_image_id,
        product_id,
        height,
        position,
        src,
        variant_ids,
        width,
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
