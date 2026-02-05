
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_id
from "shopify"."main_stg_shopify"."stg_shopify__product_tag"
where product_id is null



  
  
      
    ) dbt_internal_test