with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__collection_tmp"
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
    
    
    disjunctive
    
 as 
    
    disjunctive
    
, 
    
    
    handle
    
 as 
    
    handle
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    published_at
    
 as 
    
    published_at
    
, 
    
    
    published_scope
    
 as 
    
    published_scope
    
, 
    
    
    rules
    
 as 
    
    rules
    
, 
    
    
    sort_order
    
 as 
    
    sort_order
    
, 
    
    
    title
    
 as 
    
    title
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as collection_id,
        _fivetran_deleted as is_deleted,
        case 
            when disjunctive is null then null
            when disjunctive then 'disjunctive'
            else 'conjunctive' end as rule_logic,
        handle,
        published_scope,
        rules,
        sort_order,
        title,
        cast(
    cast(cast(published_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as published_at,
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