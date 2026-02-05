
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_shipping_line_id
from "shopify"."main_stg_shopify"."stg_shopify__order_shipping_line"
where order_shipping_line_id is null



  
  
      
    ) dbt_internal_test