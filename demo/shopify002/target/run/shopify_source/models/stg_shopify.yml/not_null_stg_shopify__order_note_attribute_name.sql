
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select name
from "shopify"."main_stg_shopify"."stg_shopify__order_note_attribute"
where name is null



  
  
      
    ) dbt_internal_test