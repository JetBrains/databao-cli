
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select fulfillment_id
from "shopify"."main_stg_shopify"."stg_shopify__fulfillment"
where fulfillment_id is null



  
  
      
    ) dbt_internal_test