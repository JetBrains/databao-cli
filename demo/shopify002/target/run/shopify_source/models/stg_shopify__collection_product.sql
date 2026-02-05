
  
  create view "shopify"."main_stg_shopify"."stg_shopify__collection_product__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__collection_product_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    collection_id
    
 as 
    
    collection_id
    
, 
    
    
    product_id
    
 as 
    
    product_id
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        collection_id,
        product_id,
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
