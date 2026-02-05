
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        order_id, index, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__order_discount_code"
    group by order_id, index, source_relation
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test