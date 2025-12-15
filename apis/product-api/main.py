import json
import uuid
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn

# Configuration
NUM_RECORDS = 10000
DATA_FILE = "products_10k.json"

# Mock Data Sources
SERVICE_LOCATIONS = [10020030, 40050099, 10020031, 55002211, 80009000]

PRODUCT_TEMPLATES = [
    {"group": "Produce", "name": "Organic Cavendish Bananas", "base_price": 0.79, "desc": "Fresh, fair-trade organic bananas grown in Ecuador."},
    {"group": "Produce", "name": "Red Delicious Apples", "base_price": 1.29, "desc": "Crisp and sweet red apples, perfect for snacking."},
    {"group": "Produce", "name": "Hass Avocados", "base_price": 1.50, "desc": "Creamy, ripe avocados. Great for guacamole."},
    {"group": "Dairy", "name": "Whole Milk (1 Gallon)", "base_price": 4.29, "desc": "Pasteurized, homogenized whole milk with Vitamin D."},
    {"group": "Dairy", "name": "Greek Yogurt (Strawberry)", "base_price": 1.19, "desc": "Rich and creamy greek yogurt with real fruit on the bottom."},
    {"group": "Dairy", "name": "Unsalted Butter", "base_price": 3.99, "desc": "Grade AA sweet cream butter, perfect for baking."},
    {"group": "Bakery", "name": "Sourdough Loaf", "base_price": 5.49, "desc": "Hearth-baked sourdough with a crispy crust."},
    {"group": "Bakery", "name": "Blueberry Muffins (4 Pack)", "base_price": 4.99, "desc": "Moist muffins loaded with fresh blueberries."},
    {"group": "Meat", "name": "Boneless Skinless Chicken Breast", "base_price": 5.99, "desc": "Lean, air-chilled chicken breast. No antibiotics."},
    {"group": "Meat", "name": "Ground Beef (80/20)", "base_price": 6.49, "desc": "Premium ground beef, ideal for burgers and tacos."},
    {"group": "Pantry", "name": "Tomato Sauce", "base_price": 2.50, "desc": "Classic marinara sauce made with vine-ripened tomatoes."},
    {"group": "Pantry", "name": "Spaghetti Pasta", "base_price": 1.25, "desc": "Enriched wheat pasta. Cooks in 10 minutes."},
    {"group": "Beverages", "name": "Orange Juice (Pulp Free)", "base_price": 3.99, "desc": "100% pure squeezed orange juice. Not from concentrate."},
    {"group": "Frozen", "name": "Pepperoni Pizza", "base_price": 7.50, "desc": "Thin crust pizza topped with mozzarella and pepperoni."}
]

# Pydantic Models
class Product(BaseModel):
    id: str
    serviceLocationId: int
    productId: str
    productGroup: str
    name: str
    itemDesc: str
    price: float

# FastAPI App
app = FastAPI(
    title="Product API",
    description="API for managing and querying product catalog",
    version="1.0.0"
)

# Global data storage
products_data: List[dict] = []

def generate_dataset():
    """Generate product dataset if it doesn't exist"""
    data = []
    used_product_ids = set()
    
    print(f"Generating {NUM_RECORDS} unique records...")
    
    count = 0
    while count < NUM_RECORDS:
        template = random.choice(PRODUCT_TEMPLATES)
        price_variation = random.uniform(-0.10, 0.50)
        final_price = round(max(0.50, template["base_price"] + price_variation), 2)
        
        sku_prefix = template["name"][:3].upper()
        sku_num = random.randint(1000, 99999)
        product_id = f"SKU-{sku_prefix}-{sku_num}"
        
        if product_id in used_product_ids:
            continue
        
        used_product_ids.add(product_id)
        
        item = {
            "id": str(uuid.uuid4()),
            "serviceLocationId": random.choice(SERVICE_LOCATIONS),
            "productId": product_id,
            "productGroup": template["group"],
            "name": template["name"],
            "itemDesc": template["desc"],
            "price": final_price
        }
        
        data.append(item)
        count += 1

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully created {DATA_FILE} with {len(data)} unique items.")
    return data

def load_products():
    """Load products from JSON file"""
    global products_data
    try:
        with open(DATA_FILE, 'r') as f:
            products_data = json.load(f)
        print(f"Loaded {len(products_data)} products from {DATA_FILE}")
    except FileNotFoundError:
        print(f"{DATA_FILE} not found, generating new dataset...")
        products_data = generate_dataset()

@app.on_event("startup")
async def startup_event():
    """Load products on startup"""
    load_products()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Product API",
        "version": "1.0.0",
        "endpoints": {
            "get_all_products": "/get-all-products",
            "get_product_by_id": "/get-product-by-id/{product_id}",
            "get_products_by_service_location": "/get-products-by-service-location-id/{service_location_id}"
        },
        "total_products": len(products_data)
    }

@app.get("/get-all-products", response_model=List[Product])
async def get_all_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    """
    Get all products with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    return products_data[skip:skip + limit]

@app.get("/get-product-by-id/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    """
    Get a specific product by its productId (SKU)
    
    - **product_id**: The product SKU (e.g., SKU-ORG-12345)
    """
    for product in products_data:
        if product["productId"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")

@app.get("/get-products-by-service-location-id/{service_location_id}", response_model=List[Product])
async def get_products_by_service_location_id(
    service_location_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    """
    Get all products for a specific service location with pagination
    
    - **service_location_id**: The service location ID (e.g., 10020030)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    filtered_products = [
        product for product in products_data 
        if product["serviceLocationId"] == service_location_id
    ]
    
    if not filtered_products:
        raise HTTPException(
            status_code=404, 
            detail=f"No products found for service location ID '{service_location_id}'"
        )
    
    return filtered_products[skip:skip + limit]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_products": len(products_data),
        "service_locations": SERVICE_LOCATIONS
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)