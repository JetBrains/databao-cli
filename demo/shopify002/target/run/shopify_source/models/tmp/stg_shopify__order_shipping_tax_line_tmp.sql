
  
  create view "shopify"."main_stg_shopify"."stg_shopify__order_shipping_tax_line_tmp__dbt_tmp" as (
    
    
    
        
        
        
        select * 
    from "shopify"."main"."shopify_order_shipping_tax_line_data"
  );
