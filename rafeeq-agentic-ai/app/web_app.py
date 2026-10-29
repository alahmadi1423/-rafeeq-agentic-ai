from flask import Flask, jsonify, render_template, request

from app.openrouter_agent import run_openrouter_agent

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"error": "اكتب رسالة أولاً."}), 400

    try:
        result = run_openrouter_agent(message)
        return jsonify({"result": result})
    except Exception:
        app.logger.exception("Rafeeq agent request failed")
        return jsonify({
            "error": "تعذر تشغيل الوكيل. تحقق من مفتاح OpenRouter والاتصال، ثم راجع سجل الخادم."
        }), 500


if __name__ == "__main__":
    # Local demo only. Do not expose publicly without authentication and safeguards.
    app.run(host="127.0.0.1", port=5000, debug=False)
