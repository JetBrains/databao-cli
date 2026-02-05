
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment"
    group by status

)

select *
from all_values
where value_field not in (
    'pending','open','success','cancelled','error','failure'
)



  
  
      
    ) dbt_internal_test