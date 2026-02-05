-- this model will be all NULL until you have made an order line refund in Shopify

with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_line_refund_tmp"

),

fields as (

    select
    
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    location_id
    
 as 
    
    location_id
    
, 
    
    
    order_line_id
    
 as 
    
    order_line_id
    
, 
    
    
    subtotal
    
 as 
    
    subtotal
    
, 
    
    
    subtotal_set
    
 as 
    
    subtotal_set
    
, 
    
    
    total_tax
    
 as 
    
    total_tax
    
, 
    
    
    total_tax_set
    
 as 
    
    total_tax_set
    
, 
    
    
    quantity
    
 as 
    
    quantity
    
, 
    
    
    refund_id
    
 as 
    
    refund_id
    
, 
    
    
    restock_type
    
 as 
    
    restock_type
    




        


, cast('' as TEXT) as source_relation




    from base

),

final as (

    select
        id as order_line_refund_id,
        location_id,
        order_line_id,
        subtotal,
        subtotal_set,
        total_tax,
        total_tax_set,
        quantity,
        refund_id,
        restock_type,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

        





    from fields
)

select *
from final