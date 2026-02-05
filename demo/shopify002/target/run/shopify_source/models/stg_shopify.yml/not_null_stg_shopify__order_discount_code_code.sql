
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select code
from "shopify"."main_stg_shopify"."stg_shopify__order_discount_code"
where code is null



  
  
      
    ) dbt_internal_test