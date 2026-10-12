# SteelFlow Intelligence

### End-to-End Supply Chain Analytics, Machine Learning & Decision Intelligence

**SteelFlow Intelligence** is an end-to-end supply chain intelligence platform designed around a simulated steel-pipe manufacturing company operating across Maharashtra, India.

The project combines synthetic data engineering, exploratory data analysis, SQL analytics, business intelligence, machine learning, and application development to model how procurement, production, inventory, transportation, customer demand, and financial performance interact within a manufacturing supply chain.

Rather than building isolated dashboards or training disconnected machine learning models, SteelFlow aims to develop a connected business system where operational data can be transformed into measurable insights, predictive signals, and actionable recommendations.

> **Project status:** Under development. The business scenario and intended scope are defined, while data generation, validation, analytics, machine learning, and application capabilities will be implemented and documented progressively.

---

## 1. Project Overview

Manufacturing supply chains involve interconnected decisions.

A supplier delay can interrupt raw-material availability. Material shortages can reduce production output. Production shortfalls can affect customer fulfilment, delivery commitments, revenue, and customer satisfaction. Meanwhile, changing demand, material prices, transportation costs, and seasonal conditions influence profitability.

These problems cannot always be understood by examining individual datasets in isolation.

SteelFlow models these relationships through a simulated manufacturing business with connected operational and financial records. The resulting data will support analytical investigations and predictive modelling across the supply chain lifecycle.

### Primary objectives

- Build a realistic, reproducible synthetic dataset representing a manufacturing supply chain.
- Design relational datasets with consistent identifiers, business rules, and traceable inventory movements.
- Perform end-to-end exploratory data analysis and SQL-based business analysis.
- Develop interactive Power BI dashboards for operational and management reporting.
- Train and evaluate machine learning models for forecasting, prediction, risk assessment, and anomaly detection.
- Integrate selected analytical and predictive capabilities into an application.
- Document the entire workflow so that the project can be reproduced, tested, evaluated, and extended.

### Core principle

**Every analytical result and model prediction should connect to a meaningful business question.**

The objective is not simply to achieve a high model score. It is to understand the underlying problem, construct valid features, evaluate models appropriately, explain the results, and identify how the output could support a real operational decision.

---

## 2. Business Scenario

SteelFlow represents a fictional B2B manufacturer that purchases steel and related raw materials, manufactures steel pipes, manages factory and warehouse inventory, and supplies construction companies and other business customers.

All companies, transactions, operational events, and financial records will be synthetic. The business scenario is designed to be realistic, but it does not represent a particular real-world company's confidential information.

### Simulated business structure

| Component | Planned scope |
|---|---|
| Geographic coverage | Maharashtra, India |
| Factories | 2 manufacturing facilities |
| Factory regions | East Maharashtra and West Maharashtra |
| Suppliers | Approximately 20–30 |
| B2B customers | Approximately 200–300 |
| Transportation carriers | Approximately 15 |
| Product catalogue | Approximately 40–50 individual items |
| Product classification | 4 product families |
| Warehouses | A limited number of facilities located close to the factories |
| Dataset scale | Targeting approximately 500,000–1,000,000 rows across generated datasets |
| Data characteristics | Time-dependent, relational, imperfect, and suitable for analytical modelling |

These figures describe the intended simulation, not verified generated-data counts. Final counts will be reported after the generator is implemented and validated.

### Business operations

The simulated business will cover the following interconnected activities:

1. Procurement of raw materials from suppliers.
2. Inbound deliveries to factories.
3. Raw-material inventory management.
4. Production planning and manufacturing.
5. Finished-goods inventory management.
6. Transfers between factories and nearby warehouses where applicable.
7. Customer order processing and fulfilment.
8. Outbound transportation and delivery.
9. Product quality monitoring and rejection handling.
10. Supplier, customer, carrier, and factory performance analysis.
11. Revenue, costs, margins, and profitability analysis.

