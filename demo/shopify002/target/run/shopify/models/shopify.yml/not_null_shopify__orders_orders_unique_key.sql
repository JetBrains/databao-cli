
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select orders_unique_key
from "shopify"."main"."shopify__orders"
where orders_unique_key is null



  
  
      
    ) dbt_internal_test