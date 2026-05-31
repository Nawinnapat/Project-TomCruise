# Project TomCruise DBD Extractor

Production-oriented extractor for public company information from DBD DataWarehouse only.

## Source Policy

- Trusted source: `https://datawarehouse.dbd.go.th`
- No Google, social networks, company websites, third-party enrichment, or inferred values.
- Missing data is exported as `NULL`/empty values, never guessed.

## Usage

```powershell
python -m src.main --input companies.csv --years 2568,2567,2566
python -m src.main --name "ซีพี ออลล์" --years 2568,2567
python -m src.main --juristic-id 0107542000011 --years 2568
```

Input files should include `company_name` and/or `juristic_id` columns.

## Outputs

Generated under `output/` by default:

- `results.csv`
- `results.xlsx`
- `results.json`
- `errors.csv`
- `processing_report.json`

## Runtime Notes

- The extractor is API-first and targets observed DataWarehouse JSON/XHR endpoints.
- Direct requests may require a valid `DBD_COOKIE` if DBD WAF/Incapsula blocks the session.
- Cache TTL defaults to 24 hours.
- Logs are written to `logs/error.log`, `logs/validation.log`, and `logs/processing.log`.

