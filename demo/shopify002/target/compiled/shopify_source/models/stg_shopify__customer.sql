with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__customer_tmp"

),

fields as (

    select
    
        
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    
    
    accepts_marketing
    
 as 
    
    accepts_marketing
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    default_address_id
    
 as 
    
    default_address_id
    
, 
    
    
    email
    
 as 
    
    email
    
, 
    
    
    first_name
    
 as 
    
    first_name
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    last_name
    
 as 
    
    last_name
    
, 
    
    
    orders_count
    
 as 
    
    orders_count
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    state
    
 as 
    
    state
    
, 
    
    
    tax_exempt
    
 as 
    
    tax_exempt
    
, 
    
    
    total_spent
    
 as 
    
    total_spent
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    verified_email
    
 as 
    
    verified_email
    
, 
    cast(null as timestamp) as 
    
    email_marketing_consent_consent_updated_at
    
 , 
    cast(null as TEXT) as 
    
    email_marketing_consent_opt_in_level
    
 , 
    cast(null as TEXT) as 
    
    email_marketing_consent_state
    
 , 
    cast(null as TEXT) as 
    
    note
    
 , 
    cast(null as timestamp) as 
    
    accepts_marketing_updated_at
    
 , 
    cast(null as TEXT) as 
    
    marketing_opt_in_level
    
 , 
    cast(null as TEXT) as 
    
    currency
    
 



        


, cast('' as TEXT) as source_relation




    from base

),

final as (

    select 
        id as customer_id,
        lower(email) as email,
        first_name,
        last_name,
        orders_count,
        default_address_id,
        phone,
        lower(state) as account_state,
        tax_exempt as is_tax_exempt,
        total_spent,
        verified_email as is_verified_email,
        note,
        currency,
        case 
            when email_marketing_consent_state is null then
                case 
                    when accepts_marketing is null then null
                    when accepts_marketing then 'subscribed (legacy)' 
                    else 'not_subscribed (legacy)' end
            else lower(email_marketing_consent_state) end as marketing_consent_state,
        lower(coalesce(email_marketing_consent_opt_in_level, marketing_opt_in_level)) as marketing_opt_in_level,

        cast(
    cast(cast(coalesce(accepts_marketing_updated_at, email_marketing_consent_consent_updated_at) as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as marketing_consent_updated_at,
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