Each operation should produce records that can be traced to the relevant business entities and events.

---

## 3. Supply Chain Lifecycle

The intended operational flow is:

```text
Suppliers
    |
    v
Purchase Orders
    |
    v
Inbound Deliveries
    |
    v
Raw Material Inventory
    |
    v
Production Planning
    |
    v
Manufacturing
    |
    +------> Production Quality
    |
    v
Finished Goods Inventory
    |
    v
Factory / Warehouse Allocation
    |
    v
Customer Orders
    |
    v
Shipment Planning
    |
    v
Outbound Transportation
    |
    v
Customer Delivery
    |
    v
Revenue, Cost & Service Analysis
```

Customer demand, supplier reliability, production capacity, raw-material availability, weather, transportation conditions, prices, and seasonality will influence appropriate parts of this process.

The generator must preserve the distinction between events that actually occur and the business decisions or outcomes associated with those events.

For example, a requested customer quantity is not necessarily the same as the accepted order quantity, the fulfilled quantity, or the quantity ultimately delivered.

These distinctions are essential for meaningful analytics and trustworthy ML targets.

---

## 4. Synthetic Data Engineering

Synthetic data generation is a foundational component of SteelFlow.

The objective is to generate a large, reproducible collection of related datasets that behave like a plausible manufacturing business over time, rather than a collection of independent random CSV files.

### 4.1 Data generation requirements

The generator should support:

- Configurable simulation periods and random seeds.
- Reproducible generation runs.
- Consistent primary and foreign keys.
- Explicit relationships between master and transaction tables.
- Time-dependent business behaviour.
- Seasonal demand patterns and changes in underlying trends.
- Differences between products, suppliers, customers, factories, and carriers.
- Operational constraints such as production capacity and available inventory.
- Realistic costs, selling prices, quantities, and financial calculations.
- Missing values, imperfect records, and selected data-quality problems.
- Validation reports that identify broken relationships and inconsistent business rules.

Randomness should introduce realistic variation without destroying the underlying business logic.

### 4.2 Planned dataset domains

The final table names and schemas will be documented in the data dictionary after the generator specification is frozen.

| Domain | Intended contents |
|---|---|
| Master data | Products, product families, suppliers, customers, factories, warehouses, carriers, routes, and relevant contracts |
| Procurement | Purchase orders, supplier allocations, ordered quantities, agreed prices, and inbound receipts |
| Inventory | Opening balances, receipts, material consumption, production receipts, transfers, dispatches, and adjustments |
| Production | Production plans, production runs, material requirements, actual output, capacity utilisation, and operational losses |
| Quality | Inspections, defects, rejected quantities, and relevant quality outcomes |
| Customer orders | Requested quantities, accepted quantities, order dates, commitments, fulfilment, cancellations, and backorders where applicable |
| Logistics | Shipment bookings, planned transit times, actual transit times, transportation costs, carrier assignments, and delivery outcomes |
| Pricing | Supplier purchase prices, product selling prices, discounts, and relevant cost components |
| Finance | Revenue, material costs, production costs, logistics costs, and profitability measures where the underlying records support them |
| External conditions | Simulated weather, monsoon effects, seasonal factors, and other time-dependent operational conditions |

Not every domain requires a separate physical table. The final design will avoid unnecessary duplication while preserving the relationships needed for analysis.

### 4.3 Time-dependent behaviour

The simulation should represent how the business changes over time.

Examples include:

- Seasonal customer demand and monsoon-related demand changes.
- Long-term changes in demand and product prices.
- Differences in demand between products and customer segments.
- Supplier reliability and variation in procurement lead times.
- Carrier-specific transit behaviour.
- Route-specific transportation conditions.
- Factory capacity constraints and production interruptions.
- Customer purchasing patterns and changes in order frequency.
- Stock shortages, delayed fulfilment, and quality problems.

These patterns should emerge through explicit, documented generation rules.

