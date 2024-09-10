from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from datetime import datetime
import sqlite3

# Importing necessary functions from bot.py
from bot import calcData, saveData, get_today_stats

app = FastAPI()

# Define the food data model that will be received
class FoodData(BaseModel):
    name: str
    prot: float
    fat: float
    carb: float
    kcal: float
    weight: float

# Endpoint to receive food data and process it
@app.post("/process_food_data")
async def process_food_data(data: FoodData):
    # Calculate the food data based on the received data
    processed_data = {
        "Prot": data.prot * data.weight / 100,
        "Fat": data.fat * data.weight / 100,
        "Carb": data.carb * data.weight / 100,
        "KCal": data.kcal * data.weight / 100,
        "Name": data.name,
        "Weight": data.weight
    }
    
    # Save processed data into the database using bot's functions
    saveData(processed_data)
    
    return {"status": "Food data processed and saved successfully"}

# Endpoint to retrieve the current day's status of nutrient intake
@app.get("/get_status")
async def get_status():
    DayFoodData = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'KCal': 0}
    
    for row in get_today_stats():
        if row[3]:
            DayFoodData['Prot'] += row[3]
        if row[4]:
            DayFoodData['Fat'] += row[4]
        if row[5]:
            DayFoodData['Carb'] += row[5]
        if row[6]:
            DayFoodData['KCal'] += row[6]
    
    # Returning the daily intake summary
    return {
        "Protein (g)": round(DayFoodData['Prot']),
        "Fat (g)": round(DayFoodData['Fat']),
        "Carbohydrates (g)": round(DayFoodData['Carb']),
        "Calories (kcal)": round(DayFoodData['KCal']),
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
