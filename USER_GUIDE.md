# Project TomCruise User Guide

Project TomCruise is a DBD DataWarehouse extraction tool for collecting public Thai company information from `https://datawarehouse.dbd.go.th`. It accepts company names, juristic registration numbers, CSV files, or Excel files, then exports structured records to CSV, XLSX, and JSON.

The project is source-restricted by design: extracted data comes from DBD DataWarehouse only. Missing values are left empty or `null`; the extractor does not infer or enrich data from third-party sources.

## Contents

- [Purpose](#purpose)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Major Modules](#major-modules)
- [Environment Requirements](#environment-requirements)
- [Configuration](#configuration)
- [Authentication Flow](#authentication-flow)
- [API Client Flow](#api-client-flow)
- [Extraction Flow](#extraction-flow)
- [Company Search](#company-search)
- [Encrypted Envelope Decryption](#encrypted-envelope-decryption)
- [Financial Extraction](#financial-extraction)
- [Exports](#exports)
- [Logging and Reporting](#logging-and-reporting)
- [Running the Extractor](#running-the-extractor)
- [Input File Formats](#input-file-formats)
- [Expected Outputs](#expected-outputs)
- [Testing and Coverage](#testing-and-coverage)
- [Common Failures and Troubleshooting](#common-failures-and-troubleshooting)
- [Deployment Notes](#deployment-notes)
- [Maintenance Notes](#maintenance-notes)

## Purpose

The extractor automates collection of DBD company data into a normalized `CompanyRecord`.

The output model includes:

- Company name
- Juristic registration number
- Registration status
- Registration date
- Registered capital
- Address
- Business type
- Industry code
- Revenue
- Profit
- Loss
- Assets
- Liabilities
- Company size
- Historical changes
- Source URL
- Extraction timestamp
- Confidence score
- Review flag
- Raw DBD payloads
- Errors

The tool is intended for repeatable batch extraction, not manual browser scraping.

## Architecture

The application is organized around a CLI entrypoint, a service layer, a DBD API client, parsers, exporters, and utilities.

```text
CLI
  src/main.py
    |
    v
ExtractionService
  services/extraction_service.py
    |
    v
DbdDataWarehouseClient
  scraper/dbd_client.py
    |
    v
DbdHttpClient
  scraper/http_client.py
    |
    +--> PlaywrightDbdAuthenticator
    |      scraper/dbd_auth.py
    |
    +--> decrypt_envelope()
           scraper/dbd_crypto.py
```

High-level responsibilities:

- `src/main.py` parses CLI arguments and writes exports.
- `services/extraction_service.py` orchestrates search, profile, history, and financial extraction.
- `scraper/dbd_client.py` defines DBD endpoint methods.
- `scraper/http_client.py` handles authentication, retries, caching, encrypted response decryption, and HTTP transport.
- `scraper/dbd_auth.py` obtains anonymous DBD JWTs through Playwright.
- `scraper/dbd_crypto.py` decrypts encrypted DBD API envelopes.
- `parser/dbd_parser.py` converts raw DBD JSON into `CompanyRecord`.
- `exporters/` writes CSV, XLSX, JSON, errors, and processing reports.
- `utils/` contains validation, Thai name normalization, caching, and logging helpers.

## Folder Structure

Current repository layout:

```text
Project TomCruise/
  config/
    settings.py
  exporters/
    csv_exporter.py
    excel_exporter.py
    json_exporter.py
    report_exporter.py
  models/
    company.py
  parser/
    dbd_parser.py
  scraper/
    dbd_auth.py
    dbd_client.py
    dbd_crypto.py
    http_client.py
    node_fetch.mjs
    browser_client.py
  services/
    extraction_service.py
    matching.py
  src/
    main.py
  tests/
    test_dbd_auth.py
    test_dbd_client.py
    test_dbd_crypto.py
    test_exporters.py
    test_extraction_service.py
    test_http_client.py
    test_matching.py
    test_parser.py
    test_validation.py
  utils/
    cache.py
    logging.py
    thai.py
    validation.py
  README.md
  RULES.md
  pyproject.toml
```

Generated runtime folders:

```text
cache/
logs/
output/
.pytest_cache/
__pycache__/
```

These generated folders are not source code and are usually ignored in Git.

## Major Modules

### `src/main.py`

The CLI entrypoint. It:

1. Initializes logging.
2. Parses arguments.
3. Loads input records from CLI, CSV, or XLSX.
4. Calls `ExtractionService.extract_many`.
5. Writes all output files.

Supported CLI options:

```text
--input       CSV/XLSX input file with company_name and/or juristic_id columns
--name        single company name
--juristic-id single 13-digit juristic registration number
--years       comma-separated fiscal years, for example 2568,2567
--output-dir  output directory, defaults to output/
```

### `config/settings.py`

Defines runtime settings from environment variables. Defaults are embedded in the `Settings` dataclass.

Important variables:

```text
DBD_BASE_URL                       default: https://datawarehouse.dbd.go.th
DBD_REQUEST_TIMEOUT_SECONDS        default: 20
DBD_MAX_RETRIES                    default: 3
DBD_MIN_DELAY_SECONDS              default: 0.8
DBD_MAX_DELAY_SECONDS              default: 2.2
DBD_CACHE_TTL_SECONDS              default: 86400
DBD_USER_AGENT                     default: Chrome-like desktop UA
DBD_COOKIE                         default: empty
DBD_PLAYWRIGHT_HEADLESS            default: true
DBD_PLAYWRIGHT_TIMEOUT_SECONDS     default: 45
DBD_CACHE_DIR                      default: cache
DBD_LOGS_DIR                       default: logs
DBD_OUTPUT_DIR                     default: output
```

### `models/company.py`

Defines the data structures:

- `CompanyInput`: input company name and/or juristic ID.
- `CompanyRecord`: normalized extraction result.

`CompanyRecord.to_dict()` is used by all exporters.

### `services/extraction_service.py`

The main orchestration layer.

It supports:

- Batch extraction with `extract_many`.
- Single-record extraction with `extract_one`.
- CSV and XLSX input loading.
- Juristic ID validation.
- Search-based type resolution.
- Profile retrieval.
- Historical change retrieval.
- Financial statement retrieval.
- Error capture per company so a batch can continue after failures.

When a company fails, the service returns a `CompanyRecord` with `errors` populated instead of crashing the whole run.

### `services/matching.py`

Ranks search candidates.

Confidence scores:

```text
100 exact valid juristic ID match
95  exact company name match
80  normalized company name match
60  partial normalized name match
0   no match
```

Records with confidence below `60` are marked for review.

### `utils/thai.py`

Normalizes company names for matching. It:

- Applies Unicode NFKC normalization.
- Uses casefolding.
- Removes common Thai legal terms such as `บริษัท`, `จำกัด`, `บจก.`, `บมจ.`, and `หจก.`.
- Removes punctuation and collapses whitespace.

### `utils/validation.py`

Provides:

- `valid_juristic_id`: requires exactly 13 digits.
- `parse_number`: parses numbers with commas and returns `None` for empty, `-`, `NULL`, or invalid values.
- `clean_text`: trims text and converts empty strings to `None`.

### `utils/cache.py`

Provides a JSON file cache:

- Cache keys are SHA-256 hashes.
- Cached files contain `created_at` and `data`.
- Expired cache entries are ignored.
- Default TTL is 24 hours.

### `utils/logging.py`

Configures three loggers:

```text
logs/processing.log
logs/validation.log
logs/error.log
```

### `scraper/browser_client.py`

This file contains a placeholder `PlaywrightFallbackClient`. It is not used for extraction today. The implemented browser use is authentication-only in `scraper/dbd_auth.py`, not DOM scraping.

## Environment Requirements

Project dependencies are declared in `pyproject.toml`:

```text
Python >= 3.11
requests >= 2.32.0
openpyxl >= 3.1.0
cryptography >= 42.0.0
playwright >= 1.60.0
```

Development dependencies:

```text
pytest >= 8.0.0
pytest-cov >= 7.0.0
```

The extractor also uses Node.js for the `scraper/node_fetch.mjs` fallback transport.

Install Python dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Install Playwright browser binaries:

```powershell
python -m playwright install chromium
```

If you want browser binaries stored inside this project instead of a user-level Playwright cache:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
python -m playwright install chromium
```

## Configuration

Environment variables can override defaults.

Example:

```powershell
$env:DBD_MIN_DELAY_SECONDS="0.8"
$env:DBD_MAX_DELAY_SECONDS="2.2"
$env:DBD_MAX_RETRIES="3"
$env:DBD_OUTPUT_DIR="output"
$env:DBD_CACHE_DIR="cache"
$env:DBD_LOGS_DIR="logs"
```

For troubleshooting Playwright, headed mode can be enabled:

```powershell
$env:DBD_PLAYWRIGHT_HEADLESS="false"
```

This project also supports `DBD_COOKIE`, but the current production-stable path obtains cookies through Playwright and passes them to the HTTP client automatically.

## Authentication Flow

DBD DataWarehouse uses an anonymous JWT for API access. Raw HTTP token acquisition can be blocked by Imperva WAF, so the project uses Playwright for token bootstrap.

Implemented flow:

1. `DbdHttpClient` needs an access token.
2. It calls `PlaywrightDbdAuthenticator.acquire()`.
3. Playwright launches Chromium.
4. Chromium opens `https://datawarehouse.dbd.go.th`.
5. The page waits briefly for browser-side DBD/Imperva state.
6. Inside the browser page context, JavaScript calls:

   ```javascript
   fetch('/api/refresh', {
     method: 'POST',
     credentials: 'include',
     headers: {
       'Accept': 'application/json, text/plain, */*',
       'Content-Type': 'application/json'
     }
   })
   ```

7. The response must contain `idToken`.
8. The JWT payload is decoded.
9. The JWT expiration time is read from `exp`.
10. Browser cookies are collected from the Playwright context.
11. `DbdHttpClient` stores:
    - JWT in `self.access_token`
    - expiration in `self.access_token_exp`
    - cookies in the `requests.Session`
    - `Authorization: Bearer <token>` header

Token refresh behavior:

- Before each uncached API request, `_ensure_access_token()` checks whether a token exists and is not close to expiry.
- If no valid token exists, it obtains a new token through Playwright.
- If an API request returns HTTP 401, the client refreshes through Playwright and retries that request once.

Logging:

- Token acquisition start and success are logged to `processing.log`.
- Playwright auth failures and WAF-like refresh failures are logged to `error.log`.

The token value itself is not logged.

## API Client Flow

`scraper/dbd_client.py` exposes endpoint-level methods.

Company search:

```text
POST /api/v1/company-profiles/infos
```

Company profile:

```text
GET /api/v1/company-profiles/info/{juristic_type}/{juristic_id}
```

History endpoints:

```text
GET /api/v1/company-profiles/names/{juristic_type}/{juristic_id}
GET /api/v1/company-profiles/capitals/{juristic_type}/{juristic_id}
GET /api/v1/company-profiles/mergers/{juristic_type}/{juristic_id}
```

Financial endpoints:

```text
GET /api/v1/fin/basics/{juristic_type}/{juristic_id}?fiscalYear={year}
GET /api/v1/fin/submit/{juristic_type}/{juristic_id}?fiscalYear={year}
GET /api/v1/fin/balancesheet/year/{juristic_type}/{juristic_id}?fiscalYear={year}
GET /api/v1/fin/profitloss/year/{juristic_type}/{juristic_id}?fiscalYear={year}
GET /api/v1/fin/ratio/year/{juristic_type}/{juristic_id}?fiscalYear={year}
```

`DbdHttpClient` performs:

1. Cache lookup.
2. Token validation or acquisition.
3. HTTP request through `requests`.
4. Node fetch fallback when needed.
5. HTTP 401 refresh and retry.
6. Encrypted envelope detection and decryption.
7. Cache write.

## Extraction Flow

For each input company:

1. Read input from CLI, CSV, or XLSX.
2. If `juristic_id` is present:
   - Validate whether it is a 13-digit ID.
   - Search DBD by ID to resolve `juristic_type`.
3. If only a company name is present:
   - Search DBD by name.
   - Parse candidates.
   - Score candidates.
   - Choose the highest-confidence match.
4. If no match exists:
   - Return a record with `errors=["NOT_FOUND"]`.
5. If the juristic ID is invalid:
   - Return a record with `errors=["INVALID_JURISTIC_ID"]`.
6. Fetch the company profile.
7. Fetch history:
   - name changes
   - capital changes
   - mergers
8. Determine financial years:
   - Use CLI `--years` if supplied.
   - Otherwise use `fiscalYear` or `fiscalYearRpt` from the profile.
9. Fetch financial statements for up to five years.
10. Parse the normalized `CompanyRecord`.
11. Set confidence score, review flag, and source URL.
12. Continue to the next input, even if one company fails.

## Company Search

Search is implemented by `DbdDataWarehouseClient.search_companies`.

Request body:

```json
{
  "keyword": "0107544000108",
  "type": "",
  "sortBy": "jpName",
  "currentPage": 1
}
```

If `page_size` is not the default of `10`, `itemsPerPage` is included.

Search result parsing handles payload keys such as:

```text
contents
data
items
results
ResultList
resultList
```

Each candidate is normalized into:

```json
{
  "juristic_id": "...",
  "juristic_type": "...",
  "company_name": "...",
  "registration_status": "...",
  "industry_code": "...",
  "raw": {}
}
```

## Encrypted Envelope Decryption

Some DBD API responses are encrypted envelopes. The client detects an encrypted envelope when a dictionary contains:

```text
kid
salt
iv
ct
```

Decryption is implemented in `scraper/dbd_crypto.py`.

Workflow:

1. Decode the JWT payload.
2. Read `encKey` from the JWT.
3. Decode envelope fields from base64url:
   - `salt`
   - `iv`
   - `ct`
4. Build HKDF info from the API path:

   ```text
   bdw|v{kid}|{api_path}
   ```

5. Derive a 32-byte AES key:

   ```text
   HKDF-SHA256(
     ikm = JWT encKey,
     salt = envelope salt,
     info = bdw|v{kid}|{api_path}
   )
   ```

6. Decrypt ciphertext with AES-GCM:

   ```text
   nonce = envelope iv
   data = envelope ct
   associated_data = info
   ```

7. Decompress plaintext using:
   - gzip
   - zlib
   - raw zlib
   - or no decompression if all attempts fail
8. Parse JSON.

The decrypted payload is passed to parsers and cached.

## Financial Extraction

Financial extraction is implemented by `DbdDataWarehouseClient.financial_statements` and `ExtractionService._financials`.

For each fiscal year, the client requests:

- basics
- submit history
- balance sheet
- profit/loss
- ratios

The result is stored under the fiscal year:

```json
{
  "2568": {
    "basics": {},
    "submit": [],
    "balancesheet": {},
    "profitloss": {},
    "ratio": {}
  }
}
```

The parser merges the latest financial data from:

```text
basics
balancesheet
profitloss
ratio
```

If sections contain `finStatementDailyDtos`, the parser prefers the row matching the requested fiscal year.

Mapped financial fields include:

```text
revenue      from revenue, revenueA, totalIncome, totalRevenue, TotalRevenue
profit       from profitloss, profitlossA, netProfit, NetProfit, profit
loss         from loss, Loss
assets       from assets, assetsA, totalAsset, TotalAsset
liabilities  from liabilities, liabilitiesA, totalLiability, totalLiabilities, TotalLiabilities
```

## Exports

The CLI always writes five files:

```text
results.csv
results.xlsx
results.json
errors.csv
processing_report.json
```

Default location:

```text
output/
```

Custom location:

```powershell
python -m src.main --juristic-id 0107544000108 --output-dir output\ptt
```

### CSV Export

`exporters/csv_exporter.py` writes:

- `results.csv`: all records and all `CompanyRecord` fields.
- `errors.csv`: only records with `errors` or `review_required`.

CSV files are written as UTF-8 with BOM (`utf-8-sig`) for better spreadsheet compatibility.

### XLSX Export

`exporters/excel_exporter.py` writes `results.xlsx`.

The workbook contains one sheet named:

```text
results
```

Dictionary and list values are converted to strings before writing cells.

### JSON Export

`exporters/json_exporter.py` writes `results.json`.

JSON is written with:

```text
ensure_ascii=False
indent=2
```

This preserves Thai text.

### Processing Report

`exporters/report_exporter.py` writes:

```json
{
  "generated_at": "2026-06-01T00:00:00Z",
  "total": 1,
  "success": 1,
  "failed": 0,
  "review_required": 0
}
```

## Logging and Reporting

Logs are created under `logs/`:

```text
logs/processing.log
logs/validation.log
logs/error.log
```

Examples of logged events:

- Token acquisition start.
- Token acquisition success.
- Token refresh.
- Cache hits.
- Successful requests.
- Request failures.
- DBD WAF or refresh failures.
- Endpoint failures for history or financial sections.
- Invalid numeric values.
- Per-company extraction failures.

Batch reporting files:

```text
errors.csv
processing_report.json
```

`errors.csv` includes:

```text
company_name,juristic_id,errors,confidence_score
```

## Running the Extractor

Run all commands from the repository root:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"
```

If using a local project dependency cache:

```powershell
$env:PYTHONPATH="cache\python-packages;."
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
```

### Single Company Extraction by Name

```powershell
python -m src.main --name "PTT PUBLIC COMPANY LIMITED" --years 2568 --output-dir output\single_name
```

Expected files:

```text
output/single_name/results.csv
output/single_name/results.xlsx
output/single_name/results.json
output/single_name/errors.csv
output/single_name/processing_report.json
```

If no match is found, `results.*` will contain an error record and `errors.csv` will include `NOT_FOUND`.

### Extraction by Juristic ID

```powershell
python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\ptt
```

Expected `processing_report.json` shape:

```json
{
  "generated_at": "...",
  "total": 1,
  "success": 1,
  "failed": 0,
  "review_required": 0
}
```

Expected `results.json` shape:

```json
[
  {
    "company_name": "...",
    "juristic_id": "0107544000108",
    "registration_status": "...",
    "registration_date": "...",
    "registered_capital": 0.0,
    "address": "...",
    "business_type": "...",
    "industry_code": "...",
    "revenue": 0.0,
    "profit": 0.0,
    "loss": null,
    "assets": 0.0,
    "liabilities": 0.0,
    "company_size": "...",
    "historical_changes": [],
    "source_url": "https://datawarehouse.dbd.go.th/company/profile/...",
    "extraction_timestamp": "...",
    "confidence_score": 100,
    "review_required": false,
    "raw": {},
    "errors": []
  }
]
```

Values depend on the current DBD response.

### Batch Extraction from CSV

Example input file:

```csv
company_name,juristic_id
,0107544000108
PTT PUBLIC COMPANY LIMITED,
```

Run:

```powershell
python -m src.main --input companies.csv --years 2568,2567 --output-dir output\batch_csv
```

The extractor reads `company_name` and/or `juristic_id`.

### Batch Extraction from XLSX

The first worksheet is read. The first row must contain headers.

Supported headers:

```text
company_name
name
juristic_id
```

Run:

```powershell
python -m src.main --input companies.xlsx --years 2568 --output-dir output\batch_xlsx
```

### Automatic Fiscal Year Selection

If `--years` is omitted, the extractor uses `fiscalYear` or `fiscalYearRpt` from the profile payload.

```powershell
python -m src.main --juristic-id 0107544000108 --output-dir output\auto_year
```

## Input File Formats

### CSV

CSV is read with `utf-8-sig`.

Accepted columns:

```text
company_name
name
juristic_id
```

Example:

```csv
company_name,juristic_id
,0107544000108
Example Company,
```

### XLSX

XLSX is read with `openpyxl` in read-only mode.

The first row is used as headers. Each subsequent row becomes one `CompanyInput`.

## Expected Outputs

Example output folder:

```text
output/ptt/
  results.csv
  results.xlsx
  results.json
  errors.csv
  processing_report.json
```

Example successful processing report:

```json
{
  "generated_at": "2026-06-01T00:00:00Z",
  "total": 20,
  "success": 20,
  "failed": 0,
  "review_required": 0
}
```

Example error report row:

```csv
company_name,juristic_id,errors,confidence_score
Unknown Co,,NOT_FOUND,0
```

## Testing and Coverage

Run the full test suite:

```powershell
python -m pytest
```

Run with coverage:

```powershell
python -m pytest --cov=config --cov=exporters --cov=models --cov=parser --cov=scraper --cov=services --cov=src --cov=utils --cov-report=term
```

The tests cover:

- JWT token acquisition helpers
- Token refresh flow
- Encrypted envelope decryption
- DBD endpoint method wiring
- Profile extraction
- Financial extraction
- Thai name normalization
- Matching and confidence scoring
- CSV/XLSX/JSON exporters
- Validation utilities

At the time this guide was created, the suite contained tests under `tests/` for these modules. Coverage percentage depends on the exact command and environment.

## Common Failures and Troubleshooting

### Playwright is not installed

Error:

```text
Playwright is required for stable DBD authentication
```

Fix:

```powershell
python -m pip install playwright
python -m playwright install chromium
```

### Browser binary not found

If Playwright cannot find Chromium, install it:

```powershell
python -m playwright install chromium
```

For local workspace browser cache:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
python -m playwright install chromium
```

### DBD Playwright refresh failed with HTTP 403

This means DBD or Imperva returned a blocked response while acquiring the anonymous JWT.

Try:

```powershell
$env:DBD_PLAYWRIGHT_HEADLESS="false"
python -m src.main --juristic-id 0107544000108 --years 2568
```

Also consider increasing timeout:

```powershell
$env:DBD_PLAYWRIGHT_TIMEOUT_SECONDS="60"
```

### HTTP 401 from API

The client is designed to refresh the JWT through Playwright and retry once. If it still fails:

- Check `logs/error.log`.
- Confirm Playwright can launch Chromium.
- Confirm DBD is reachable.
- Try headed mode with `DBD_PLAYWRIGHT_HEADLESS=false`.

### DBD endpoint failed after retries

The HTTP client retries according to `DBD_MAX_RETRIES`.

Possible causes:

- DBD is temporarily unavailable.
- WAF is blocking the current environment.
- Network timeout.
- Authentication failed.
- Endpoint response changed.

Check:

```text
logs/error.log
logs/processing.log
```

### Search returns no candidates

For company-name extraction, search results are matched by normalized name. If DBD returns no candidates, the record is returned with:

```text
NOT_FOUND
```

For highest reliability, provide `juristic_id` when available.

### Invalid juristic ID

Juristic IDs must be exactly 13 digits.

Invalid values produce:

```text
INVALID_JURISTIC_ID
```

### Missing financial values

The extractor does not invent missing data. If DBD omits a field, the exported value remains empty or `null`.

### Garbled Thai text in terminal

On Windows, set UTF-8 output:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

CSV output uses `utf-8-sig`, which is usually easier for spreadsheet applications.

### Generated folders appear in Git

Generated runtime folders should normally be ignored:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
cache/
output/
logs/
```

## Deployment Notes

Production deployment should include:

- Python 3.11 or newer.
- Project Python dependencies.
- Node.js for `scraper/node_fetch.mjs` fallback transport.
- Playwright Chromium installed.
- Writable directories for:
  - cache
  - logs
  - output

Recommended environment variables:

```powershell
$env:DBD_CACHE_DIR="cache"
$env:DBD_LOGS_DIR="logs"
$env:DBD_OUTPUT_DIR="output"
$env:DBD_MAX_RETRIES="3"
$env:DBD_MIN_DELAY_SECONDS="0.8"
$env:DBD_MAX_DELAY_SECONDS="2.2"
$env:DBD_PLAYWRIGHT_HEADLESS="true"
```

For unattended runs, ensure the service account can launch Playwright Chromium in headless mode.

For servers with strict sandboxing, verify Playwright can start before running large batches:

```powershell
python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\smoke
```

## Maintenance Notes

### Keep authentication isolated

Authentication is intentionally isolated in `scraper/dbd_auth.py`. Extraction logic should not depend on browser automation directly.

If DBD changes its frontend token flow, inspect and update only the authentication boundary when possible.

### Keep API extraction separate from parsing

Endpoint methods belong in `scraper/dbd_client.py`.

Response normalization belongs in `parser/dbd_parser.py`.

Avoid mixing endpoint transport logic into parsers.

### Update decryption carefully

Encrypted envelope decryption depends on:

- JWT `encKey`
- envelope `kid`
- API path
- `salt`
- `iv`
- `ct`
- HKDF-SHA256
- AES-GCM

If DBD changes envelope structure, add tests in `tests/test_dbd_crypto.py` before changing production code.

### Add tests for endpoint changes

When adding or changing endpoints:

1. Add method-level tests in `tests/test_dbd_client.py`.
2. Add parser tests in `tests/test_parser.py`.
3. Add service-level tests when orchestration changes.

### Preserve source-of-truth rules

Do not add third-party enrichment unless explicitly approved. All company data should remain traceable to DBD responses.

### Use cache intentionally

The cache reduces duplicate requests. During live validation, use a separate cache directory or expire cache entries if you need to force fresh API calls.

Example:

```powershell
$env:DBD_CACHE_DIR="cache\fresh_run"
```

### Handle large batches conservatively

Use throttling and retries:

```powershell
$env:DBD_MIN_DELAY_SECONDS="0.8"
$env:DBD_MAX_DELAY_SECONDS="2.2"
$env:DBD_MAX_RETRIES="3"
```

Avoid unnecessarily low delays in production. The DBD website should not be flooded.

## Quick Reference

Single juristic ID:

```powershell
python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\ptt
```

Single name:

```powershell
python -m src.main --name "PTT PUBLIC COMPANY LIMITED" --years 2568 --output-dir output\single_name
```

Batch CSV:

```powershell
python -m src.main --input companies.csv --years 2568,2567 --output-dir output\batch
```

Batch XLSX:

```powershell
python -m src.main --input companies.xlsx --years 2568 --output-dir output\batch_xlsx
```

Tests:

```powershell
python -m pytest
```

Coverage:

```powershell
python -m pytest --cov=config --cov=exporters --cov=models --cov=parser --cov=scraper --cov=services --cov=src --cov=utils --cov-report=term
```
