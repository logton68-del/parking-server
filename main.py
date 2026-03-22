from fastapi import FastAPI

app = FastAPI()

protected_numbers = ["A096MT156", "X777XX77"]
alerts = []

@app.get("/")
def root():
    return {"message": "Server is working 🚀"}

@app.get("/check")
def check_plate(number: str):
    if number in protected_numbers:
        alerts.append({
            "number": number,
            "status": "alert"
        })
        return {
            "status": "protected",
            "number": number,
            "alert": "created"
        }
    else:
        return {
            "status": "not_found",
            "number": number
        }

@app.get("/alerts")
def get_alerts():
    return alerts
