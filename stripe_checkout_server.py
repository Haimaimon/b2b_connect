from flask import Flask, request, jsonify, redirect
import stripe
import os
from dotenv import load_dotenv
from services.sheets import GoogleSheetsService

load_dotenv()  # ← חשוב!

app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# דמי עמלה לדוגמה
MATCH_FEE = 10.00  # שקלים

# הגדרת שירות sheets
gs = GoogleSheetsService()

@app.route("/pay/<match_id>", methods=["GET"])
def create_checkout_session(match_id):
    try:
        # יצירת session תשלום
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'ils',
                    'product_data': {
                        'name': f'עמלת התאמה - {match_id}',
                    },
                    'unit_amount': int(MATCH_FEE * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{request.url_root}success?match_id={match_id}",
            cancel_url=f"{request.url_root}cancel",
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route("/success")
def payment_success():
    match_id = request.args.get("match_id")
    if not match_id:
        return "Missing match ID", 400

    # עדכון סטטוס התשלום ל-True בטבלת Matches
    worksheet = gs.sheet.worksheet("Matches")
    matches = worksheet.get_all_records()

    for i, match in enumerate(matches, start=2):  # start=2 בגלל השורה של הכותרות
        if match.get("match_id") == match_id:
            worksheet.update_cell(i, 6, "True")  # סטטוס תשלום
            return "✅ התשלום הצליח! פרטי הקשר יישלחו אליכם בטלגרם."

    return "Match ID not found.", 404

@app.route("/cancel")
def cancel():
    return "❌ התשלום בוטל."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

