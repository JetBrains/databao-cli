
  
  create view "shopify"."main_stg_shopify"."stg_shopify__refund_tmp__dbt_tmp" as (
    -- this model will be all NULL until you create a refund in Shopify


    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_refund_data"
  );
