
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select transactions_unique_id
from "shopify"."main"."shopify__transactions"
where transactions_unique_id is null



  
  
      
    ) dbt_internal_test