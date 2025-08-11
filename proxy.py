from flask import Flask, redirect, request, session, url_for, render_template, Response
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # para sessions

CLIENT_ID = "f6706182174fc70842b6161db71246ba"
CLIENT_SECRET = "0cb9d1b9c63450eecd4143ffa161f53154ed8eafc07d9658c0e261d7775688a9"
TENANT = "keyruspt.eu.qlikcloud.com"
REDIRECT_URI = "http://localhost:5000/callback"
WEB_INTEGRATION_ID = "F5lgGsalXWNob9SEj1n-PuH-l93y9Ojk"
APP_ID = "2600467e-7e6c-4c36-9fb4-2139caa1cb4d"
SHEET_ID = "pwn"

AUTH_URL = f"https://{TENANT}/oauth/authorize"
TOKEN_URL = f"https://{TENANT}/oauth/token"

@app.route("/")
def index():
    if "access_token" in session:
        return render_template("proxy.html")
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
        "state": "random_state_string",
        "web-integration-id": WEB_INTEGRATION_ID
    }
    url = AUTH_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Erro: código OAuth não recebido", 400
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "web-integration-id": WEB_INTEGRATION_ID
    }
    token_resp = requests.post(TOKEN_URL, data=data, headers=headers)
    if token_resp.status_code != 200:
        return f"Erro ao obter token: {token_resp.text}", 400
    token_json = token_resp.json()
    session["access_token"] = token_json["access_token"]
    return redirect(url_for("index"))

@app.route("/proxy")
def proxy():
    if "access_token" not in session:
        return redirect(url_for("index"))
    token = session["access_token"]
    url = f"https://{TENANT}/single/?appid={APP_ID}&sheet={SHEET_ID}&opt=ctxmenu,currsel&theme=classic"
    headers = {
        "Authorization": f"Bearer {token}",
        "qlik-web-integration-id": WEB_INTEGRATION_ID
    }
    resp = requests.get(url, headers=headers)
    return Response(resp.content, content_type=resp.headers.get("Content-Type"))

if __name__ == "__main__":
    app.run(debug=True)
