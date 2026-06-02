"""
Flask application — Number Lookup PoC.
"""
import os
import re
from decimal import Decimal, InvalidOperation

from flask import Flask, redirect, render_template, request, session, url_for

import db
from colors import get_number_colors

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production-abc123xyz")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB hard cap on request body

db.init_db()

_VALID_NUMBER_RE = re.compile(r"^-?(\d+\.?\d*|\.\d+)$")
MAX_NUMBER_LEN = 10_000
MAX_SAVE_LEN = 2_000


@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'"
    )
    return response


def _validate_and_normalize(raw: str) -> str:
    """
    Clean and validate user input.
    - Strips commas
    - Rejects anything that isn't a valid number (digits, optional leading -, optional .)
    - Enforces MAX_NUMBER_LEN character cap
    - Parses with Decimal for arbitrary precision
    - Returns canonical string representation
    Raises ValueError with a user-friendly message on bad input.
    """
    cleaned = raw.strip().replace(",", "")
    if not cleaned:
        raise ValueError("Please enter a number.")
    if len(cleaned) > MAX_NUMBER_LEN:
        raise ValueError(
            f"Input too long. Numbers are limited to {MAX_NUMBER_LEN:,} characters."
        )
    if not _VALID_NUMBER_RE.match(cleaned):
        raise ValueError(
            "Invalid input. Only numbers are accepted "
            "(digits, an optional minus sign, and an optional decimal point)."
        )
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError("Could not parse that as a number.")
    return str(value)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    raw = request.form.get("number", "")
    try:
        canonical = _validate_and_normalize(raw)
    except ValueError as exc:
        return render_template("index.html", error=str(exc), value=raw)
    session["number"] = canonical
    return redirect(url_for("view_number"))


@app.route("/view", methods=["GET"])
def view_number():
    canonical = session.get("number")
    if not canonical:
        return redirect(url_for("index"))
    saved_text = db.lookup_number(canonical)
    bg_hex, text_hex = get_number_colors(canonical)
    return render_template(
        "number.html",
        number=canonical,
        saved_text=saved_text,
        bg_hex=bg_hex,
        text_hex=text_hex,
    )


@app.route("/view/save", methods=["POST"])
def save():
    canonical = session.get("number")
    if not canonical:
        return redirect(url_for("index"))
    text = request.form.get("saved_text", "").strip()
    if not text:
        bg_hex, text_hex = get_number_colors(canonical)
        return render_template(
            "number.html",
            number=canonical,
            saved_text=None,
            bg_hex=bg_hex,
            text_hex=text_hex,
            save_error="Text cannot be empty.",
        )
    if len(text) > MAX_SAVE_LEN:
        bg_hex, text_hex = get_number_colors(canonical)
        return render_template(
            "number.html",
            number=canonical,
            saved_text=None,
            bg_hex=bg_hex,
            text_hex=text_hex,
            save_error=f"Text too long. Maximum is {MAX_SAVE_LEN:,} characters.",
        )
    db.save_number(canonical, text)
    return redirect(url_for("view_number"))


if __name__ == "__main__":
    app.run(debug=True)
