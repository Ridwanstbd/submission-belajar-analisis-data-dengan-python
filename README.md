# Brazilian E-commerce Dashboard ✨

## Description

This dashboard provides comprehensive analysis of Brazilian e-commerce data from 2017-2018. It visualizes key business insights across five main analysis areas:

- Overview - General business metrics, sales trends, and top product categories
- Product Photography Analysis - Impact of product photos on customer conversion and order values
- Payment Installments Analysis - Effect of payment options on purchasing behavior and revenue
- Delivery Performance Analysis - Impact of on-time vs late delivery on customer satisfaction
- Ibitinga Cluster Analysis - Performance comparison between the specialized textile industry cluster in Ibitinga and sellers from other cities

The dashboard incorporates multiple data visualization techniques to present insights from the comprehensive e-commerce dataset, allowing users to understand performance metrics, customer behavior patterns, and strategic opportunities for business growth.

### Data Sources

The dashboard uses Brazilian e-commerce public dataset originally published by Olist Store. The data has been processed and merged into a comprehensive analysis-ready dataset that includes:

- Order information (timestamps, status, delivery dates)
- Product details (categories, photography, pricing)
- Seller information (location, including Ibitinga cluster identification)
- Customer geographic data
- Payment details (methods, installment options)
- Review scores and delivery performance metrics

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app

```
streamlit run dashboard.py
```