Where appropriate, the generator will include controlled randomness, shocks, noise, and missing values. The strength of these effects will be configurable and validated rather than chosen solely to make a model appear accurate.

### 4.4 Data integrity and reconciliation

The generator must satisfy business invariants before the full dataset is accepted.

Examples include:

- Every transaction references valid business entities.
- Received material cannot exceed the quantity supported by the corresponding receipt records.
- Production material consumption and finished output follow documented manufacturing rules.
- Inventory balances reconcile with receipts, consumption, production, transfers, dispatches, and adjustments.
- Warehouse and factory transfers have consistent source and destination records.
- Customer fulfilment does not exceed the quantity available for fulfilment under the defined business rules.
- Shipment delivery dates and transit durations are consistent.
- Revenue, cost, discounts, and margins use documented definitions.
- Missing values occur only where the relevant fields permit them.
- Generated data can be reproduced using the same configuration and seed.

Validation should run on a smaller dataset before scaling to hundreds of thousands of records.

The final repository will document known limitations and distinguish intentional imperfections from generator defects.

---

## 5. Data Analytics and Business Intelligence

The analytics layer will investigate the business through SQL, Python, and Power BI.

The emphasis is on answering business questions, identifying relationships, measuring performance, and explaining why operational outcomes occur.

### 5.1 Procurement and supplier analytics

Questions to investigate:

- Which suppliers provide the most reliable deliveries?
- Which suppliers have the longest or most variable lead times?
- How do supplier prices vary across materials and time?
- Which suppliers contribute most to material shortages?
- How do supplier delays affect production schedules?
- Which materials have concentrated sourcing risk?
- Are supplier price increases associated with changes in overall production costs?

Potential metrics include supplier on-time delivery rate, average lead time, lead-time variability, purchase-price variance, rejection rate, and shortage exposure.

### 5.2 Inventory analytics

Questions to investigate:

- Which products and raw materials experience frequent stockouts?
- How much inventory is held at each factory and warehouse?
- Which products have high inventory relative to demand?
- How often do inventory shortages interrupt fulfilment?
- How do inventory movements reconcile across locations?
- Which materials have the greatest operational impact when unavailable?

Potential metrics include inventory turnover, stockout frequency, days of inventory on hand, inventory ageing where supported, and inventory value.

### 5.3 Production analytics

Questions to investigate:

- Which factories and products have the highest production output?
- How does actual output compare with planned production?
- How often does raw-material availability constrain production?
- How does capacity utilisation vary over time?
- Which products experience the most quality-related losses?
- How do production disruptions influence customer fulfilment?

Potential metrics include production attainment, capacity utilisation, yield, defect rate, material utilisation, and production shortfall.

### 5.4 Demand and customer analytics

Questions to investigate:

- How does demand vary by product, customer, region, and season?
- Which products experience the strongest seasonal changes?
- Which customers contribute the most revenue?
- How often is requested demand not fulfilled?
- Are cancellations and backorders concentrated in particular customer segments?
- How do changes in demand affect production and inventory requirements?

Potential metrics include order volume, requested versus fulfilled quantity, fill rate, revenue contribution, cancellation rate, and customer purchasing frequency.

### 5.5 Logistics analytics

Questions to investigate:

- Which carriers and routes experience the most delays?
- How do planned and actual transit times differ?
- How do shipment weight, route characteristics, season, and weather affect delivery?
- Which shipments incur unusually high transportation costs?
- How do late deliveries affect customer service performance?
- How do carrier reliability and capacity influence shipment allocation?

Potential metrics include on-time delivery rate, average delay, transit-time variability, cost per shipment, cost per kilogram, and carrier performance by route.

Inbound deliveries and outbound customer shipments will be analysed separately because their responsibilities and operational constraints differ.

### 5.6 Financial analytics

Questions to investigate:

