from flask import Flask, request, jsonify
import requests
import concurrent.futures
import time

app = Flask(__name__)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

WEBHOOKS = {
    "void-egg": {
        "free": "LINK_FREE",
        "premium": "LINK_PREMIUM",
        "roleTag": "<@&role>"
    },
    "combined": {
        "free": "LINK_COMBINED_FREE",
        "premium": "LINK_COMBINED_PREMIUM",
        "roleTag": ""
    },
    # tambahkan egg lainnya di sini
}

def send_webhook(url, payload):
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"[SEND] {url} -> Status {response.status_code}")
    except Exception as e:
        print("[ERROR SEND]", e)

def delayed_send(url, payload, delay):
    time.sleep(delay)
    send_webhook(url, payload)

def handle_send(data):
    eggName = data.get('eggName')
    luckText = data.get('luckText')
    timerText = data.get('timerText')
    height = data.get('height')
    jobId = data.get('jobId')

    if not eggName or not jobId:
        print("[ERROR] Missing eggName or jobId")
        return

    webhook = WEBHOOKS.get(eggName, WEBHOOKS.get("combined"))

    embed = {
        "title": eggName.replace("-", " ").title(),
        "description": f"```game:GetService('TeleportService'):TeleportToPlaceInstance(85896571713843,'{jobId}')```",
        "color": 16753920,
        "fields": [
            {"name": ":four_leaf_clover: Luck", "value": luckText or "Unknown", "inline": False},
            {"name": ":mountain: Height", "value": str(height or "0"), "inline": False},
            {"name": "Timer", "value": timerText or "Unknown", "inline": False}
        ],
        "footer": {"text": "XRift Bot"},
        "thumbnail": {
            "url": "THUMBNAIL_URL"  # opsional
        }
    }

    payload = {"embeds": [embed]}

    # Kirim langsung ke premium
    if webhook.get("premium"):
        executor.submit(send_webhook, webhook["premium"], payload)

    # Kirim ke free setelah 30 detik
    if webhook.get("free"):
        executor.submit(delayed_send, webhook["free"], payload, 30)

@app.route('/')
def hello():
    return "<p>Webhook Server Alive!</p>"

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    executor.submit(handle_send, data)
    return jsonify({"status": "queued"}), 200
