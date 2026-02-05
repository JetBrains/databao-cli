with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_tmp"
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
    
    
    abandoned_checkout_url
    
 as 
    
    abandoned_checkout_url
    
, 
    
    
    billing_address_address_1
    
 as 
    
    billing_address_address_1
    
, 
    cast(null as TEXT) as 
    
    billing_address_address_2
    
 , 
    
    
    billing_address_city
    
 as 
    
    billing_address_city
    
, 
    
    
    billing_address_company
    
 as 
    
    billing_address_company
    
, 
    
    
    billing_address_country
    
 as 
    
    billing_address_country
    
, 
    
    
    billing_address_country_code
    
 as 
    
    billing_address_country_code
    
, 
    
    
    billing_address_first_name
    
 as 
    
    billing_address_first_name
    
, 
    
    
    billing_address_last_name
    
 as 
    
    billing_address_last_name
    
, 
    
    
    billing_address_latitude
    
 as 
    
    billing_address_latitude
    
, 
    
    
    billing_address_longitude
    
 as 
    
    billing_address_longitude
    
, 
    
    
    billing_address_name
    
 as 
    
    billing_address_name
    
, 
    
    
    billing_address_phone
    
 as 
    
    billing_address_phone
    
, 
    
    
    billing_address_province
    
 as 
    
    billing_address_province
    
, 
    
    
    billing_address_province_code
    
 as 
    
    billing_address_province_code
    
, 
    
    
    billing_address_zip
    
 as 
    
    billing_address_zip
    
, 
    
    
    buyer_accepts_marketing
    
 as 
    
    buyer_accepts_marketing
    
, 
    
    
    cart_token
    
 as 
    
    cart_token
    
, 
    
    
    closed_at
    
 as 
    
    closed_at
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    currency
    
 as 
    
    currency
    
, 
    
    
    customer_id
    
 as 
    
    customer_id
    
, 
    
    
    customer_locale
    
 as 
    
    customer_locale
    
, 
    
    
    device_id
    
 as 
    
    device_id
    
, 
    
    
    email
    
 as 
    
    email
    
, 
    
    
    gateway
    
 as 
    
    gateway
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    landing_site_base_url
    
 as 
    
    landing_site_base_url
    
, 
    
    
    location_id
    
 as 
    
    location_id
    
, 
    
    
    name
    
 as 
    
    name
    
, 
    
    
    note
    
 as 
    
    note
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    presentment_currency
    
 as 
    
    presentment_currency
    
, 
    
    
    referring_site
    
 as 
    
    referring_site
    
, 
    
    
    shipping_address_address_1
    
 as 
    
    shipping_address_address_1
    
, 
    cast(null as TEXT) as 
    
    shipping_address_address_2
    
 , 
    
    
    shipping_address_city
    
 as 
    
    shipping_address_city
    
, 
    
    
    shipping_address_company
    
 as 
    
    shipping_address_company
    
, 
    
    
    shipping_address_country
    
 as 
    
    shipping_address_country
    
, 
    
    
    shipping_address_country_code
    
 as 
    
    shipping_address_country_code
    
, 
    
    
    shipping_address_first_name
    
 as 
    
    shipping_address_first_name
    
, 
    
    
    shipping_address_last_name
    
 as 
    
    shipping_address_last_name
    
, 
    
    
    shipping_address_latitude
    
 as 
    
    shipping_address_latitude
    
, 
    
    
    shipping_address_longitude
    
 as 
    
    shipping_address_longitude
    
, 
    
    
    shipping_address_name
    
 as 
    
    shipping_address_name
    
, 
    
    
    shipping_address_phone
    
 as 
    
    shipping_address_phone
    
, 
    
    
    shipping_address_province
    
 as 
    
    shipping_address_province
    
, 
    
    
    shipping_address_province_code
    
 as 
    
    shipping_address_province_code
    
, 
    
    
    shipping_address_zip
    
 as 
    
    shipping_address_zip
    
, 
    
    
    source_name
    
 as 
    
    source_name
    
, 
    
    
    subtotal_price
    
 as 
    
    subtotal_price
    
, 
    
    
    taxes_included
    
 as 
    
    taxes_included
    
, 
    
    
    token
    
 as 
    
    token
    
, 
    
    
    total_discounts
    
 as 
    
    total_discounts
    
, 
    
    
    total_duties
    
 as 
    
    total_duties
    
, 
    
    
    total_line_items_price
    
 as 
    
    total_line_items_price
    
, 
    
    
    total_price
    
 as 
    
    total_price
    
, 
    
    
    total_tax
    
 as 
    
    total_tax
    
, 
    
    
    total_weight
    
 as 
    
    total_weight
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    user_id
    
 as 
    
    user_id
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        _fivetran_deleted as is_deleted,
        abandoned_checkout_url,
        billing_address_address_1,
        billing_address_address_2,
        billing_address_city,
        billing_address_company,
        billing_address_country,
        billing_address_country_code,
        billing_address_first_name,
        billing_address_last_name,
        billing_address_latitude,
        billing_address_longitude,
        billing_address_name,
        billing_address_phone,
        billing_address_province,
        billing_address_province_code,
        billing_address_zip,
        buyer_accepts_marketing as has_buyer_accepted_marketing,
        cart_token,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_at,
        cast(
    cast(cast(closed_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as closed_at,
        currency as shop_currency,
        customer_id,
        customer_locale,
        device_id,
        email,
        gateway,
        id as checkout_id,
        landing_site_base_url,
        location_id,
        name,
        note,
        phone,
        presentment_currency,
        referring_site,
        shipping_address_address_1,
        shipping_address_address_2,
        shipping_address_city,
        shipping_address_company,
        shipping_address_country,
        shipping_address_country_code,
        shipping_address_first_name,
        shipping_address_last_name,
        shipping_address_latitude,
        shipping_address_longitude,
        shipping_address_name,
        shipping_address_phone,
        shipping_address_province,
        shipping_address_province_code,
        shipping_address_zip,
        source_name,
        subtotal_price,
        taxes_included as has_taxes_included,
        token,
        total_discounts,
        total_duties,
        total_line_items_price,
        total_price,
        total_tax,
        total_weight,
        cast(
    cast(cast(updated_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as updated_at,
        user_id,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation
        
    from fields
)

select *
from final