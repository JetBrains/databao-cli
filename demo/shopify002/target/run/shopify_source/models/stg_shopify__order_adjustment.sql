
  
  create view "shopify"."main_stg_shopify"."stg_shopify__order_adjustment__dbt_tmp" as (
    -- this model will be all NULL until you have made an order adjustment in Shopify

with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_adjustment_tmp"

),

fields as (

    select
        
    
    
    id
    
 as 
    
    id
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    refund_id
    
 as 
    
    refund_id
    
, 
    
    
    amount
    
 as 
    
    amount
    
, 
    
    
    amount_set
    
 as 
    
    amount_set
    
, 
    
    
    tax_amount
    
 as 
    
    tax_amount
    
, 
    
    
    tax_amount_set
    
 as 
    
    tax_amount_set
    
, 
    
    
    kind
    
 as 
    
    kind
    
, 
    
    
    reason
    
 as 
    
    reason
    
, 
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    




        


, cast('' as TEXT) as source_relation



        
    from base
),

final as (

    select
        id as order_adjustment_id,
        order_id,
        refund_id,
        amount,
        amount_set,
        tax_amount,
        tax_amount_set,
        kind,
        reason,
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
