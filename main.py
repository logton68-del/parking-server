from fastapi import FastAPI

app = FastAPI()

protected_numbers = set()
alerts = []

@app.get("/")
def root():
    return {"message": "Server is working 🚀"}

@app.get("/protect")
def protect_plate(number: str):
    protected_numbers.add(number.upper())
    return {
        "status": "protected_enabled",
        "number": number.upper()
    }

@app.get("/unprotect")
def unprotect_plate(number: str):
    protected_numbers.discard(number.upper())
    return {
        "status": "protected_disabled",
        "number": number.upper()
    }

@app.get("/check")
def check_plate(number: str):
    number = number.upper()

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

    return {
        "status": "not_found",
        "number": number
    }

@app.get("/alerts")
def get_alerts():
    return alerts

@app.get("/protected")
def get_protected():
    return list(protected_numbers)
