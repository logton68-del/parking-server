import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
from fastapi import FastAPI

# === FIREBASE INIT ===
firebase_key_str = os.getenv("FIREBASE_KEY")

if not firebase_key_str:
    raise ValueError("FIREBASE_KEY not found")

firebase_key = json.loads(firebase_key_str)

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

# === APP ===
app = FastAPI()

# теперь: номер -> токен
protected_numbers = {}
alerts = []

# === PUSH ===
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


# === TEST PUSH ===
@app.get("/send_test")
def send_test():
    for token in protected_numbers.values():
        send_push_notification(
            token,
            "🚨 Внимание",
            "Вашу машину могут эвакуировать!"
        )

    return {"status": "sent"}


# === ROOT ===
@app.get("/")
def root():
    return {"message": "Server is working 🚀"}


# === PROTECT ===
@app.get("/protect")
def protect_plate(number: str, token: str):
    number = number.upper()

    # сохраняем номер -> токен
    protected_numbers[number] = token

    return {
        "status": "protected_enabled",
        "number": number
    }


# === UNPROTECT ===
@app.get("/unprotect")
def unprotect_plate(number: str):
    number = number.upper()

    protected_numbers.pop(number, None)

    global alerts
    alerts = [a for a in alerts if a.get("number") != number]

    return {
        "status": "protected_disabled",
        "number": number
    }


# === CHECK ===
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

        token = protected_numbers[number]

        # 🔥 отправляем push сразу владельцу
        send_push_notification(
            token,
            "🚨 Внимание",
            f"Вашу машину ({number}) могут эвакуировать!"
        )

        return {
            "status": "protected",
            "number": number,
            "alert": "created"
        }

    return {
        "status": "not_found",
        "number": number
    }


# === ALERTS ===
@app.get("/alerts")
def get_alerts():
    return alerts


# === CLEAR ALERT ===
@app.get("/clear")
def clear_alert(number: str):
    number = number.upper()

    global alerts
    alerts = [a for a in alerts if a.get("number") != number]

    return {
        "status": "cleared",
        "number": number
    }


# === DEBUG: список защищённых ===
@app.get("/protected")
def get_protected():
    return protected_numbers
