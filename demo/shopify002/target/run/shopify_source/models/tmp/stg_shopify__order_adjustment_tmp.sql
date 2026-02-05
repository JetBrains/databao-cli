
  
  create view "shopify"."main_stg_shopify"."stg_shopify__order_adjustment_tmp__dbt_tmp" as (
    -- this model will be all NULL until you have made an order adjustment in Shopify


    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_order_adjustment_data"
  );
