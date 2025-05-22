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

@app.route("/")
def home():
    return "Stripe Server is alive ✅", 200

@app.route("/pay/<match_id>", methods=["GET"])
def create_checkout_session(match_id):
    payer = request.args.get("payer")
    if not payer:
        return "Missing payer username", 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'ils',
                    'product_data': {
                        'name': f'עמלת התאמה - {match_id}',
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{request.url_root}success?match_id={match_id}&payer={payer}",
            cancel_url=f"{request.url_root}cancel",
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route("/success")
def payment_success():
    match_id = request.args.get("match_id")
    if not match_id:
        return "❌ Missing match ID", 400

    worksheet = gs.sheet.worksheet("Matches")
    matches = worksheet.get_all_records()

    for i, match in enumerate(matches, start=2):  # i = row number
        if match.get("match_id") == match_id:
            buyer_paid = match.get("סטטוס תשלום עסק") == "True"
            supplier_paid = match.get("סטטוס תשלום ספק") == "True"
            buyer_username = match.get("buyer_username")
            supplier_username = match.get("supplier_username")

            # נזהה מי זה ששילם עכשיו לפי query param
            payer_username = request.args.get("payer")  # ?payer=@username
            if payer_username == buyer_username:
                worksheet.update_cell(i, 6, "True")  # תשלום עסק
            elif payer_username == supplier_username:
                worksheet.update_cell(i, 7, "True")  # תשלום ספק
            else:
                return "❌ לא זוהה מי שילם", 400

            # נעדכן מחדש את הסטטוסים
            buyer_paid = worksheet.cell(i, 6).value == "True"
            supplier_paid = worksheet.cell(i, 7).value == "True"

            if buyer_paid and supplier_paid:
                return "🎉 שני הצדדים שילמו. פרטי הקשר יישלחו בטלגרם."
            else:
                return "✅ תשלום התקבל! ממתינים לתשלום מהצד השני."

    return "❌ Match ID not found", 404

@app.route("/cancel")
def cancel():
    return "❌ התשלום בוטל."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

