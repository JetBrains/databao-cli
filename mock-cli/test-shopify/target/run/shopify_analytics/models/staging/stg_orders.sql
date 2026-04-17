
  
  create view "shopify"."main"."stg_orders__dbt_tmp" as (
    select * from "shopify"."main"."orders"
  );
