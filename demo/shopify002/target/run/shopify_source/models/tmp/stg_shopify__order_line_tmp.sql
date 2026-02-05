
  
  create view "shopify"."main_stg_shopify"."stg_shopify__order_line_tmp__dbt_tmp" as (
    
    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_order_line_data"
  );
