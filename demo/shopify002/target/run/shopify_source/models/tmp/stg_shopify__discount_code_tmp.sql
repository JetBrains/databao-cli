
  
  create view "shopify"."main_stg_shopify"."stg_shopify__discount_code_tmp__dbt_tmp" as (
    -- this model will be all NULL until you create a discount code in Shopify


    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_discount_code_data"
  );
