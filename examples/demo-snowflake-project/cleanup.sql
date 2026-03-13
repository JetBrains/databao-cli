-- ============================================================
-- CLEANUP: Drop all objects created by setup.sql for a given suffix.
-- Set the same suffix you used in setup.sql, then run this script.
-- ============================================================

SET suffix = 'DEMO';

USE ROLE ACCOUNTADMIN;

DECLARE
  _sql             VARCHAR;

  -- Derived object names (must match setup.sql)
  _db              VARCHAR DEFAULT 'STREAMLIT_DATABAO_DB_' || $suffix;
  _wh              VARCHAR DEFAULT 'STREAMLIT_DATABAO_WAREHOUSE_' || $suffix;
  _user            VARCHAR DEFAULT 'STREAMLIT_DATABAO_USER_' || $suffix;
  _network_policy  VARCHAR DEFAULT 'STREAMLIT_DATABAO_NETWORK_POLICY_' || $suffix;
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

  -- User (unset network policy first, then drop)
  _sql := 'ALTER USER IF EXISTS ' || :_user || ' UNSET NETWORK_POLICY';
  EXECUTE IMMEDIATE :_sql;
  EXECUTE IMMEDIATE 'DROP USER IF EXISTS ' || :_user;

  -- Network policy
  EXECUTE IMMEDIATE 'DROP NETWORK POLICY IF EXISTS ' || :_network_policy;

  -- Warehouse
  EXECUTE IMMEDIATE 'DROP WAREHOUSE IF EXISTS ' || :_wh;
END;
