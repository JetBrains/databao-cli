
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_id
from "shopify"."main_stg_shopify"."stg_shopify__customer_tag"
where customer_id is null



  
  
      
    ) dbt_internal_test