- Which products generate the highest revenue and contribution margins?
- How do material and transportation costs affect profitability?
- Which customers and product categories contribute most to revenue?
- How do discounts affect realised selling prices?
- How do delays, quality problems, and stock shortages create operational costs?
- How does profitability change across products, factories, and periods?

Financial measures will be calculated from documented cost and revenue components. If the simulation does not model a financial component, the project will not silently treat that component as zero and claim to have calculated complete company profit.

### 5.7 Power BI dashboard

The planned dashboard will provide a management-level overview and focused operational views.

Proposed dashboard areas:

- Executive overview.
- Demand and sales performance.
- Procurement and supplier performance.
- Inventory and stock availability.
- Production and quality.
- Logistics and delivery performance.
- Cost and profitability analysis.

The dashboard will use appropriate relationships, measures, filters, drill-throughs, and time-based comparisons.

The exact dashboard design will follow the questions supported by the validated data rather than being decided by the number of available visual types.

---

## 6. Machine Learning Scope

SteelFlow will investigate several ML use cases using the same connected business data.

Each use case should have a clearly defined target, a defensible prediction time, appropriate features, a baseline model, evaluation metrics, and a documented business interpretation.

The models listed below are planned candidates, not completed results.

### 6.1 Demand forecasting

**Objective:** Forecast future demand for selected products over defined time horizons.

Potential features:

- Historical demand.
- Product and product-family identifiers.
- Calendar and seasonal features.
- Historical prices.
- Customer or regional demand patterns.
- Relevant weather and monsoon indicators.
- Documented demand shocks or trend changes.

Candidate approaches include seasonal naive baselines, statistical forecasting methods, and gradient-boosted models with lagged and calendar features where suitable.

Evaluation will use chronological holdouts and metrics appropriate for the demand distribution, such as MAE, RMSE, and WAPE where defined.

The purpose is to support demand planning and inventory decisions, not merely predict historical order quantities.

### 6.2 Delivery-delay prediction

**Objective:** Estimate whether an outbound shipment will arrive late relative to its agreed delivery commitment.

Potential features:

- Carrier and route.
- Planned transit duration.
- Shipment weight and relevant load characteristics.
- Booking information.
- Season and weather conditions available at prediction time.
- Historical carrier and route performance.
- Shipment scheduling and operational conditions.

Candidate models include logistic regression, decision trees, random forests, and gradient-boosted classifiers such as XGBoost, LightGBM, or CatBoost.

Evaluation will consider precision, recall, F1-score, PR-AUC where appropriate, and probability calibration. Class imbalance will be examined rather than ignored.

A critical constraint is that actual delivery time, actual transit duration, or other post-delivery information must not be used to predict a delay before delivery.

### 6.3 Price prediction

**Objective:** Predict relevant purchase or selling prices for supported products and transactions.

Possible targets include supplier purchase price or customer selling price, treated as separate modelling problems where necessary.

Potential features include:

- Product and material characteristics.
- Supplier or customer attributes.
- Historical prices and documented trends.
- Order quantities.
- Contractual pricing terms.
- Calendar and seasonal effects.

Candidate models include linear regression, regularised regression, random forests, and gradient-boosted regression models.

Evaluation will use MAE and RMSE, alongside residual analysis and comparisons against simple historical or contractual baselines.

### 6.4 Supplier-risk prediction

**Objective:** Identify suppliers associated with elevated future procurement or delivery risk.

Potential signals include historical delivery performance, lead-time variability, quality rejections, price instability, and material criticality.

The project will distinguish between:

- Predicting a future adverse event.
- Assigning a risk score based on historical performance.
- Clustering suppliers by operational characteristics.

These are different tasks and will not be treated as interchangeable.

Where sufficient valid target events exist, classification models may be trained to predict supplier-related disruptions. Otherwise, a transparent scorecard or unsupervised approach may be more appropriate.

### 6.5 Carrier-delay and logistics analysis

Carrier performance can support both descriptive analytics and predictive modelling.

