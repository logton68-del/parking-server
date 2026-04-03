import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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
    return {
        "protected_numbers": list(protected_numbers.keys())
    }

# === MINI SITE ===
@app.get("/report/{number}", response_class=HTMLResponse)
def report_page(number: str):
    number = number.upper()

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>ParkingShield</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
                font-family: Arial, sans-serif;
                color: white;
            }}

            .card {{
                width: 90%;
                max-width: 420px;
                background: #1E293B;
                border-radius: 20px;
                padding: 28px;
                box-sizing: border-box;
                text-align: center;
                box-shadow: 0 12px 30px rgba(0,0,0,0.35);
                border: 1px solid rgba(255,255,255,0.08);
            }}

            .logo {{
                font-size: 30px;
                margin-bottom: 8px;
            }}

            .title {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            .subtitle {{
                font-size: 15px;
                color: #CBD5E1;
                margin-bottom: 22px;
                line-height: 1.4;
            }}

            .plate-label {{
                color: #94A3B8;
                font-size: 14px;
            }}

            .plate {{
                font-size: 30px;
                font-weight: bold;
                color: #22C55E;
                margin: 14px 0 26px 0;
                letter-spacing: 1px;
            }}

            button, a.button-link {{
                display: block;
                width: 100%;
                box-sizing: border-box;
                padding: 15px;
                margin-top: 14px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                cursor: pointer;
                text-decoration: none;
            }}

            .alert-btn {{
                background: #EF4444;
                color: white;
            }}

            .app-btn {{
                background: #2563EB;
                color: white;
            }}

            .result {{
                margin-top: 18px;
                font-size: 15px;
                color: #E2E8F0;
                min-height: 22px;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">🚗</div>
            <div class="title">ParkingShield</div>
            <div class="subtitle">Если автомобиль мешает, вы можете быстро сообщить владельцу</div>

            <div class="plate-label">Номер автомобиля</div>
            <div class="plate">{number}</div>

            <button class="alert-btn" onclick="sendAlert()">🚨 Сообщить владельцу</button>

            <a class="button-link app-btn" href="https://play.google.com/store/apps/details?id=com.example.parkingshield">
                📱 Скачать приложение
            </a>

            <div class="result" id="result"></div>
        </div>

        <script>
            function sendAlert() {{
                const result = document.getElementById("result");
                result.innerText = "Отправляем сигнал...";

                fetch("/check?number={number}")
                    .then(response => response.json())
                    .then(data => {{
                        if (data.status === "protected") {{
                            result.innerText = "Сигнал отправлен владельцу 🚨";
                        }} else {{
                            result.innerText = "Этот автомобиль сейчас не найден в системе";
                        }}
                    }})
                    .catch(() => {{
                        result.innerText = "Ошибка связи с сервером";
                    }});
            }}
        </script>
    </body>
    </html>
    """
