with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_line_tmp"

),

fields as (

    select
    
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    fulfillable_quantity
    
 as 
    
    fulfillable_quantity
    
, 
    
    
    fulfillment_status
    
 as 
    
    fulfillment_status
    
, 
    
    
    gift_card
    
 as 
    
    gift_card
    
, 
    
    
    grams
    
 as 
    
    grams
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    index
    
 as 
    
    index
    
, 
    
    
    name
    
 as 
    
    name
    
, 
    
    
    order_id
    
 as 
    
    order_id
    
, 
    
    
    pre_tax_price
    
 as 
    
    pre_tax_price
    
, 
    cast(null as TEXT) as 
    
    pre_tax_price_set
    
 , 
    
    
    price
    
 as 
    
    price
    
, 
    cast(null as TEXT) as 
    
    price_set
    
 , 
    
    
    product_id
    
 as 
    
    product_id
    
, 
    
    
    quantity
    
 as 
    
    quantity
    
, 
    
    
    requires_shipping
    
 as 
    
    requires_shipping
    
, 
    
    
    sku
    
 as 
    
    sku
    
, 
    
    
    taxable
    
 as 
    
    taxable
    
, 
    cast(null as TEXT) as 
    
    tax_code
    
 , 
    
    
    title
    
 as 
    
    title
    
, 
    
    
    total_discount
    
 as 
    
    total_discount
    
, 
    cast(null as TEXT) as 
    
    total_discount_set
    
 , 
    
    
    variant_id
    
 as 
    
    variant_id
    
, 
    cast(null as TEXT) as 
    
    variant_title
    
 , 
    cast(null as TEXT) as 
    
    variant_inventory_management
    
 , 
    
    
    vendor
    
 as 
    
    vendor
    
, 
    cast(null as TEXT) as 
    
    properties
    
 



        


, cast('' as TEXT) as source_relation




    from base

),

final as (
    
    select 
        id as order_line_id,
        index,
        name,
        order_id,
        fulfillable_quantity,
        fulfillment_status,
        gift_card as is_gift_card,
        grams,
        pre_tax_price,
        pre_tax_price_set,
        price,
        price_set,
        product_id,
        quantity,
        requires_shipping as is_shipping_required,
        sku,
        taxable as is_taxable,
        tax_code,
        title,
        total_discount,
        total_discount_set,
        variant_id,
        variant_title,
        variant_inventory_management,
        vendor,
        properties,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

        





    from fields

)

select * 
from final