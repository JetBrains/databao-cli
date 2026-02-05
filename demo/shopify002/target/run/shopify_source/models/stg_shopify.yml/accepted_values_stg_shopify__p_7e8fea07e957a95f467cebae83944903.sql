
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        target_type as value_field,
        count(*) as n_records

    from "shopify"."main_stg_shopify"."stg_shopify__price_rule"
    group by target_type

)

select *
from all_values
where value_field not in (
    'line_item','shipping_line'
)



  
  
      
    ) dbt_internal_test