
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        product_image_id, product_id, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__product_image"
    group by product_image_id, product_id, source_relation
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test