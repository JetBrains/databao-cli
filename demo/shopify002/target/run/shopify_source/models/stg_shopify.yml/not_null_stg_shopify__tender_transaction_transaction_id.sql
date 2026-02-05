
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select transaction_id
from "shopify"."main_stg_shopify"."stg_shopify__tender_transaction"
where transaction_id is null



  
  
      
    ) dbt_internal_test