
  
  create view "shopify"."main_stg_shopify"."stg_shopify__shop__dbt_tmp" as (
    with base as (

    select * 
    from "shopify"."main_stg_shopify"."stg_shopify__shop_tmp"
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
    
    
    address_1
    
 as 
    
    address_1
    
, 
    
    
    address_2
    
 as 
    
    address_2
    
, 
    
    
    checkout_api_supported
    
 as 
    
    checkout_api_supported
    
, 
    
    
    city
    
 as 
    
    city
    
, 
    
    
    cookie_consent_level
    
 as 
    
    cookie_consent_level
    
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
    
    
    county_taxes
    
 as 
    
    county_taxes
    
, 
    
    
    created_at
    
 as 
    
    created_at
    
, 
    
    
    currency
    
 as 
    
    currency
    
, 
    
    
    customer_email
    
 as 
    
    customer_email
    
, 
    
    
    domain
    
 as 
    
    domain
    
, 
    
    
    eligible_for_card_reader_giveaway
    
 as 
    
    eligible_for_card_reader_giveaway
    
, 
    
    
    eligible_for_payments
    
 as 
    
    eligible_for_payments
    
, 
    
    
    email
    
 as 
    
    email
    
, 
    
    
    enabled_presentment_currencies
    
 as 
    
    enabled_presentment_currencies
    
, 
    
    
    google_apps_domain
    
 as 
    
    google_apps_domain
    
, 
    
    
    google_apps_login_enabled
    
 as 
    
    google_apps_login_enabled
    
, 
    
    
    has_discounts
    
 as 
    
    has_discounts
    
, 
    
    
    has_gift_cards
    
 as 
    
    has_gift_cards
    
, 
    
    
    has_storefront
    
 as 
    
    has_storefront
    
, 
    
    
    iana_timezone
    
 as 
    
    iana_timezone
    
, 
    
    
    id
    
 as 
    
    id
    
, 
    
    
    latitude
    
 as 
    
    latitude
    
, 
    
    
    longitude
    
 as 
    
    longitude
    
, 
    
    
    money_format
    
 as 
    
    money_format
    
, 
    
    
    money_in_emails_format
    
 as 
    
    money_in_emails_format
    
, 
    
    
    money_with_currency_format
    
 as 
    
    money_with_currency_format
    
, 
    
    
    money_with_currency_in_emails_format
    
 as 
    
    money_with_currency_in_emails_format
    
, 
    
    
    myshopify_domain
    
 as 
    
    myshopify_domain
    
, 
    
    
    name
    
 as 
    
    name
    
, 
    
    
    password_enabled
    
 as 
    
    password_enabled
    
, 
    
    
    phone
    
 as 
    
    phone
    
, 
    
    
    plan_display_name
    
 as 
    
    plan_display_name
    
, 
    
    
    plan_name
    
 as 
    
    plan_name
    
, 
    
    
    pre_launch_enabled
    
 as 
    
    pre_launch_enabled
    
, 
    
    
    primary_locale
    
 as 
    
    primary_locale
    
, 
    
    
    province
    
 as 
    
    province
    
, 
    
    
    province_code
    
 as 
    
    province_code
    
, 
    
    
    requires_extra_payments_agreement
    
 as 
    
    requires_extra_payments_agreement
    
, 
    
    
    setup_required
    
 as 
    
    setup_required
    
, 
    
    
    shop_owner
    
 as 
    
    shop_owner
    
, 
    
    
    source
    
 as 
    
    source
    
, 
    
    
    tax_shipping
    
 as 
    
    tax_shipping
    
, 
    
    
    taxes_included
    
 as 
    
    taxes_included
    
, 
    
    
    timezone
    
 as 
    
    timezone
    
, 
    
    
    updated_at
    
 as 
    
    updated_at
    
, 
    
    
    weight_unit
    
 as 
    
    weight_unit
    
, 
    
    
    zip
    
 as 
    
    zip
    




        


, cast('' as TEXT) as source_relation




    from base
),

final as (
    
    select 
        id as shop_id,
        name,
        _fivetran_deleted as is_deleted,
        address_1,
        address_2,
        city,
        province,
        province_code,
        country,
        country_code,
        country_name,
        zip,
        latitude,
        longitude,
        case when county_taxes is null then false else county_taxes end as has_county_taxes,
        currency,
        enabled_presentment_currencies,
        customer_email,
        email,
        domain,
        phone,
        timezone,
        iana_timezone,
        primary_locale,
        weight_unit,
        myshopify_domain,
        cookie_consent_level,
        shop_owner,
        source,
        tax_shipping as has_shipping_taxes,
        case when taxes_included is null then false else taxes_included end as has_taxes_included_in_price,
        has_discounts,
        has_gift_cards,
        has_storefront,
        checkout_api_supported as has_checkout_api_supported,
        eligible_for_card_reader_giveaway as is_eligible_for_card_reader_giveaway,
        eligible_for_payments as is_eligible_for_payments,
        google_apps_domain,
        case when google_apps_login_enabled is null then false else google_apps_login_enabled end as is_google_apps_login_enabled,
        money_format,
        money_in_emails_format,
        money_with_currency_format,
        money_with_currency_in_emails_format,
        plan_display_name,
        plan_name,
        password_enabled as is_password_enabled,
        pre_launch_enabled as is_pre_launch_enabled,
        requires_extra_payments_agreement as is_extra_payments_agreement_required,
        setup_required as is_setup_required,
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
