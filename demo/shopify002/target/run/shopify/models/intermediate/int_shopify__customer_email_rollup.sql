
  
  create view "shopify"."main"."int_shopify__customer_email_rollup__dbt_tmp" as (
    with customers as (

    select 
        *,
        row_number() over(
            partition by 


    email


            order by created_timestamp desc) 
            as customer_index

    from "shopify"."main_stg_shopify"."stg_shopify__customer"
    where email is not null -- nonsensical to include any null emails here

), customer_tags as (

    select 
        *
    from "shopify"."main_stg_shopify"."stg_shopify__customer_tag"

), rollup_customers as (

    select
        -- fields to group by
        lower(customers.email) as email,
        customers.source_relation,

        -- fields to string agg together
        
    string_agg(distinct cast(customers.customer_id as TEXT), ', ')

 as customer_ids,
        
    string_agg(distinct cast(customers.phone as TEXT), ', ')

 as phone_numbers,
        
    string_agg(distinct cast(customer_tags.value as TEXT), ', ')

 as customer_tags,

        -- fields to take aggregates of
        min(customers.created_timestamp) as first_account_created_at,
        max(customers.created_timestamp) as last_account_created_at,
        max(customers.updated_timestamp) as last_updated_at,
        max(customers.marketing_consent_updated_at) as marketing_consent_updated_at,
        max(customers._fivetran_synced) as last_fivetran_synced,

        -- take true if ever given for boolean fields
        

    bool_or( case when customers.customer_index = 1 then customers.is_tax_exempt else null end )

 as is_tax_exempt, -- since this changes every year
        

    bool_or( customers.is_verified_email )

 as is_verified_email

        -- for all other fields, just take the latest value
        
        
        
            
        
            
        
            
            , max(case when customers.customer_index = 1 then customers.first_name else null end) as first_name
            
        
            
            , max(case when customers.customer_index = 1 then customers.last_name else null end) as last_name
            
        
            
        
            
            , max(case when customers.customer_index = 1 then customers.default_address_id else null end) as default_address_id
            
        
            
        
            
            , max(case when customers.customer_index = 1 then customers.account_state else null end) as account_state
            
        
            
        
            
        
            
        
            
            , max(case when customers.customer_index = 1 then customers.note else null end) as note
            
        
            
            , max(case when customers.customer_index = 1 then customers.currency else null end) as currency
            
        
            
            , max(case when customers.customer_index = 1 then customers.marketing_consent_state else null end) as marketing_consent_state
            
        
            
            , max(case when customers.customer_index = 1 then customers.marketing_opt_in_level else null end) as marketing_opt_in_level
            
        
            
        
            
        
            
        
            
        
            
        

    from customers 
    left join customer_tags
        on customers.customer_id = customer_tags.customer_id
        and customers.source_relation = customer_tags.source_relation

    group by 1,2

)

select *
from rollup_customers
  );
