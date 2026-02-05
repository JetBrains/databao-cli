
  
    
    

    create  table
      "shopify"."main_stg_shopify"."stg_shopify__metafield__dbt_tmp"
  
    as (
      with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__metafield_tmp"
),

fields as (

    select
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    description
    
 as 
    
    description
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    key
    
 as 
    
    key
    
, 
    
    
    namespace
    
 as 
    
    namespace
    
, 
    
    
    owner_id
    
 as 
    
    owner_id
    
, 
    
    
    owner_resource
    
 as 
    
    owner_resource
    
, 
    
    
    type
    
 as 
    
    type
    
, 
    
    
    value_type
    
 as 
    
    value_type
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    value
    
 as 
    
    value
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as metafield_id,
        description,
        namespace,
        key,
        value,
        lower(coalesce(type, value_type)) as value_type,
        owner_id as owner_resource_id,
        lower(owner_resource) as owner_resource,
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
        lower(namespace || '_' || key) as metafield_reference,
        case when id is null and updated_at is null
            then row_number() over(partition by source_relation order by source_relation) = 1
            else row_number() over(partition by id, source_relation order by updated_at desc) = 1
        end as is_most_recent_record,
        source_relation
        
    from fields
)

select *
from final
    );
  
  