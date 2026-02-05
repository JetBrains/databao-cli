with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_discount_code_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    amount
    
 as 
    
    amount
    
, 
    
    
    code
    
 as 
    
    code
    
, 
    
    
    index
    
 as 
    
    index
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    type
    
 as 
    
    type
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        order_id,
        index,
        upper(code) as code,
        type,
        amount,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

    from fields
)

select *
from final