The project may develop route- or carrier-level risk scores, investigate transit-time distributions, and predict shipment-level delays.

Where useful, this analysis will complement the primary delivery-delay model rather than create multiple redundant models with identical targets.

### 6.6 Quality-risk prediction

**Objective:** Investigate whether available production and material information can predict quality problems or elevated defect risk.

Potential features include product type, production conditions, raw-material attributes, factory, supplier history, and relevant process measurements.

This use case depends on generating enough meaningful quality outcomes and documenting when the features become available.

### 6.7 Customer churn or declining purchasing activity

**Objective:** Identify customers whose future purchasing activity is likely to decline or cease under a defined observation and prediction window.

Potential features include purchasing frequency, recency, order volume, historical revenue, fulfilment experience, and changes in purchasing behaviour.

The project must define churn operationally, for example as no qualifying purchase within a specified future period. Customer segmentation and descriptive purchasing analysis will be kept separate from supervised churn prediction.

### 6.8 Anomaly detection

**Objective:** Identify unusual transactions, operational patterns, or business outcomes that warrant investigation.

Candidate techniques include:

- Statistical thresholds and control limits.
- Interquartile-range and robust statistical methods.
- Isolation Forest.
- Other suitable unsupervised anomaly-detection techniques.

Potential applications include unusual shipment costs, extreme transit times, unexpected inventory movements, price deviations, and atypical production or quality outcomes.

An anomaly is not automatically an error or a fraudulent transaction. Findings will be presented as investigation candidates, with appropriate context.

### 6.9 Segmentation and decision support

Additional analyses may group suppliers, customers, products, or carriers by operational characteristics.

Where appropriate, clustering and rule-based recommendations may support:

- Supplier segmentation.
- Customer purchasing profiles.
- Carrier selection analysis.
- Inventory prioritisation.
- Identification of operational bottlenecks.

Optimization and prescriptive recommendations will be attempted only when the necessary decision variables, constraints, and objective functions can be defined clearly.

### ML evaluation principles

All predictive models will follow these principles:

1. Establish a simple baseline before introducing complex models.
2. Separate training, validation, and test data appropriately.
3. Use chronological evaluation for time-dependent tasks where appropriate.
4. Prevent target leakage and respect feature availability at prediction time.
5. Compare models using task-appropriate metrics.
6. Inspect errors and performance across relevant segments.
7. Document synthetic-data limitations and the possibility of generator-specific patterns.
8. Avoid claiming real-world predictive validity solely from performance on synthetic data.

The final set of models will depend on data quality, target availability, and whether the use case produces meaningful results.

---

## 7. Application and System Architecture

The intended system will progressively connect data generation, analytics, ML pipelines, and a user-facing application.

### Proposed architecture

```text
Synthetic Data Generator
          |
          v
Generated Relational Datasets
          |
          v
Data Validation & Reconciliation
          |
          v
DuckDB / Parquet / SQL Analytics
          |
          +---------------------+
          |                     |
          v                     v
   Exploratory Analysis    Power BI Reports
          |
          v
  Feature Engineering
          |
          v
  ML Training & Evaluation
          |
          v
  Model Artifacts & Metrics
          |
          v
       FastAPI
          |
          v
  SteelFlow Web Interface
          |
          v
 Predictions, Risk Signals,
 Business Insights & Decisions
```

This is the target architecture, not a claim that all components are already implemented or connected.

### Planned technologies

| Component | Proposed technology |
|---|---|
| Programming | Python |
| Data manipulation | Pandas and NumPy |
| Analytical database | DuckDB initially |
| Storage and exchange | CSV and Parquet, as appropriate |
| Data validation | Python validation scripts and automated tests |
| Business queries | SQL |
| Visualization | Matplotlib and other appropriate Python visualization tools |
| Business intelligence | Power BI |
| Machine learning | Scikit-learn and suitable gradient-boosting libraries |
| Forecasting | Statistical or ML forecasting approaches selected for the target |
| API | FastAPI |
| Web interface | React or Next.js |
| Version control | Git and GitHub |
| Deployment | To be selected and documented as the application develops |

