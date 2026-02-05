
  
  create view "shopify"."main_stg_shopify"."stg_shopify__order__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__order_tmp"

),

fields as (

    select
    
        
    
    
    id
    
 as 
    
    id
    
, 
    
    
    processed_at
    
 as 
    
    processed_at
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    user_id
    
 as 
    
    user_id
    
, 
    
    
    total_discounts
    
 as 
    
    total_discounts
    
, 
    cast(null as TEXT) as 
    
    total_discounts_set
    
 , 
    
    
    total_line_items_price
    
 as 
    
    total_line_items_price
    
, 
    cast(null as TEXT) as 
    
    total_line_items_price_set
    
 , 
    
    
    total_price
    
 as 
    
    total_price
    
, 
    cast(null as TEXT) as 
    
    total_price_set
    
 , 
    cast(null as TEXT) as 
    
    total_tax_set
    
 , 
    
    
    total_tax
    
 as 
    
    total_tax
    
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
    
    
    total_weight
    
 as 
    
    total_weight
    
, 
    cast(null as float) as 
    
    total_tip_received
    
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
    
    
    number
    
 as 
    
    number
    
, 
    
    
    order_number
    
 as 
    
    order_number
    
, 
    
    
    cancel_reason
    
 as 
    
    cancel_reason
    
, 
    
    
    cancelled_at
    
 as 
    
    cancelled_at
    
, 
    
    
    cart_token
    
 as 
    
    cart_token
    
, 
    
    
    checkout_token
    
 as 
    
    checkout_token
    
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
    
    
    email
    
 as 
    
    email
    
, 
    
    
    financial_status
    
 as 
    
    financial_status
    
, 
    
    
    fulfillment_status
    
 as 
    
    fulfillment_status
    
, 
    
    
    referring_site
    
 as 
    
    referring_site
    
, 
    
    
    billing_address_address_1
    
 as 
    
    billing_address_address_1
    
, 
    
    
    billing_address_address_2
    
 as 
    
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
    
    
    browser_ip
    
 as 
    
    browser_ip
    
, 
    
    
    buyer_accepts_marketing
    
 as 
    
    buyer_accepts_marketing
    
, 
    
    
    total_shipping_price_set
    
 as 
    
    total_shipping_price_set
    
, 
    
    
    shipping_address_address_1
    
 as 
    
    shipping_address_address_1
    
, 
    
    
    shipping_address_address_2
    
 as 
    
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
    
    
    test
    
 as 
    
    test
    
, 
    
    
    token
    
 as 
    
    token
    
, 
    
    
    _fivetran_synced
    
 as 
    
    _fivetran_synced
    
, 
    cast(null as boolean) as 
    
    _fivetran_deleted
    
 , 
    cast(null as integer) as 
    
    app_id
    
 , 
    cast(null as integer) as 
    
    checkout_id
    
 , 
    cast(null as TEXT) as 
    
    client_details_user_agent
    
 , 
    cast(null as TEXT) as 
    
    customer_locale
    
 , 
    cast(null as TEXT) as 
    
    order_status_url
    
 , 
    cast(null as TEXT) as 
    
    presentment_currency
    
 , 
    cast(null as boolean) as 
    
    confirmed
    
 



        


, cast('' as TEXT) as source_relation




    from base

),

final as (

    select 
        id as order_id,
        user_id,
        total_discounts,
        total_discounts_set,
        total_line_items_price,
        total_line_items_price_set,
        total_price,
        total_price_set,
        total_tax_set,
        total_tax,
        source_name,
        subtotal_price,
        taxes_included as has_taxes_included,
        total_weight,
        total_tip_received,
        landing_site_base_url,
        location_id,
        name,
        note,
        number,
        order_number,
        cancel_reason,
        cart_token,
        checkout_token,
        cast(
    cast(cast(created_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as created_timestamp,
        cast(
    cast(cast(cancelled_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as cancelled_timestamp,
        cast(
    cast(cast(closed_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as closed_timestamp,
        cast(
    cast(cast(processed_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as processed_timestamp,
        cast(
    cast(cast(updated_at as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as updated_timestamp,
        currency,
        customer_id,
        lower(email) as email,
        financial_status,
        fulfillment_status,
        referring_site,
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
        browser_ip,
        total_shipping_price_set,
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
        token,
        app_id,
        checkout_id,
        client_details_user_agent,
        customer_locale,
        order_status_url,
        presentment_currency,
        test as is_test_order,
        _fivetran_deleted as is_deleted,
        buyer_accepts_marketing as has_buyer_accepted_marketing,
        confirmed as is_confirmed,
        cast(
    cast(cast(_fivetran_synced as timestamp) as timestamp)
        at time zone 'UTC' at time zone 'UTC' as timestamp
) as _fivetran_synced,
        source_relation

        





    from fields
)

select * 
from final
where not coalesce(is_test_order, false)
and not coalesce(is_deleted, false)
  );
