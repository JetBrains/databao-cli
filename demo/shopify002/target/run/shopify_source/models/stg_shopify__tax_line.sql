
  
  create view "shopify"."main_stg_shopify"."stg_shopify__tax_line__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__tax_line_tmp"
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
    
    
    order_line_id
    
 as 
    
    order_line_id
    
, 
    
    
    price
    
 as 
    
    price
    
, 
    
    
    price_set
    
 as 
    
    price_set
    
, 
    
    
    rate
    
 as 
    
    rate
    
, 
    
    
    title
    
 as 
    
    title
    



    
        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        index,
        order_line_id,
        price,
        price_set,
        rate,
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