The initial architecture prioritizes a manageable local development workflow. More infrastructure will be introduced only when the project benefits from it.

---

## 8. Testing, Reproducibility and Data Quality

Testing is a core project requirement, not a final cleanup activity.

### Data-level testing

- Verify primary-key uniqueness.
- Validate foreign-key relationships.
- Check missing-value distributions.
- Detect duplicate or invalid transactions.
- Verify date ordering and time consistency.
- Validate quantity and monetary constraints.
- Reconcile inventory movements.
- Check shipment and delivery logic.
- Validate relationships between generated features and outcomes.

### Analytical testing

- Verify KPI definitions.
- Reconcile aggregates with source transactions.
- Check that SQL transformations preserve intended business meaning.
- Validate Power BI measures against independently calculated results where feasible.

### ML testing

- Check feature availability at prediction time.
- Verify train/test separation.
- Detect target leakage.
- Compare against baseline models.
- Inspect class distributions and target variability.
- Record model configurations, metrics, and evaluation periods.
- Test prediction outputs and expected input schemas.

### Reproducibility

Generation scripts and experiments should document the relevant configuration, random seed, dependencies, and execution instructions.

The goal is to make it possible for another developer to reproduce the dataset and understand how reported results were obtained.

---

## 9. Repository Structure

The repository will evolve with the implementation. The following structure describes the intended organization.

```text
SteelFlow-Intelligence/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── demo/
│   └── data_dictionary/
│
├── src/
│   ├── data_generation/
│   ├── validation/
│   ├── analytics/
│   ├── features/
│   └── models/
│
├── sql/
│   ├── exploration/
│   ├── kpis/
│   └── business_analysis/
│
├── notebooks/
│   ├── eda/
│   └── experiments/
│
├── reports/
│   ├── analysis/
│   └── model_evaluation/
│
├── app/
│   ├── api/
│   └── web/
│
└── tests/
    ├── data/
    ├── analytics/
    └── models/
```

Not every directory needs to exist on day one. Components will be added as they become necessary.

Large generated datasets, trained model binaries, local virtual environments, secrets, and other unsuitable artifacts will be excluded from normal Git commits. Small demo data and appropriate reports may be committed to make the project easier to inspect.

---

## 10. Implementation Roadmap

### Phase 1: Business specification and data generation

- Finalize the business rules and table relationships.
- Define the generation process and its configurable parameters.
- Implement the synthetic data generator.
- Validate a small dataset.
- Correct integrity and business-logic issues.
- Generate the intended full-scale dataset.
- Document the data dictionary and generation process.

**Completion criteria:** The generated datasets are reproducible, connected, validated, and documented.

### Phase 2: Exploratory data analysis and SQL

- Inspect distributions and missing values.
- Analyse demand, prices, suppliers, inventory, production, and shipments.
- Write reusable business queries.
- Define and validate KPIs.
- Document findings, limitations, and operational questions.

**Completion criteria:** The project contains reproducible analyses that explain meaningful business patterns.

### Phase 3: Power BI dashboard

- Design the data model.
- Create measures and analytical dimensions.
- Build management and operational dashboards.
- Validate reported metrics against source data.
- Document the dashboard's purpose and supported decisions.

**Completion criteria:** The dashboard communicates verified business metrics and insights.

### Phase 4: Machine learning

- Define the prediction targets and their timing.
- Build baseline models.
- Create reusable feature-engineering pipelines.
- Train and compare suitable candidate models.
- Evaluate performance on held-out data.
- Investigate errors, leakage risks, and segment-level performance.
- Record model limitations and recommendations.

**Completion criteria:** Each implemented use case has a reproducible evaluation and an explanation of its intended business value.

