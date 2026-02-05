with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__price_rule_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    allocation_limit
    
 as 
    
    allocation_limit
    
, 
    
    
    allocation_method
    
 as 
    
    allocation_method
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    customer_selection
    
 as 
    
    customer_selection
    
, 
    
    
    ends_at
    
 as 
    
    ends_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    once_per_customer
    
 as 
    
    once_per_customer
    
, 
    
    
    prerequisite_quantity_range
    
 as 
    
    prerequisite_quantity_range
    
, 
    
    
    prerequisite_shipping_price_range
    
 as 
    
    prerequisite_shipping_price_range
    
, 
    
    
    prerequisite_subtotal_range
    
 as 
    
    prerequisite_subtotal_range
    
, 
    
    
    prerequisite_to_entitlement_purchase_prerequisite_amount
    
 as 
    
    prerequisite_to_entitlement_purchase_prerequisite_amount
    
, 
    
    
    quantity_ratio_entitled_quantity
    
 as 
    
    quantity_ratio_entitled_quantity
    
, 
    
    
    quantity_ratio_prerequisite_quantity
    
 as 
    
    quantity_ratio_prerequisite_quantity
    
, 
    
    
    starts_at
    
 as 
    
    starts_at
    
, 
    
    
    target_selection
    
 as 
    
    target_selection
    
, 
    
    
    target_type
    
 as 
    
    target_type
    
, 
    
    
    title
    
 as 
    
    title
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    usage_limit
    
 as 
    
    usage_limit
    
, 
    
    
    value
    
 as 
    
    value
    
, 
    
    
    value_type
    
 as 
    
    value_type
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select
        id as price_rule_id,
        allocation_limit,
        allocation_method,
        customer_selection,
        once_per_customer as is_once_per_customer,
        prerequisite_quantity_range as prereq_min_quantity,
        prerequisite_shipping_price_range as prereq_max_shipping_price,
        prerequisite_subtotal_range as prereq_min_subtotal,
        prerequisite_to_entitlement_purchase_prerequisite_amount as prereq_min_purchase_quantity_for_entitlement,
        quantity_ratio_entitled_quantity as prereq_buy_x_get_this,
        quantity_ratio_prerequisite_quantity as prereq_buy_this_get_y,
        target_selection,
        target_type,
        title,
        usage_limit,
        value,
        value_type,
        cast(
    cast(cast(starts_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as starts_at,
        cast(
    cast(cast(ends_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as ends_at,
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
)

select *
from final