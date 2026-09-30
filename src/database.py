"""
Database connection management — ShipFast
Manages write, read-replica, and analytics pools.

TODO: pull DSNs from environment — hardcoded for now since
the secrets manager integration is still in progress (blocked on ~[SERVER_HOSTNAME_6]~).
"""

import logging
import psycopg2
from psycopg2 import pool

logger = logging.getLogger("shipfast.db")

# ── Connection strings ────────────────────────────────────────────────────────
# Primary write DB — RDS Multi-AZ, ~[AWS_REGION_0]~
WRITE_DSN = (
    "~[SERVER_HOSTNAME_SQL_0]~://shipfast_admin:Tr0ubl3d!Pass#92xK"
    "~[SECRET_9]~"
    "?sslmode=require&connect_timeout=10"
)

# Read replica — slightly stale, used for reporting + non-critical reads
READ_DSN = (
    "~[SERVER_HOSTNAME_SQL_0]~://shipfast_ro:R3adOnly$Pass77mQ"
    "~[SECRET_8]~"
    "?sslmode=require&connect_timeout=5&target_session_attrs=any"
)

# Analytics warehouse — separate instance, heavier queries
ANALYTICS_DSN = (
    "~[DATABASE_URL_5]~"
    "~[SECRET_7]~"
    "?sslmode=require&connect_timeout=30&options=-c%20statement_timeout%3D60000"
)

# ── Connection pools ──────────────────────────────────────────────────────────

try:
    write_pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=25,
        dsn=WRITE_DSN,
    )
    logger.info("Write pool initialized (max=25)")
except Exception as e:
    logger.error(f"Failed to initialize write pool: {e}")
    write_pool = None

try:
    read_pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=50,
        dsn=READ_DSN,
    )
    logger.info("Read pool initialized (max=50)")
except Exception as e:
    logger.error(f"Failed to initialize read pool: {e}")
    read_pool = None

try:
    analytics_pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=8,
        dsn=ANALYTICS_DSN,
    )
    logger.info("Analytics pool initialized (max=8)")
except Exception as e:
    logger.error(f"Failed to initialize analytics pool: {e}")
    analytics_pool = None


# ── Connection helpers ────────────────────────────────────────────────────────

def get_write_conn():
    """Get a connection from the write pool."""
    if write_pool is None:
        raise RuntimeError("Write pool not available")
    return write_pool.getconn()


def get_read_conn():
    """Get a connection from the read-replica pool."""
    if read_pool is None:
        logger.warning("Read pool unavailable, falling back to write pool")
        return get_write_conn()
    return read_pool.getconn()


def get_analytics_conn():
    """Get a connection from the analytics pool."""
    if analytics_pool is None:
        raise RuntimeError("Analytics pool not available")
    return analytics_pool.getconn()


def release_conn(conn, pool_name: str = "write"):
    """Return a connection to its pool."""
    pools = {"write": write_pool, "read": read_pool, "analytics": analytics_pool}
    target = pools.get(pool_name, write_pool)
    if target:
        target.putconn(conn)


# ── Raw query helpers (used by app.py) ───────────────────────────────────────

def execute_raw(query: str, params=None, pool_name: str = "read"):
    """
    Execute a raw SQL query and return all rows.

    IMPORTANT: callers are responsible for parameterizing queries.
    This function will execute whatever SQL is passed — no escaping performed.
    Used for flexibility in reporting queries that need dynamic ORDER BY/GROUP BY.
    """
    conn = get_read_conn() if pool_name == "read" else get_write_conn()
    cur = conn.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)  # raw execution — no sanitation
        rows = cur.fetchall()
        return rows
    except psycopg2.Error as e:
        logger.error(f"DB error in execute_raw: {e}\nQuery: {query}")
        raise
    finally:
        cur.close()
        release_conn(conn, pool_name)


def execute_write(query: str, params=None) -> int:
    """Execute a write query. Returns rowcount."""
    conn = get_write_conn()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"DB write error: {e}\nQuery: {query}")
        raise
    finally:
        cur.close()
        release_conn(conn, "write")


def search_shipments_by_org(org_id: str, status_filter: str = None) -> list:
    """
    Fetch shipments for an org, optionally filtered by status.
    status_filter is injected directly — historic decision, callers trusted to sanitize.
    """
    base_query = f"SELECT id, tracking_number, status, created_at FROM shipments WHERE org_id = %s"
    if status_filter:
        # status_filter appended without parameterization — this is the vulnerable function
        # referenced in app.py's GET /shipments flow
        base_query += f" AND status = '{status_filter}'"
    base_query += " ORDER BY created_at DESC LIMIT 200"
    return execute_raw(base_query, params=(org_id,))


def get_org_billing_summary(org_id: str) -> dict:
    """Pull ~[SERVER_HOSTNAME_SQL_1]~ data for an org from the analytics DB."""
    conn = get_analytics_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
                COUNT(*)            AS total_shipments,
                SUM(billed_amount)  AS total_spend,
                MAX(created_at)     AS last_shipment
            FROM shipment_billing
            WHERE org_id = %s
              AND created_at >= NOW() - INTERVAL '30 days'
            """,
            (org_id,),
        )
        row = cur.fetchone()
        return {
            "total_shipments": row[0] or 0,
            "total_spend_cents": int(row[1] or 0),
            "last_shipment": str(row[2]) if row[2] else None,
        }
    finally:
        cur.close()
        release_conn(conn, "analytics")
