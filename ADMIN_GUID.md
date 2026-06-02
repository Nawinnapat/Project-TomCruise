# วิธีรัน Project TomCruise

คู่มือนี้อธิบายวิธีรัน Project TomCruise ผ่าน PowerShell แบบละเอียด

## เข้าโฟลเดอร์โปรเจกต์

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"
```

ถ้าใช้ dependency/browser cache ที่ติดตั้งไว้ในโปรเจกต์ ให้ตั้ง environment variables ก่อนรัน:

```powershell
$env:PYTHONPATH="cache\python-packages;."
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
$env:PYTHONIOENCODING="utf-8"
```

## ติดตั้งของที่จำเป็น

ถ้ายังไม่เคยติดตั้ง dependency:

```powershell
python -m pip install -e ".[dev]"
```

ติดตั้ง Chromium สำหรับ Playwright:

```powershell
python -m playwright install chromium
```

ถ้าอยากให้ Chromium อยู่ในโฟลเดอร์โปรเจกต์:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
python -m playwright install chromium
```

## รันบริษัทเดียวด้วยเลขนิติบุคคล

ตัวอย่าง PTT:

```powershell
python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\ptt
```

หลังรันเสร็จ ดูผลที่:

```text
output\ptt\results.csv
output\ptt\results.xlsx
output\ptt\results.json
output\ptt\errors.csv
output\ptt\processing_report.json
```

## รันบริษัทเดียวด้วยชื่อ

```powershell
python -m src.main --name "PTT PUBLIC COMPANY LIMITED" --years 2568 --output-dir output\single_name
```

หมายเหตุ: ถ้ามีเลขนิติบุคคล แนะนำใช้ `--juristic-id` เพราะแม่นกว่า

## รันโดยไม่ระบุปี

ระบบจะใช้ปีจาก profile ของ DBD เอง:

```powershell
python -m src.main --juristic-id 0107544000108 --output-dir output\auto_year
```

## วิธีเปิดโปรแกรม Web UI

ใช้คำสั่งนี้เวลาอยากเปิดหน้าจอโปรแกรมแบบเว็บ:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"

.\.venv\Scripts\Activate.ps1

streamlit run app.py
```

ถ้า PowerShell ไม่ยอม activate ให้รันอันนี้ก่อน:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

พอรันแล้ว จะมีลิงก์ประมาณนี้ขึ้นมา:

```text
Local URL: http://localhost:8501
```

ให้กด Ctrl + คลิกที่ลิงก์ หรือเปิด browser แล้วเข้า:

```text
http://localhost:8501
```

ถ้าอยากรันแบบไม่ activate ให้ใช้คำสั่งนี้ได้เลย:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## รันหลายปี

```powershell
python -m src.main --juristic-id 0107544000108 --years 2568,2567,2566 --output-dir output\ptt_multi_year
```

## รันจาก CSV

สร้างไฟล์ `companies.csv` แบบนี้:

```csv
company_name,juristic_id
,0107544000108
PTT PUBLIC COMPANY LIMITED,
```

แล้วรัน:

```powershell
python -m src.main --input companies.csv --years 2568 --output-dir output\batch_csv
```

## รันจาก Excel

ไฟล์ Excel ต้องมีหัวคอลัมน์แถวแรก เช่น:

```text
company_name | juristic_id
```

แล้วรัน:

```powershell
python -m src.main --input input\companies.xlsx --years 2568 --output-dir output\companies_xlsx
```

## ดูผลลัพธ์

ไฟล์หลักคือ:

```text
results.xlsx
```

ไฟล์อื่น ๆ:

```text
results.csv              ข้อมูลทั้งหมดแบบ CSV
results.json             ข้อมูลทั้งหมดแบบ JSON พร้อม raw payload
errors.csv               รายการที่ error หรือต้อง review
processing_report.json   สรุปจำนวน success/failed/review_required
```

## รันเทสต์

```powershell
python -m pytest
```

รันพร้อม coverage:

```powershell
python -m pytest --cov=config --cov=exporters --cov=models --cov=parser --cov=scraper --cov=services --cov=src --cov=utils --cov-report=term
```

## ถ้าเจอ WAF หรือ Playwright error

ลองรันแบบเปิด browser ให้เห็น:

```powershell
$env:DBD_PLAYWRIGHT_HEADLESS="false"
python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\debug
```

เพิ่ม timeout:

```powershell
$env:DBD_PLAYWRIGHT_TIMEOUT_SECONDS="60"
```

## คำสั่งแนะนำสำหรับใช้งานจริง

ใช้ชุดนี้ก่อนรัน:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"

$env:PYTHONPATH="cache\python-packages;."
$env:PLAYWRIGHT_BROWSERS_PATH="cache\ms-playwright"
$env:PYTHONIOENCODING="utf-8"

python -m src.main --juristic-id 0107544000108 --years 2568 --output-dir output\ptt
```

ถ้ารันสำเร็จ จะได้ report ประมาณนี้ใน `processing_report.json`:

```json
{
  "generated_at": "...",
  "total": 1,
  "success": 1,
  "failed": 0,
  "review_required": 0
}
```

## ต้องรันคำสั่งติดตั้งทุกครั้งไหม

ไม่ต้องรันทั้งหมดทุกครั้ง

### รันครั้งแรกครั้งเดียว

ทำตอน setup โปรเจกต์หรือเครื่องใหม่:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium

node --version
python -m pytest
```

### ครั้งต่อไปเวลาจะใช้งานจริง

รันแค่นี้พอ:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"
.\.venv\Scripts\Activate.ps1

python -m src.main --juristic-id 0107544000108 --output-dir output\auto_year
```

ถ้า PowerShell ขึ้นว่า activate ไม่ได้ ค่อยรันอันนี้อีกครั้งในหน้าต่างนั้น:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### สรุปสั้น ๆ

ทุกครั้งต้องทำ:

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"
.\.venv\Scripts\Activate.ps1
python -m src.main --juristic-id 0107544000108 --output-dir output\auto_year
```

ไม่ต้องทำทุกครั้ง:

```powershell
python -m venv .venv
python -m pip install -e ".[dev]"
python -m playwright install chromium
python -m pytest
```

ทำใหม่เฉพาะตอน:

- ย้ายเครื่อง
- ลบ `.venv`
- dependency เปลี่ยน
- Playwright browser หาย
- ต้องการรันเทสต์เช็กระบบอีกครั้ง

## สรุปคำสั่งชุดเดียวสำหรับเครื่องใหม่

```powershell
cd "C:\Project_CODE🧑‍💻\Project TomCruise"

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium

node --version
python -m pytest

python -m src.main --juristic-id 0107544000108 --output-dir output\auto_year
```
