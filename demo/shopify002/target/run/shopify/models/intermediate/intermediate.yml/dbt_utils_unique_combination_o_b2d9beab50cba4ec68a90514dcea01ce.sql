
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        email, source_relation
    from "shopify"."main"."int_shopify__customer_email_rollup"
    group by email, source_relation
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test