from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from storage import init_db, save_reading

app = FastAPI(title="AquaDrain-AI Sensor API", version="0.1.0")

class SensorReading(BaseModel):
    pressure_1: float = Field(ge=0, description="Pressure sensor 1, use consistent unit e.g. bar")
    pressure_2: float = Field(ge=0, description="Pressure sensor 2, same unit as pressure_1")
    flow_1: float = Field(ge=0, description="Flow sensor 1, use consistent unit e.g. L/min")
    flow_2: float = Field(ge=0, description="Flow sensor 2, same unit as flow_1")
    pump_status: int = Field(ge=0, le=1, description="0=OFF, 1=ON")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"project": "AquaDrain-AI", "status": "API online"}

@app.post("/sensor")
def receive_sensor_data(data: SensorReading):
    try:
        row = data.model_dump()
        row["timestamp"] = datetime.now(timezone.utc).isoformat()
        save_reading(row, source="ESP32")
        return {"ok": True, "message": "Data saved", "timestamp": row["timestamp"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