### Phase 5: API and web application

- Expose selected analytical and predictive functionality through FastAPI.
- Define input and output schemas.
- Integrate trained models where appropriate.
- Build the web interface.
- Present predictions, supporting information, and business insights.
- Add error handling and tests.

**Completion criteria:** Users can interact with selected project capabilities through a documented application interface.

### Phase 6: Deployment and final documentation

- Prepare the application for deployment.
- Configure environment variables and dependency management.
- Add reproducible setup instructions.
- Publish appropriate reports and demonstration material.
- Document known limitations, model results, and future improvements.

**Completion criteria:** The project can be reviewed and reproduced by someone who did not participate in its development.

---

## 11. Limitations and Responsible Interpretation

SteelFlow is a synthetic-data project. Its results must be interpreted accordingly.

- The simulated business does not represent a real company's actual performance.
- Generated relationships may be easier for a model to learn than relationships in real industrial data.
- Model performance on synthetic data does not establish real-world deployment readiness.
- Simulated causal mechanisms are assumptions encoded in the generator, not independently discovered causal relationships.
- Forecasting and prediction quality depends on the validity of the simulated processes and the evaluation design.
- Business recommendations must respect the constraints and information available in the simulated environment.

Where the generator intentionally introduces a relationship between a feature and an outcome, this will be documented so that evaluation does not confuse recoverable synthetic patterns with proof of generalization.

---

## 12. Future Enhancements

Depending on the results of the initial implementation, potential extensions include:

- More advanced forecasting and uncertainty estimation.
- Time-aware monitoring of model performance.
- Improved supplier and carrier risk analysis.
- Explainable ML and feature attribution.
- Scenario simulation for changes in demand, costs, and capacity.
- Inventory and shipment optimization under explicit constraints.
- Automated data-quality and model-evaluation reports.
- Workflow orchestration for repeatable pipelines.
- Model versioning and performance monitoring.
- More extensive API testing and application observability.

These are possible extensions, not requirements that must all be implemented for the project to be successful.

---

## 13. Project Success Criteria

SteelFlow will be evaluated on the quality and completeness of the system rather than the number of technologies used.

The project should demonstrate:

- A well-defined manufacturing business scenario.
- A reproducible and validated synthetic data-generation pipeline.
- Consistent relationships across operational datasets.
- Meaningful SQL analysis and business KPIs.
- Clear and independently verifiable Power BI metrics.
- Appropriate machine learning baselines and evaluation methods.
- Honest treatment of leakage, uncertainty, and synthetic-data limitations.
- A modular and maintainable codebase.
- Documented setup and execution procedures.
- A working application for selected analytical or predictive capabilities once development reaches that stage.

The strongest outcome will be a connected project where the business logic, generated data, analytics, predictive models, and application all support the same operational story.

---

## 14. Development Status

This section will be updated as the project progresses.

| Component | Current status |
|---|---|
| Business scenario | Defined |
| Intended project scope | Documented |
| Data schema and business rules | Being finalized |
| Synthetic data generator | Under development and validation |
| Data quality and reconciliation | Pending complete validation |
| SQL analytics | Planned |
| Exploratory data analysis | Planned |
| Power BI dashboard | Planned |
| ML pipelines | Planned |
| FastAPI integration | Planned |
| Web application | Planned |
| Deployment | Planned |

Status should change only when the corresponding implementation and validation work has actually been completed.

---

## Conclusion

SteelFlow Intelligence aims to demonstrate how data engineering, analytics, and machine learning can work together within a realistic manufacturing supply chain.

The project begins with a carefully modelled business and a trustworthy synthetic dataset. It then builds progressively toward operational reporting, predictive analytics, and an interactive decision-support application.

The central objective is to create a reproducible, technically sound, and business-oriented system that demonstrates the complete journey from raw operational events to useful analytical decisions.

**SteelFlow Intelligence: From supply chain data to operational intelligence.**

