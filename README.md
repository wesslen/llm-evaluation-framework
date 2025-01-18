# LLM Evaluation Framework

A comprehensive framework for evaluating Large Language Models (LLMs) through automated testing and result tracking.

## Repository Structure
```
llm-evaluation-framework/
├── .github/
│   └── workflows/
│       └── run_tests.yml
├── database/
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── init_db.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_summarization.py
│   ├── test_reasoning.py
│   ├── test_mathematics.py
│   ├── test_code_generation.py
│   └── test_few_shot.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── llm_client.py
│   └── metrics.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── datasette.yaml
```

## Database Versioning

The framework maintains a SQLite database (`database/llm_evaluation.db`) that stores all test results. This database is versioned in Git to maintain historical test results across runs. Each time the GitHub Actions workflow runs:

1. The existing database is fetched from the repository
2. New test results are appended to the database
3. The updated database is automatically committed and pushed back to the repository

Note: While the `.gitignore` file excludes most `.db` files, the main evaluation database is specifically tracked using a negation rule (`!database/llm_evaluation.db`).

## Local Development with Datasette

### Starting the Datasette Server

Run the following command from the project root:

```bash
datasette serve database/llm_evaluation.db \
  --metadata datasette.yaml \
  --reload \
  --open
```

### Available Endpoints

- Web Interface: http://localhost:8001
- JSON API: http://localhost:8001/llm_evaluation.json
- Table-specific JSON: http://localhost:8001/llm_evaluation/[table_name].json

### Example Queries

Visit http://localhost:8001/llm_evaluation to run SQL queries like:

```sql
-- Get recent test results with model info
SELECT 
    tr.created_at,
    mr.model_name,
    mr.model_version,
    tc.test_name,
    tr.pass_fail
FROM test_results tr
JOIN evaluation_runs er ON tr.run_id = er.run_id
JOIN model_registry mr ON er.model_id = mr.model_id
JOIN test_cases tc ON tr.test_id = tc.test_id
ORDER BY tr.created_at DESC
LIMIT 10;

-- Get model performance summary
SELECT 
    mr.model_name,
    mr.model_version,
    COUNT(*) as total_tests,
    SUM(CASE WHEN tr.pass_fail THEN 1 ELSE 0 END) as passed_tests,
    ROUND(AVG(CASE WHEN tr.pass_fail THEN 1 ELSE 0 END) * 100, 2) as pass_rate
FROM test_results tr
JOIN evaluation_runs er ON tr.run_id = er.run_id
JOIN model_registry mr ON er.model_id = mr.model_id
GROUP BY mr.model_id, mr.model_name, mr.model_version
ORDER BY pass_rate DESC;
```

### Development Tips

1. The `--reload` flag automatically refreshes when database changes
2. Use the built-in SQL editor at `/llm_evaluation/-/queryplan`
3. Export results as CSV, JSON, or other formats
4. Use `?_sort=column` in URLs to sort by specific columns
5. Append `.json` to any table URL to get JSON output

## Development Requirements

### Environment Variables
```
API_BASE_URL=
API_KEY=
MODEL_NAME=
DATABASE_URL=sqlite:///database/llm_evaluation.db
```

### Setup Requirements
- Python 3.9+
- Virtual environment
- Pre-commit hooks
- SQLite3

### Installation
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## Running Tests

1. Set up your environment variables in `.env`
2. Initialize the database:
```bash
python database/init_db.py
```
3. Run the tests:
```bash
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.