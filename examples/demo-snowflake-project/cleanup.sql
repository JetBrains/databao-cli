-- ============================================================
-- CLEANUP: Drop all objects created by setup-oauth.sql for a given suffix.
-- Set the same suffix you used in setup-oauth.sql, then run this script.
-- ============================================================

SET suffix          = 'DEMO';

-- Derived object names (must match setup-oauth.sql)
SET database_name   = 'STREAMLIT_DATABAO_DB_' || $suffix;
SET app_warehouse   = 'STREAMLIT_DATABAO_WAREHOUSE_' || $suffix;
SET git_integration = 'STREAMLIT_DATABAO_GIT_INTEGRATION_' || $suffix;
SET app_eai         = 'STREAMLIT_DATABAO_EAI_' || $suffix;
SET secrets_access  = 'STREAMLIT_DATABAO_SECRETS_ACCESS_' || $suffix;

-- Database (cascades: Streamlit app, UDF, secrets, git repo, network rule)
DROP DATABASE IF EXISTS IDENTIFIER($database_name);

-- External access integrations
DROP INTEGRATION IF EXISTS IDENTIFIER($secrets_access);
DROP INTEGRATION IF EXISTS IDENTIFIER($app_eai);

-- API integration (git)
DROP INTEGRATION IF EXISTS IDENTIFIER($git_integration);

-- Warehouse
DROP WAREHOUSE IF EXISTS IDENTIFIER($app_warehouse);

SELECT 'Streamlit app STREAMLIT_DATABAO_APP_' || $suffix || ' cleaned up successfully.' AS STATUS;