
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        product_id, index, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__product_tag"
    group by product_id, index, source_relation
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test