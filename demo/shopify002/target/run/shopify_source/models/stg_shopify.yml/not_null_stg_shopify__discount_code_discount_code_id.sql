
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select discount_code_id
from "shopify"."main_stg_shopify"."stg_shopify__discount_code"
where discount_code_id is null



  
  
      
    ) dbt_internal_test