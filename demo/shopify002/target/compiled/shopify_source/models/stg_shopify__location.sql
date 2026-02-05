with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__location_tmp"
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
    
    
    active
    
 as 
    
    active
    
, 
    
    
    address_1
    
 as 
    
    address_1
    
, 
    
    
    address_2
    
 as 
    
    address_2
    
, 
    
    
    city
    
 as 
    
    city
    
, 
    
    
    country
    
 as 
    
    country
    
, 
    
    
    country_code
    
 as 
    
    country_code
    
, 
    
    
    country_name
    
 as 
    
    country_name
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    legacy
    
 as 
    
    legacy
    
, 
    
    
    localized_country_name
    
 as 
    
    localized_country_name
    
, 
    
    
    localized_province_name
    
 as 
    
    localized_province_name
    
, 
    
    
    name
    
 as 
    
    name
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    province
    
 as 
    
    province
    
, 
    
    
    province_code
    
 as 
    
    province_code
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    zip
    
 as 
    
    zip
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as location_id,
        name,
        _fivetran_deleted as is_deleted,
        active as is_active,
        address_1,
        address_2,
        city,
        country,
        country_code,
        country_name,
        legacy as is_legacy,
        localized_country_name,
        localized_province_name,
        phone,
        province,
        province_code,
        zip,
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