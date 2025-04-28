from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)

# DATA

WEBHOOKS = {
    "void-egg": {
        "role": "<@&1366059599379173467>",
        "free": "https://discord.com/api/webhooks/1366079904554156184/f32ARd2diPXhIYjkLHHuxqWfDGV7y4d-89vmUTbqZmaCDx_FJyI1OC36xL-xHEVfzDdB",
        "premium": "https://discord.com/api/webhooks/1366080458026123264/aCUbgR3e-70ihgGDwjqdg36Nsv5gmoRK482dU5kZcyammPm9L0mFzOCcs-HibiGMyoMe"
    },
    "rainbow-egg": {
        "role": "<@&1366059597881675827>",
        "free": "https://discord.com/api/webhooks/1366079898959216710/JuqW052XBVXFArQSqXt-WO8JbQ4HCtfeY9YKgQWK3F4tXwEmBnD2gsLKHh4QIFuvDllJ",
        "premium": "https://discord.com/api/webhooks/1366080452774858794/VdTb7iy8iZ3LKUBcfpDb7HXY6P1B1tlUYejR1HOluQUwmVdJP4xO2SPRR0F8zPZdRmWo"
    },
    "nightmare-egg": {
        "free": "https://discord.com/api/webhooks/1366079911021903934/Jr6hVrl03hGgXRILL9BV8mv2CvWNc4kCs2uRCKE1TlwoBj6ZHTBSyRRoKO_zt7nNdmP_",
        "premium": "https://discord.com/api/webhooks/1366080468734447746/Fm_yBbfa8Nb5RzKu7WVlzD131_jEROvDTnyxsidx7HJBwS3irFvuyF12Tv94YRs15N2c",
        "role": "<@&1366059601073668166>"
    },
    "combined": {
        "free": "https://discord.com/api/webhooks/1366079891900207236/ThAaXYh-mU4u1p2fLfIG6PRn6k0y_Kst9Zq-xKLWLgdZu93ZPdTfdGJb_s-cxiiE5Ru5",
        "premium": "https://discord.com/api/webhooks/1366080447611797534/kgaLnOlglUpTH1hzuhiHBKUy4CyXu96facOyB0NgR8s1znKpcVFjTpJRPRNNDIjuLZ5U"
    }
}

THUMBNAILS = {
    "silly-egg": "https://cdn.discordapp.com/attachments/993685739000840202/1366049588364185630/Twemoji2_1f602.svg.png",
    "event-3": "https://cdn.discordapp.com/attachments/993685739000840202/1365894024644526201/IMG_4088.png",
    "royal-chest": "https://cdn.discordapp.com/attachments/993685739000840202/1366049704336425073/latest.png",
    "rainbow-egg": "https://cdn.discordapp.com/attachments/993685739000840202/1365892022837313638/Rainbow_Egg.webp",
    "nightmare-egg": "https://cdn.discordapp.com/attachments/993685739000840202/1365892241620729967/Nightmare_Egg.webp",
    "void-egg": "https://cdn.discordapp.com/attachments/993685739000840202/1365892406108618803/Void_Egg.webp"
}

# List egg yang boleh masuk combined
COMBINED_EGGS = {"rainbow-egg", "void-egg", "nightmare-egg"}

# FUNCTIONS

def format_discord_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def send_webhook(url, embed, delay=0, job_id=None, is_free=True):
    if delay > 0:
        time.sleep(delay)

    # Determine the footer text based on whether it's a free webhook
    if is_free:
        footer_text = f"XRift Free Version | Delay 30 Sec (Buy Premium no Delay) | \n{format_discord_time()}"
    else:
        footer_text = f"XRift | {format_discord_time()}"

    # Add the footer with the correct timestamp and message
    embed['footer'] = {"text": footer_text}

    # Prepare the components (buttons)
    components = [
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "style": 5,
                    "label": "Join Game",
                    "url": f"https://fern.wtf/joiner?placeId=85896571713843&gameInstanceId={job_id}" if job_id else "#"
                }
            ]
        }
    ]

    data = {
        "embeds": [embed],
        "components": components
    }

    response = requests.post(url, json=data)

    if response.status_code != 204:
        print(f"Error sending webhook to {url}: {response.status_code}")
    else:
        print(f"Webhook sent to {url} successfully.")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    eggName = data.get("eggName")
    luckText = data.get("luckText")
    timerText = data.get("timerText")
    height = data.get("height")
    jobId = data.get("jobId")
    currentPlayers = data.get("currentPlayers")
    maxPlayers = data.get("maxPlayers")

    webhook_info = WEBHOOKS.get(eggName)
    combined_info = WEBHOOKS.get("combined")

    if not webhook_info and not combined_info:
        return jsonify({"status": "ignored"}), 200

    thumbnail_url = THUMBNAILS.get(eggName)
    display_name = eggName.replace("-", " ").title()

    fields = []

    if luckText:
        fields.append({"name": ":four_leaf_clover: Luck", "value": luckText, "inline": False})

    fields.extend([
        {"name": ":mountain: Height", "value": str(height), "inline": False},
        {"name": "Timer", "value": timerText, "inline": False},
        {"name": "Players", "value": f"{currentPlayers}/{maxPlayers}", "inline": False},
    ])

    base_embed = {
        "title": display_name,
        "description": f"```game:GetService('TeleportService'):TeleportToPlaceInstance(85896571713843,'{jobId}')```",
        "color": 16753920,
        "fields": fields,
        "footer": {"text": f"XRift | {format_discord_time()}"}
    }

    if thumbnail_url:
        base_embed["thumbnail"] = {"url": thumbnail_url}

    # Send webhook to premium and free channels
    if webhook_info:
        if webhook_info.get("premium"):
            executor.submit(send_webhook, webhook_info["premium"], base_embed, job_id=jobId)

        if webhook_info.get("free"):
            executor.submit(send_webhook, webhook_info["free"], base_embed, delay=30, job_id=jobId)

    # If eggName is in the combined list
    if eggName in COMBINED_EGGS and combined_info:
        egg_webhook_info = WEBHOOKS.get(eggName)  # Get webhook info for the specific egg

        # Send to combined webhook
        if combined_info.get("premium"):
            executor.submit(send_webhook, combined_info["premium"], base_embed, job_id=jobId, is_free=True)

        if combined_info.get("free"):
            executor.submit(send_webhook, combined_info["free"], base_embed, delay=30, job_id=jobId, is_free=False)

    return jsonify({"status": "sent"}), 200

@app.route('/')
def hello_world():
    return 'Hello, World!'
if __name__ == "__main__":
    app.run(debug=True)
