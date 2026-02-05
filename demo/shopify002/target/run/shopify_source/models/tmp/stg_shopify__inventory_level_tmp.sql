
  
  create view "shopify"."main_stg_shopify"."stg_shopify__inventory_level_tmp__dbt_tmp" as (
    
    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_inventory_level_data"
  );
