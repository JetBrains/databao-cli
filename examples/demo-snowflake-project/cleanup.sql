-- ============================================================
-- CLEANUP: Drop all objects created by setup.sql for a given suffix.
-- Set the same suffix you used in setup.sql, then run this script.
-- ============================================================

SET suffix = 'DEMO';

USE ROLE ACCOUNTADMIN;

-- Bootstrap warehouse: needed for expression evaluation in the scripting block.
CREATE WAREHOUSE IF NOT EXISTS STREAMLIT_DATABAO_BOOTSTRAP_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
USE WAREHOUSE STREAMLIT_DATABAO_BOOTSTRAP_WH;

DECLARE
  -- Derived object names (must match setup.sql)
  _db              VARCHAR DEFAULT 'STREAMLIT_DATABAO_DB_' || $suffix;
  _wh              VARCHAR DEFAULT 'STREAMLIT_DATABAO_WAREHOUSE_' || $suffix;
  _git_integration VARCHAR DEFAULT 'STREAMLIT_DATABAO_GIT_INTEGRATION_' || $suffix;
  _eai             VARCHAR DEFAULT 'STREAMLIT_DATABAO_EAI_' || $suffix;
  _secrets_access  VARCHAR DEFAULT 'STREAMLIT_DATABAO_SECRETS_ACCESS_' || $suffix;
  _compute_pool    VARCHAR DEFAULT 'STREAMLIT_DATABAO_COMPUTE_POOL_' || $suffix;
BEGIN
  -- Database (cascades: Streamlit app, UDF, secrets, git repo, network rule)
  EXECUTE IMMEDIATE 'DROP DATABASE IF EXISTS ' || :_db;

  -- Compute pool
  EXECUTE IMMEDIATE 'DROP COMPUTE POOL IF EXISTS ' || :_compute_pool;

  -- External access integrations
  EXECUTE IMMEDIATE 'DROP INTEGRATION IF EXISTS ' || :_secrets_access;
  EXECUTE IMMEDIATE 'DROP INTEGRATION IF EXISTS ' || :_eai;

  -- API integration (git)
  EXECUTE IMMEDIATE 'DROP INTEGRATION IF EXISTS ' || :_git_integration;

  -- Warehouse
  EXECUTE IMMEDIATE 'DROP WAREHOUSE IF EXISTS ' || :_wh;
END;

DROP WAREHOUSE IF EXISTS STREAMLIT_DATABAO_BOOTSTRAP_WH;

SELECT 'Streamlit app STREAMLIT_DATABAO_APP_' || $suffix || ' cleaned up successfully.' AS STATUS;
