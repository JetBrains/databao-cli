with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__product_variant_tmp"

),

fields as (

    select
    
        
    
    
    id
    
 as 
    
    id
    
, 
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    product_id
    
 as 
    
    product_id
    
, 
    
    
    inventory_item_id
    
 as 
    
    inventory_item_id
    
, 
    
    
    image_id
    
 as 
    
    image_id
    
, 
    
    
    title
    
 as 
    
    title
    
, 
    
    
    price
    
 as 
    
    price
    
, 
    
    
    sku
    
 as 
    
    sku
    
, 
    
    
    position
    
 as 
    
    position
    
, 
    
    
    inventory_policy
    
 as 
    
    inventory_policy
    
, 
    
    
    compare_at_price
    
 as 
    
    compare_at_price
    
, 
    
    
    fulfillment_service
    
 as 
    
    fulfillment_service
    
, 
    
    
    inventory_management
    
 as 
    
    inventory_management
    
, 
    
    
    taxable
    
 as 
    
    taxable
    
, 
    
    
    barcode
    
 as 
    
    barcode
    
, 
    
    
    grams
    
 as 
    
    grams
    
, 
    
    
    old_inventory_quantity
    
 as 
    
    old_inventory_quantity
    
, 
    
    
    inventory_quantity
    
 as 
    
    inventory_quantity
    
, 
    
    
    weight
    
 as 
    
    weight
    
, 
    
    
    weight_unit
    
 as 
    
    weight_unit
    
, 
    
    
    option_1
    
 as 
    
    option_1
    
, 
    
    
    option_2
    
 as 
    
    option_2
    
, 
    
    
    option_3
    
 as 
    
    option_3
    
, 
    
    
    tax_code
    
 as 
    
    tax_code
    




        


, cast('' as TEXT) as source_relation




    from base

),

final as (

    select
        id as variant_id,
        product_id,
        inventory_item_id,
        image_id,
        title,
        price,
        sku,
        position,
        inventory_policy,
        compare_at_price,
        fulfillment_service,
        inventory_management,
        taxable as is_taxable,
        barcode,
        grams,
        coalesce(inventory_quantity, old_inventory_quantity) as inventory_quantity,
        weight,
        weight_unit,
        option_1,
        option_2,
        option_3,
        tax_code,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_timestamp,
        cast(
    cast(cast(updated_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as updated_timestamp,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

        





    from fields
)

select * 
from final