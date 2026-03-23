import os
import resend
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

KAMPDAVID_EMAIL = os.environ["KAMPDAVID_EMAIL"]   # e.g. info@kampdavid.co.ke
FROM_EMAIL      = os.environ["FROM_EMAIL"]         # e.g. noreply@kampdavid.co.ke (must be verified in Resend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/photos/<path:filename>")
def photos(filename):
    return send_from_directory(os.path.join(BASE_DIR, "photos"), filename)


@app.route("/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}

    first_name = data.get("firstName", "").strip()
    last_name  = data.get("lastName",  "").strip()
    email      = data.get("email",     "").strip()
    phone      = data.get("phone",     "").strip()
    interest   = data.get("interest",  "").strip()
    message    = data.get("message",   "").strip()

    if not first_name or not last_name or not email:
        return jsonify({"error": "First name, last name and email are required."}), 400

    full_name = f"{first_name} {last_name}"

    # 1 — Notify KampDavid
    resend.Emails.send({
        "from":    FROM_EMAIL,
        "to":      [KAMPDAVID_EMAIL],
        "subject": f"New Enquiry from {full_name}",
        "html":    _notification_html(full_name, email, phone, interest, message),
    })

    # 2 — Acknowledge to the sender
    resend.Emails.send({
        "from":    FROM_EMAIL,
        "to":      [email],
        "subject": "Your Enquiry Has Been Received — KampDavid Mall",
        "html":    _acknowledgement_html(first_name),
    })

    return jsonify({"success": True}), 200


# ─── Email templates ──────────────────────────────────────────────────────────

def _notification_html(full_name, email, phone, interest, message):
    phone_row = f"""
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;border-bottom:1px solid #f0f0f0;">
            <strong style="color:#0a0a16;display:inline-block;width:130px;">Phone</strong>{phone or "—"}
          </td>
        </tr>""" if phone else ""

    interest_row = f"""
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;border-bottom:1px solid #f0f0f0;">
            <strong style="color:#0a0a16;display:inline-block;width:130px;">Interested In</strong>{interest}
          </td>
        </tr>""" if interest else ""

    message_block = f"""
        <tr>
          <td style="padding:20px 0 0;">
            <p style="margin:0 0 8px;font-size:13px;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.08em;color:#c9a96e;">Message</p>
            <p style="margin:0;font-size:14px;color:#444;line-height:1.7;
                      background:#f9f9f9;border-left:3px solid #c9a96e;padding:14px 16px;
                      border-radius:0 4px 4px 0;">{message}</p>
          </td>
        </tr>""" if message else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:8px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;">

        <!-- Header -->
        <tr>
          <td style="background:#0a0a16;padding:28px 40px;text-align:center;">
            <p style="margin:0;font-size:22px;font-weight:700;color:#c9a96e;letter-spacing:0.04em;">
              KampDavid Mall
            </p>
            <p style="margin:6px 0 0;font-size:12px;color:rgba(255,255,255,0.45);
                      text-transform:uppercase;letter-spacing:0.12em;">New Enquiry</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 28px;">
            <h2 style="margin:0 0 6px;font-size:20px;color:#0a0a16;">
              You have a new enquiry
            </h2>
            <p style="margin:0 0 28px;font-size:14px;color:#777;">
              Submitted via the KampDavid Mall website contact form.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:8px 0;color:#555;font-size:14px;border-bottom:1px solid #f0f0f0;">
                  <strong style="color:#0a0a16;display:inline-block;width:130px;">Name</strong>{full_name}
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;color:#555;font-size:14px;border-bottom:1px solid #f0f0f0;">
                  <strong style="color:#0a0a16;display:inline-block;width:130px;">Email</strong>
                  <a href="mailto:{email}" style="color:#c9a96e;text-decoration:none;">{email}</a>
                </td>
              </tr>
              {phone_row}
              {interest_row}
              {message_block}
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9f9f9;padding:16px 40px;border-top:1px solid #eee;
                     text-align:center;font-size:12px;color:#aaa;">
            KampDavid Mall &nbsp;|&nbsp; P.O Box 1202-40200, Kisii, Kenya
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _acknowledgement_html(first_name):
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:8px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;">

        <!-- Header -->
        <tr>
          <td style="background:#0a0a16;padding:28px 40px;text-align:center;">
            <p style="margin:0;font-size:22px;font-weight:700;color:#c9a96e;letter-spacing:0.04em;">
              KampDavid Mall
            </p>
            <p style="margin:6px 0 0;font-size:12px;color:rgba(255,255,255,0.45);
                      text-transform:uppercase;letter-spacing:0.12em;">Enquiry Received</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 32px;">
            <h2 style="margin:0 0 16px;font-size:20px;color:#0a0a16;">
              Thank you, {first_name}!
            </h2>
            <p style="margin:0 0 14px;font-size:15px;color:#444;line-height:1.7;">
              We have received your enquiry and our team will review it shortly.
              You can expect to hear from us within <strong>1–2 business days</strong>.
            </p>
            <p style="margin:0 0 28px;font-size:15px;color:#444;line-height:1.7;">
              In the meantime, feel free to reach us directly:
            </p>

            <!-- Contact details -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#f9f9f9;border-radius:6px;padding:0;">
              <tr>
                <td style="padding:14px 20px;font-size:14px;color:#555;
                           border-bottom:1px solid #eee;">
                  📞 &nbsp;<a href="tel:+254738988474" style="color:#c9a96e;text-decoration:none;">
                    0738 988 474
                  </a> &nbsp;/&nbsp;
                  <a href="tel:+254717232295" style="color:#c9a96e;text-decoration:none;">
                    0717 232 295
                  </a>
                </td>
              </tr>
              <tr>
                <td style="padding:14px 20px;font-size:14px;color:#555;
                           border-bottom:1px solid #eee;">
                  ✉️ &nbsp;<a href="mailto:info@kampdavid.co.ke"
                              style="color:#c9a96e;text-decoration:none;">
                    info@kampdavid.co.ke
                  </a>
                </td>
              </tr>
              <tr>
                <td style="padding:14px 20px;font-size:14px;color:#555;">
                  🌐 &nbsp;<a href="http://www.kampdavid.co.ke"
                              style="color:#c9a96e;text-decoration:none;">
                    www.kampdavid.co.ke
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- CTA -->
        <tr>
          <td style="padding:0 40px 36px;text-align:center;">
            <a href="http://www.kampdavid.co.ke"
               style="display:inline-block;padding:13px 32px;
                      background:linear-gradient(135deg,#c9a96e,#a07840);
                      color:#fff;text-decoration:none;border-radius:4px;
                      font-size:14px;font-weight:700;letter-spacing:0.05em;">
              Visit Our Website
            </a>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9f9f9;padding:16px 40px;border-top:1px solid #eee;
                     text-align:center;font-size:12px;color:#aaa;">
            KampDavid Mall &nbsp;|&nbsp; P.O Box 1202-40200, Kisii, Kenya<br>
            <span style="font-size:11px;">
              You received this email because you submitted an enquiry on our website.
            </span>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5000)
