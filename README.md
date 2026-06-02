# Project TomCruise DBD Extractor

Project TomCruise extracts public company profile and financial information from DBD DataWarehouse.

The project has two interfaces:

- CLI commands for automation and batch jobs.
- Streamlit web UI for interactive single-company and batch extraction.

The Streamlit UI is an additional interface only. It reuses the existing extraction engine, Playwright + Google Chrome authentication, parsers, models, and exporters.

## Installation

Create and activate a virtual environment:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Google Chrome for Playwright authentication:

```powershell
playwright install chrome
```

For development and tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Run CLI

Existing CLI commands continue to work:

```powershell
python -m src.main --name "บริษัท"
python -m src.main --juristic-id 0107556000485
python -m src.main --input companies.xlsx --years 2568
```

More examples:

```powershell
python -m src.main --input companies.csv --years 2568,2567,2566
python -m src.main --name "บริษัท อิชิตัน กรุ๊ป จำกัด (มหาชน)" --years 2568
python -m src.main --juristic-id 0107556000485 --years 2568 --output-dir output\ichitan
```

## Run Web UI

Start Streamlit:

```powershell
streamlit run app.py
```

The web UI includes:

- Single Company Search by company name or juristic ID.
- Batch CSV/XLSX upload.
- Interactive result table with search, filter, sort, and pagination.
- Download buttons for XLSX, CSV, and JSON.
- System Status page.
- Log Viewer for `logs/error.log`, `logs/processing.log`, and `logs/validation.log`.

## Batch Input Format

CSV/XLSX files should include one or both columns:

```csv
company_name,juristic_id
บริษัท อิชิตัน กรุ๊ป จำกัด (มหาชน),0107556000485
,0107544000108
บริษัท ปตท. จำกัด (มหาชน),
```

Supported inputs:

- `company_name` only
- `juristic_id` only
- both `company_name` and `juristic_id`

## Outputs

The CLI writes files to `output/` by default:

- `results.csv`
- `results.xlsx`
- `results.json`
- `errors.csv`
- `processing_report.json`

The Streamlit UI writes generated downloads under:

```text
output/streamlit/
```

## DBD Authentication

DBD authentication uses Playwright with real Google Chrome:

- `channel="chrome"`
- `headless=False`
- locale `th-TH`
- timezone `Asia/Bangkok`
- persistent Chrome profile in `cache/dbd-chrome-profile`

This avoids the `HeadlessChrome` client hints that trigger Imperva WAF blocks on `/api/refresh`.

## Logs

Logs are written to:

```text
logs/processing.log
logs/error.log
logs/validation.log
```

The web UI Log Viewer can display the latest entries from each log file.

## Cache

API responses are cached under `cache/` by default. Cache TTL defaults to 24 hours.

Relevant environment variables:

```powershell
$env:DBD_CACHE_DIR="cache"
$env:DBD_OUTPUT_DIR="output"
$env:DBD_LOGS_DIR="logs"
$env:DBD_PLAYWRIGHT_CHANNEL="chrome"
$env:DBD_PLAYWRIGHT_HEADLESS="false"
```
