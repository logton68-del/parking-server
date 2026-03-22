import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
from fastapi import FastAPI

firebase_key_str = os.getenv("FIREBASE_KEY")

if not firebase_key_str:
    raise ValueError("FIREBASE_KEY not found")

firebase_key = json.loads(firebase_key_str)

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

app = FastAPI()

protected_numbers = set()
alerts = []
tokens = set()

def send_push_notification(token, title, body):
    try:
        message = messaging.Message(
            data={
                "title": title,
                "body": body
            },
            token=token,
        )

        response = messaging.send(message)
        print("Push sent:", response)

    except Exception as e:
        print("ERROR SENDING PUSH:", str(e))

@app.get("/send_test")
def send_test():
    for token in tokens:
        send_push_notification(
            token,
            "🚨 Внимание",
            "Вашу машину могут эвакуировать!"
        )

    return {"status": "sent"}

@app.get("/save_token")
def save_token(token: str):
    tokens.add(token)
    return {
        "status": "saved",
        "tokens_count": len(tokens)
    }

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
