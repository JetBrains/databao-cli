
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_id
from "shopify"."main_stg_shopify"."stg_shopify__order_note_attribute"
where order_id is null



  
  
      
    ) dbt_internal_test