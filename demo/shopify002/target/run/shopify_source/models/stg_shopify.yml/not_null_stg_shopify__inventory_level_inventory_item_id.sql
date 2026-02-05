
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select inventory_item_id
from "shopify"."main_stg_shopify"."stg_shopify__inventory_level"
where inventory_item_id is null



  
  
      
    ) dbt_internal_test