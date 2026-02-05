
  
  create view "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_tmp__dbt_tmp" as (
    
    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_abandoned_checkout_data"
  );
