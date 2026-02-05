
  
  create view "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_discount_code__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_discount_code_tmp"
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
    
    
    checkout_id
    
 as 
    
    checkout_id
    
, 
    
    
    code
    
 as 
    
    code
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    discount_id
    
 as 
    
    discount_id
    
, 
    
    
    index
    
 as 
    
    index
    
, 
    
    
    type
    
 as 
    
    type
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        checkout_id,
        upper(code) as code,
        discount_id,
        amount,
        type,
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
        source_relation, 
        case when checkout_id is null and code is null and index is null
            then row_number() over(partition by source_relation order by source_relation)
            else row_number() over(partition by checkout_id, upper(code), source_relation order by index desc)
        end as index

    from fields
    
)

select *
from final
where index = 1
  );
