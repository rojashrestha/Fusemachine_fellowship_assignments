import json
import csv
import psycopg2
import psycopg2.extras
from typing import Dict, List, Tuple

DB_CONFIG = {
    "dbname": "mydatabase",
    "user": "admin",
    "password": "secret",
    "host": "localhost",
    "port": 5432
}

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
                where_or_group = ""
        else:
            where_or_group = f"WHERE {filters}"
    else:
        where_or_group = ""
    
    sql = f"SELECT {select_clause} {from_clause} {join_clause} {where_or_group}".strip()
    sql = " ".join(sql.split())
    return sql

def execute_sql(sql: str, retry: bool = True) -> Tuple[bool, str, List]:
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        result_rows = [dict(row) for row in rows]
        cur.close()
        conn.close()
        return True, "Success", result_rows
    except Exception as e:
        error_msg = str(e)
        if retry:
            fixed_sql = sql
            print(f"First attempt failed: {error_msg}. Retrying...")
            try:
                conn2 = psycopg2.connect(**DB_CONFIG)
                cur2 = conn2.cursor()
                cur2.execute(fixed_sql)
                rows2 = cur2.fetchall()
                cur2.close()
                conn2.close()
                return True, "Success after retry", [dict(row) for row in rows2]
            except Exception as e2:
                return False, f"Failed after retry: {str(e2)}", []
        else:
            return False, error_msg, []
    finally:
        if conn:
            conn.close()

def run_pipeline(question: str, decomp: Dict) -> Dict:
    sql = generate_sql(decomp)
    success, message, rows = execute_sql(sql)
    return {
        "question": question,
        "generated_sql": sql,
        "execution_success": success,
        "message": message,
        "row_count": len(rows),
        "sample_rows": rows[:5] if rows else []
    }

def main():
    with open("decompositions.json", "r", encoding="utf-8") as f:
        decompositions = json.load(f)
    
    questions = []
    with open("sql_questions_only.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row["question"].strip()
            questions.append(q)
    
    results = []
    for q in questions:
        if q not in decompositions:
            print(f"Warning: No decomposition found for '{q}'. Skipping.")
            continue
        decomp = decompositions[q]
        print(f"Processing: {q}")
        res = run_pipeline(q, decomp)
        results.append(res)
        print(f"  SQL: {res['generated_sql']}")
        print(f"  Status: {res['execution_success']} - {res['message']}")
        print(f"  Rows returned: {res['row_count']}\n")
    
    with open("evaluation_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Generated SQL", "Executed Successfully", "Message", "Row Count"])
        for r in results:
            writer.writerow([r["question"], r["generated_sql"], r["execution_success"], r["message"], r["row_count"]])
    
    print("Done. Evaluation report saved as 'evaluation_report.csv'")

if __name__ == "__main__":
    main()