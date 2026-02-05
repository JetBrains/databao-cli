
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select key
from "shopify"."main_stg_shopify"."stg_shopify__order_url_tag"
where key is null



  
  
      
    ) dbt_internal_test