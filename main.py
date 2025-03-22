from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict
from producer import KafkaProducer

app = FastAPI()
kafka_producer = KafkaProducer()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template rendering
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/enter_data")
def enter_data(request: Request):
    # Categorical options
    categories = ["Clothing", "Food", "Electronics", "Furniture"]
    transportation_modes = ["Air", "Rail", "Road", "Sea"]

    return templates.TemplateResponse(
        "enter_data.html",
        {"request": request, "categories": categories, "transportation_modes": transportation_modes},
    )


@app.post("/submit")
def submit_data(
    request: Request,
    sku: str = Form(...),
    category: str = Form(...),
    sales_last_month: int = Form(...),
    sales_last_week: int = Form(...),
    sales_trend: float = Form(...),
    current_stock: int = Form(...),
    warehouse_capacity: int = Form(...),
    supplier_lead_time: int = Form(...),
    manufacturing_lead_time: int = Form(...),
    transportation_mode: str = Form(...),
    historical_defect_rate: float = Form(...),
    price_adjustment: float = Form(...),
    seasonality_index: float = Form(...),
    holiday_effect: float = Form(...),
    customer_demand_fluctuation: float = Form(...),
    economic_indicator: float = Form(...),
    competitor_pricing: float = Form(...),
    marketing_spend: int = Form(...),
    regional_sales_growth: float = Form(...),
    inventory_turnover_rate: float = Form(...),
):
    data = {
        "SKU": sku,
        "Category": category,
        "Sales Last Month": sales_last_month,
        "Sales Last Week": sales_last_week,
        "Sales Trend": sales_trend,
        "Current Stock": current_stock,
        "Warehouse Capacity": warehouse_capacity,
        "Supplier Lead Time": supplier_lead_time,
        "Manufacturing Lead Time": manufacturing_lead_time,
        "Transportation Mode": transportation_mode,
        "Historical Defect Rate": historical_defect_rate,
        "Price Adjustment": price_adjustment,
        "Seasonality Index": seasonality_index,
        "Holiday Effect": holiday_effect,
        "Customer Demand Fluctuation": customer_demand_fluctuation,
        "Economic Indicator": economic_indicator,
        "Competitor Pricing": competitor_pricing,
        "Marketing Spend": marketing_spend,
        "Regional Sales Growth": regional_sales_growth,
        "Inventory Turnover Rate": inventory_turnover_rate,
    }
    kafka_producer.produce(**data)
    return templates.TemplateResponse("result.html", {"request": request, "data": data})



if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app",host='0.0.0.0',port=5000)