
  
  create view "shopify"."main_stg_shopify"."stg_shopify__inventory_item__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__inventory_item_tmp"
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
    
    
    cost
    
 as 
    
    cost
    
, 
    
    
    country_code_of_origin
    
 as 
    
    country_code_of_origin
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    province_code_of_origin
    
 as 
    
    province_code_of_origin
    
, 
    
    
    requires_shipping
    
 as 
    
    requires_shipping
    
, 
    
    
    sku
    
 as 
    
    sku
    
, 
    
    
    tracked
    
 as 
    
    tracked
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as inventory_item_id,
        sku,
        _fivetran_deleted as is_deleted, -- won't filter out for now
        cost,
        country_code_of_origin,
        province_code_of_origin,
        requires_shipping as is_shipping_required,
        tracked as is_inventory_quantity_tracked,
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
  );
