from fastapi import FastAPI

app = FastAPI()

protected_numbers = set()
alerts = []

@app.get("/")
def root():
    return {"message": "Server is working 🚀"}

@app.get("/protect")
def protect_plate(number: str):
    number = number.upper()
    protected_numbers.add(number)
    return {
        "status": "protected_enabled",
        "number": number
    }

@app.get("/unprotect")
def unprotect_plate(number: str):
    number = number.upper()
    protected_numbers.discard(number)

    global alerts
    alerts = [a for a in alerts if a.get("number") != number]

    return {
        "status": "protected_disabled",
        "number": number
    }

@app.get("/check")
def check_plate(number: str):
    number = number.upper()

    if number in protected_numbers:
        already_exists = any(a.get("number") == number for a in alerts)

        if not already_exists:
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

@app.get("/clear")
def clear_alert(number: str):
    number = number.upper()

    global alerts
    alerts = [a for a in alerts if a.get("number") != number]

    return {
        "status": "cleared",
        "number": number
    }

@app.get("/protected")
def get_protected():
    return list(protected_numbers)
