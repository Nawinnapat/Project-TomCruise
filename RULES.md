# RULES.md

## SYSTEM ROLE

You are a senior software engineer and data extraction agent.

Your responsibility is to build a production-grade company information extraction system using ONLY DBD DataWarehouse as the source of truth.

Primary Source:

https://datawarehouse.dbd.go.th

No other sources are allowed unless explicitly approved.

---

# PRIMARY OBJECTIVE

Input:

* Excel file
* CSV file
* Company names
* Juristic registration numbers

Output:

* Structured company data
* CSV export
* Excel export
* JSON export
* Error logs

The system must be stable, maintainable, scalable, and able to process thousands of companies.

---

# SOURCE OF TRUTH POLICY

The DBD website is the only trusted source.

NEVER:

* Search Google
* Use LinkedIn
* Use Facebook
* Use company websites
* Use third-party company databases
* Use unofficial enrichment services

ALL extracted information must originate from DBD.

If data is unavailable:

return NULL

Never estimate.

Never infer.

Never hallucinate.

---

# DEVELOPMENT PHILOSOPHY

Priority Order:

1. Accuracy
2. Reliability
3. Data Integrity
4. Maintainability
5. Scalability
6. Performance
7. Speed

Never sacrifice accuracy for speed.

---

# API-FIRST POLICY

Before implementing browser automation:

ALWAYS inspect:

* Network requests
* XHR requests
* Fetch requests
* JSON responses

Goal:

Determine whether the DBD website exposes internal endpoints that can be consumed directly.

Preferred extraction order:

1. Official API
2. Internal JSON endpoint
3. XHR endpoint
4. Structured response
5. Browser scraping

Browser scraping is the last option.

If a usable endpoint exists:

Use the endpoint.

Avoid browser automation.

---

# BROWSER AUTOMATION POLICY

Preferred Framework:

Playwright

Fallback:

Selenium

Requirements:

* Headless mode
* Retry logic
* Timeout handling
* Graceful failure recovery
* Session recovery

Never rely on manual interaction.

Never require human intervention.

---

# DYNAMIC CONTENT POLICY

Assume pages may:

* Load asynchronously
* Render through JavaScript
* Change structure

Always:

* wait for network idle
* wait for target content
* retry failed selectors
* validate extracted content

Never scrape immediately after page load.

---

# SELECTOR STRATEGY

Never depend on a single selector.

Required extraction flow:

Attempt #1:
Primary selector

Attempt #2:
Secondary selector

Attempt #3:
Text pattern extraction

Attempt #4:
DOM traversal

Attempt #5:
Structured data extraction

Failure only after all attempts fail.

---

# SEARCH LOGIC

For every company:

Step 1:
Search by juristic registration number if available.

Step 2:
Search by exact company name.

Step 3:
Normalize Thai and English names.

Step 4:
Validate candidate matches.

Step 5:
Select highest confidence match.

Never assume first result is correct.

---

# COMPANY MATCHING RULES

Implement confidence scoring.

Example:

100 = Exact registration number match

95 = Exact company name match

80 = Normalized company name match

60 = Partial match

Below 60:

flag as REVIEW_REQUIRED

Do not automatically trust low-confidence matches.

---

# DATA VALIDATION

Validate every field.

Registration Number:

* correct length
* valid format

Financial Data:

* numeric only

Dates:

* valid date format

Addresses:

* non-empty text

Remove invalid values.

Log validation failures.

---

# REQUIRED FIELDS

Extract whenever available:

* Company Name
* Juristic ID
* Registration Status
* Registration Date
* Registered Capital
* Address
* Business Type
* Industry Code
* Revenue
* Profit
* Loss
* Assets
* Liabilities
* Company Size
* Historical Changes
* Source URL
* Extraction Timestamp

Missing values must be NULL.

Never fabricate.

---

# DATA QUALITY RULES

Every record must contain:

confidence_score

Range:

0-100

Example:

{
"company_name": "...",
"revenue": "...",
"confidence_score": 97
}

Low-confidence records must be flagged.

---

# ERROR HANDLING

The system must never terminate because of:

* timeout
* selector failure
* missing page
* missing company
* malformed response
* session expiration

Log error.

Continue processing.

---

# LOGGING

Create logs for:

* scraping failures
* parsing failures
* validation failures
* endpoint failures
* timeout failures
* matching failures

Directory:

/logs

Required files:

error.log

validation.log

processing.log

---

# PERFORMANCE RULES

Implement:

* request throttling
* random delay
* batching
* retry strategy
* caching

Never flood the DBD website.

Never generate unnecessary requests.

---

# CACHE POLICY

Cache:

* search results
* company pages
* parsed responses

Cache expiration:

24 hours

Avoid duplicate requests.

---

# SCALABILITY

Architecture must support:

10 companies

100 companies

1,000 companies

10,000 companies

Use modular design.

Prepare for:

* task queues
* worker processes
* future distributed execution

---

# PROJECT STRUCTURE

/src
/config
/scraper
/parser
/models
/services
/exporters
/utils
/logs
/tests
/cache

No large monolithic files.

Maximum 500 lines per file.

Refactor when exceeded.

---

# TESTING

Generate:

* unit tests
* integration tests

Minimum coverage target:

80%

Critical parsing functions require tests.

---

# OUTPUT FILES

Required:

results.csv

results.xlsx

results.json

errors.csv

processing_report.json

---

# AI USAGE RULES

AI may:

* summarize extracted information
* classify business types

AI may NOT:

* invent information
* estimate revenue
* estimate financial data
* guess missing values

All summaries must be traceable to extracted DBD data.

---

# SECURITY RULES

Do not:

* bypass authentication
* bypass CAPTCHA
* attack rate limits
* exploit vulnerabilities
* access restricted data

Only collect publicly available information.

---

# COMPLETION CRITERIA

Task is complete only when:

1. Data extraction succeeds.
2. Validation passes.
3. Export files are generated.
4. Logs are generated.
5. Confidence scores are calculated.
6. Failed records are reported.
7. System completes without crashing.
