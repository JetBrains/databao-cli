
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select collection_id
from "shopify"."main_stg_shopify"."stg_shopify__collection_product"
where collection_id is null



  
  
      
    ) dbt_internal_test