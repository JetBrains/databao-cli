
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select price_rule_id
from "shopify"."main_stg_shopify"."stg_shopify__price_rule"
where price_rule_id is null



  
  
      
    ) dbt_internal_test