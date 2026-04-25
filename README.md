# Manufacturing Performance Intelligence Platform

A Streamlit-based manufacturing operations dashboard focused on **OEE, downtime, production loss, quality loss, and maintenance risk**.

This version pivots the original fashion supply-chain dashboard into a core manufacturing use case suitable for plant managers, MSME owners, and manufacturing operations teams.

## What the app does

The dashboard helps answer:

- Which machine is causing the most production loss?
- Which line has the weakest OEE?
- Which shift is generating the highest defect rate?
- Which downtime reason is recurring most often?
- Which machine should maintenance inspect first?
- What is the estimated value of production loss?

## Main screens

- **Plant Manager Action Center**: deterministic recommendations based on downtime, defect rate, OEE, and maintenance risk.
- **OEE & Production Loss**: OEE trend, machine-level OEE, loss tree, and line-level production split.
- **Downtime, Quality & Maintenance Risk**: downtime Pareto, shift loss, defect heatmap, and machine risk score.
- **Filtered records**: row-level production records for validation.

## Data

The app uses:

```text
data/manufacturing_operations_data.csv
```

The sample dataset includes synthetic manufacturing records with columns such as:

```text
date, plant_id, line_id, machine_id, shift, product_id,
planned_production_time_min, runtime_min, downtime_min,
downtime_reason, target_output_qty, actual_output_qty,
good_units, rejected_units, defect_type, machine_temperature_c,
machine_vibration_mm_s, estimated_loss_value
```

For a real deployment, replace this CSV with data from MES, ERP, PLC/SCADA historians, CMMS, or shopfloor Excel logs.

## Run locally

### 1. Create virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the app

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Run with Docker

```bash
docker compose up --build
```

Open:

```text
http://localhost:8501
```

## Host on your own domain

A simple production pattern is:

```text
Domain / DNS
   ↓
Nginx reverse proxy
   ↓
Streamlit app running on port 8501
```

### Example deployment steps on a Linux VM

1. Point your domain or subdomain DNS A-record to your VM public IP.
2. Install Docker and Docker Compose.
3. Copy this project to the VM.
4. Run:

```bash
docker compose up -d --build
```

5. Configure Nginx using:

```text
nginx/manufacturing-app.conf
```

6. Replace:

```text
manufacturing.yourdomain.com
```

with your real domain.

7. Enable HTTPS using Certbot:

```bash
sudo certbot --nginx -d manufacturing.yourdomain.com
```

## Important production notes

This is still a demo-grade app. Before using it in a real plant:

- Replace synthetic data with live manufacturing data.
- Add authentication.
- Add data quality checks.
- Add audit logging.
- Validate OEE formulas with the plant operations team.
- Treat maintenance risk scoring as advisory, not as a certified predictive-maintenance model.

## Project structure

```text
.
├── app.py
├── data/
│   └── manufacturing_operations_data.csv
├── src/
│   ├── charts.py
│   ├── data.py
│   ├── insights.py
│   ├── kpis.py
│   └── styles.py
├── .streamlit/
│   └── config.toml
├── nginx/
│   └── manufacturing-app.conf
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```


## Streamlit Cloud deployment note

The app resolves image and data assets relative to `app.py`, so it can run locally and on Streamlit Community Cloud even when the repository contains nested folders. Use `app.py` as the Streamlit entrypoint.

If your repository contains this app inside a subfolder, set the Streamlit main file path to that subfolder's `app.py`, for example:

```text
imanufacturing_performance_v4/app.py
```

Do not use customer or production data in the public repository.
