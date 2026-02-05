
  
  create view "shopify"."main_stg_shopify"."stg_shopify__discount_code__dbt_tmp" as (
    -- this model will be all NULL until you create a discount code in Shopify

with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__discount_code_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    code
    
 as 
    
    code
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    price_rule_id
    
 as 
    
    price_rule_id
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    usage_count
    
 as 
    
    usage_count
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as discount_code_id,
        upper(code) as code,
        price_rule_id,
        usage_count,
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
