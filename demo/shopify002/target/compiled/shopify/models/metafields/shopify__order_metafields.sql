








with source_table as (
    select *
    from "shopify"."main_stg_shopify"."stg_shopify__order"
)

,
lookup_object as (
    select 
        *,
        
  
    (
      
      case
      when metafield_reference = 'blade_runner_returnauthorizations'
        then value
      else null
      end
    )
    
      
        as blade_runner_returnauthorizations
      
    
    
  

    from "shopify"."main_stg_shopify"."stg_shopify__metafield"
    where is_most_recent_record
),

final as (
    select
        
            source_table.order_id,
        
            source_table.user_id,
        
            source_table.total_discounts,
        
            source_table.total_discounts_set,
        
            source_table.total_line_items_price,
        
            source_table.total_line_items_price_set,
        
            source_table.total_price,
        
            source_table.total_price_set,
        
            source_table.total_tax_set,
        
            source_table.total_tax,
        
            source_table.source_name,
        
            source_table.subtotal_price,
        
            source_table.has_taxes_included,
        
            source_table.total_weight,
        
            source_table.total_tip_received,
        
            source_table.landing_site_base_url,
        
            source_table.location_id,
        
            source_table.name,
        
            source_table.note,
        
            source_table.number,
        
            source_table.order_number,
        
            source_table.cancel_reason,
        
            source_table.cart_token,
        
            source_table.checkout_token,
        
            source_table.created_timestamp,
        
            source_table.cancelled_timestamp,
        
            source_table.closed_timestamp,
        
            source_table.processed_timestamp,
        
            source_table.updated_timestamp,
        
            source_table.currency,
        
            source_table.customer_id,
        
            source_table.email,
        
            source_table.financial_status,
        
            source_table.fulfillment_status,
        
            source_table.referring_site,
        
            source_table.billing_address_address_1,
        
            source_table.billing_address_address_2,
        
            source_table.billing_address_city,
        
            source_table.billing_address_company,
        
            source_table.billing_address_country,
        
            source_table.billing_address_country_code,
        
            source_table.billing_address_first_name,
        
            source_table.billing_address_last_name,
        
            source_table.billing_address_latitude,
        
            source_table.billing_address_longitude,
        
            source_table.billing_address_name,
        
            source_table.billing_address_phone,
        
            source_table.billing_address_province,
        
            source_table.billing_address_province_code,
        
            source_table.billing_address_zip,
        
            source_table.browser_ip,
        
            source_table.total_shipping_price_set,
        
            source_table.shipping_address_address_1,
        
            source_table.shipping_address_address_2,
        
            source_table.shipping_address_city,
        
            source_table.shipping_address_company,
        
            source_table.shipping_address_country,
        
            source_table.shipping_address_country_code,
        
            source_table.shipping_address_first_name,
        
            source_table.shipping_address_last_name,
        
            source_table.shipping_address_latitude,
        
            source_table.shipping_address_longitude,
        
            source_table.shipping_address_name,
        
            source_table.shipping_address_phone,
        
            source_table.shipping_address_province,
        
            source_table.shipping_address_province_code,
        
            source_table.shipping_address_zip,
        
            source_table.token,
        
            source_table.app_id,
        
            source_table.checkout_id,
        
            source_table.client_details_user_agent,
        
            source_table.customer_locale,
        
            source_table.order_status_url,
        
            source_table.presentment_currency,
        
            source_table.is_test_order,
        
            source_table.is_deleted,
        
            source_table.has_buyer_accepted_marketing,
        
            source_table.is_confirmed,
        
            source_table._fivetran_synced,
        
            source_table.source_relation
        
        
            , max(lookup_object.blade_runner_returnauthorizations) as metafield_blade_runner_returnauthorizations
        
    from source_table
    left join lookup_object 
        on lookup_object.owner_resource_id = source_table.order_id
        and lookup_object.owner_resource = 'order'
    group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80
)

select *
from final

