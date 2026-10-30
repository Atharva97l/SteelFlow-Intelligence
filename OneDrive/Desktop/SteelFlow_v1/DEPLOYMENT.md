# Deployment

Local run:

```text
pip install -r requirements.txt
streamlit run app.py
```

Container run:

```text
docker build -t steelflow-ml .
docker run --rm -p 8501:8501 steelflow-ml
```

Validate model artifacts before deployment:

```text
python scripts/health_check.py
```

The UI exposes late-delivery, freight-cost, demand (7/14/30-day), credit-default, inventory-stockout, supplier-late-receipt, and customer-churn predictions.
