
  
  create view "shopify"."main_stg_shopify"."stg_shopify__inventory_item_tmp__dbt_tmp" as (
    
    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_inventory_item_data"
  );
