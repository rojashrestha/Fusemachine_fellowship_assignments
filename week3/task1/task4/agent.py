
import json
import time
import logging
import re
from typing import Dict, List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import psycopg2.extras

# ---------- Logging setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------- Database config (matches your docker-compose.yml) ----------
DB_CONFIG = {
    "dbname": "mydatabase",
    "user": "admin",
    "password": "secret",
    "host": "localhost",
    "port": 5432
}

# ---------- Load decompositions (from Task 3) ----------
try:
    with open("decompositions.json", "r", encoding="utf-8") as f:
        DECOMPOSITIONS = json.load(f)
    logger.info(f"Loaded {len(DECOMPOSITIONS)} decompositions")
except FileNotFoundError:
    logger.error("decompositions.json not found. Please copy it from Task 3.")
    DECOMPOSITIONS = {}

# ---------- SQL generator (rule-based) ----------
def generate_sql(decomp: Dict) -> str:
    tables = decomp["tables"]
    columns = decomp["columns"]
    filters = decomp["filters"]
    joins = decomp["joins"]

    if columns == ["*"] or columns == "*":
        select_clause = "*"
    else:
        select_clause = ", ".join(columns)

    from_clause = f'FROM {tables[0]}'

    join_clause = ""
    if joins != "None" and isinstance(joins, list):
        for j in joins:
            join_clause += f" JOIN {j.split('.')[0]} ON {j}"

    where_or_group = ""
    if filters != "None":
        if filters.startswith("GROUP BY"):
            where_or_group = filters
        elif filters.startswith("DISTINCT"):
            if "DISTINCT" in filters:
                select_clause = "DISTINCT " + select_clause
        else:
            where_or_group = f"WHERE {filters}"

    sql = f"SELECT {select_clause} {from_clause} {join_clause} {where_or_group}".strip()
    sql = " ".join(sql.split())
    return sql

# ---------- Error fixing (retry logic) ----------
def fix_sql_from_error(sql: str, error_msg: str) -> str:
    """Attempt to fix SQL based on error message."""
    error_lower = error_msg.lower()
    # Case: column does not exist -> add double quotes
    if "column" in error_lower and "does not exist" in error_lower:
        match = re.search(r'column "([^"]+)"', error_msg)
        if match:
            col = match.group(1)
            # Quote the column name in SQL (case‑sensitive)
            sql = re.sub(rf'\b{col}\b', f'"{col}"', sql, flags=re.IGNORECASE)
            logger.info(f"Fixed column '{col}' -> \"{col}\"")
    return sql

# ---------- Executor with retry (max 3 attempts) ----------
def execute_with_retry(sql: str, max_retries: int = 3) -> Tuple[bool, str, List[Dict], int]:
    current_sql = sql
    for attempt in range(1, max_retries + 1):
        conn = None
        try:
            start = time.time()
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(current_sql)
            rows = cur.fetchall()
            elapsed = int((time.time() - start) * 1000)
            result_rows = [dict(row) for row in rows]
            cur.close()
            conn.close()
            return True, current_sql, result_rows, elapsed
        except Exception as e:
            elapsed = int((time.time() - start) * 1000) if 'start' in locals() else 0
            error_msg = str(e)
            logger.warning(f"Attempt {attempt}/{max_retries} failed: {error_msg}")
            if attempt < max_retries:
                fixed_sql = fix_sql_from_error(current_sql, error_msg)
                if fixed_sql != current_sql:
                    logger.info(f"Retrying with fixed SQL: {fixed_sql}")
                    current_sql = fixed_sql
                else:
                    logger.info("No fix applied, retrying with same SQL")
            else:
                logger.error(f"All {max_retries} attempts failed.")
                return False, current_sql, [], elapsed
        finally:
            if conn:
                conn.close()
    return False, current_sql, [], 0

# ---------- Natural language summary ----------
def generate_summary(question: str, rows: List[Dict], success: bool) -> str:
    if not success:
        return "Sorry, the agent could not execute the query after multiple retries."
    if not rows:
        return "The query returned no results."
    if "count" in question.lower() or "how many" in question.lower():
        return f"Found {len(rows)} records."
    if len(rows) <= 5:
        return f"Result: {rows}"
    else:
        return f"Returned {len(rows)} rows. First 5: {rows[:5]}"

# ---------- FastAPI app ----------
app = FastAPI(title="Mini SQL Agent", description="Self-correcting Text-to-SQL agent")

class SQLRequest(BaseModel):
    question: str

class SQLResponse(BaseModel):
    sql: str
    result: List[Dict]
    summary: str
    status: str

@app.post("/agent/sql", response_model=SQLResponse)
async def agent_sql(request: SQLRequest):
    question = request.question.strip()
    logger.info(f"Received question: {question}")

    # Decompose
    if question not in DECOMPOSITIONS:
        logger.warning(f"No decomposition for '{question}'. Using fallback.")
        decomp = {
            "intent": "unknown",
            "tables": ["customers"],
            "columns": ["*"],
            "filters": "None",
            "joins": "None"
        }
    else:
        decomp = DECOMPOSITIONS[question]
    logger.info(f"Decomposition: {decomp}")

    # Generate SQL
    sql = generate_sql(decomp)
    logger.info(f"Generated SQL: {sql}")

    # Execute with retry
    success, final_sql, rows, exec_time = execute_with_retry(sql)
    logger.info(f"Execution success: {success}, rows: {len(rows)}, time: {exec_time}ms")

    # Summary
    summary = generate_summary(question, rows, success)
    status = "success" if success else "failed"

    return SQLResponse(sql=final_sql, result=rows, summary=summary, status=status)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)