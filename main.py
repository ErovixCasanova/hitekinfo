# Developed NIROB | Premium JWT Generator API & Web
# Fixed By NIROB
# tg : MT_0G
# Vercel-compatible Flask version

import os
import sys
import json
import time
import random
import gzip
import ssl
import http.client
from io import BytesIO
from datetime import datetime

import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from flask import Flask, request, jsonify, render_template_string

# Protobuf modules (must be present in the same directory)
import MajoRLoGinrEq_pb2
import MajoRLoGinrEs_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== CONSTANTS ====================
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
PORT = int(os.environ.get("PORT", 8080))

# Vercel looks for a top-level variable named `app` (Flask instance)
app = Flask(__name__)


# ==================== HELPER FUNCTIONS ====================

def encrypt_proto(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(data, AES.block_size)
    return cipher.encrypt(padded)


def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": str(uid),
        "password": str(password),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            j = r.json()
            return j.get('access_token'), j.get('open_id')
        return None, None
    except Exception:
        return None, None


def major_login_protobuf(access_token, open_id):
    try:
        major_login = MajoRLoGinrEq_pb2.MajorLogin()
        major_login.event_time = str(datetime.now())[:-7]
        major_login.game_name = "free fire"
        major_login.platform_id = 2
        major_login.client_version = "1.126.2"
        major_login.client_version_code = "2024010012"
        major_login.system_software = "Android OS 11 / API-30 (RQ3A.210805.001)"
        major_login.system_hardware = "Handheld"
        major_login.device_type = "Handheld"
        major_login.telecom_operator = "Verizon"
        major_login.network_operator_a = "Verizon"
        major_login.network_type = "WIFI"
        major_login.network_type_a = "WIFI"
        major_login.screen_width = 1080
        major_login.screen_height = 2400
        major_login.screen_dpi = "440"
        major_login.processor_details = "ARMv8"
        major_login.cpu_type = 2
        major_login.cpu_architecture = "64"
        major_login.memory = 6144
        major_login.gpu_renderer = "Adreno (TM) 650"
        major_login.gpu_version = "OpenGL ES 3.2 V@1.50"
        major_login.graphics_api = "OpenGLES3"
        major_login.unique_device_id = f"Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c{random.randint(10,99)}"
        major_login.client_ip = ""
        major_login.language = "en"
        major_login.open_id = open_id
        major_login.open_id_type = "4"
        major_login.login_open_id_type = 4
        major_login.access_token = access_token
        major_login.login_by = 3
        major_login.platform_sdk_id = 2
        major_login.origin_platform_type = "4"
        major_login.primary_platform_type = "4"

        memory_available = major_login.memory_available
        memory_available.version = 55
        memory_available.hidden_value = 81

        major_login.external_storage_total = 128512
        major_login.external_storage_available = random.randint(38000, 52000)
        major_login.internal_storage_total = 110731
        major_login.internal_storage_available = random.randint(18000, 32000)
        major_login.game_disk_storage_total = 26628
        major_login.game_disk_storage_available = random.randint(18000, 25000)
        major_login.external_sdcard_total_storage = 119234
        major_login.external_sdcard_avail_storage = random.randint(25000, 60000)
        major_login.library_path = f"/data/app/~~{random.randint(100,999)}/base.apk"
        major_login.library_token = "hash|base.apk"
        major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
        major_login.supported_astc_bitset = 16383
        major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
        major_login.loading_time = random.randint(9000, 18000)
        major_login.release_channel = "android"
        major_login.channel_type = 3
        major_login.reg_avatar = 1
        major_login.if_push = 1
        major_login.is_vpn = 0
        major_login.android_engine_init_flag = 110009

        serialized = major_login.SerializeToString()
        encrypted = encrypt_proto(serialized)

        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=15)
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        conn.request("POST", "/MajorLogin", body=encrypted, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()

        if response.getheader('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()
        conn.close()

        if response.status in [200, 201]:
            return raw_data.hex()
        return None
    except Exception:
        return None


def decrypt_major_response(hex_data):
    try:
        proto = MajoRLoGinrEs_pb2.MajorLoginRes()
        proto.ParseFromString(bytes.fromhex(hex_data))
        return proto
    except Exception:
        return None


def generate_jwt(uid, password):
    """Main function to generate JWT token from UID and Password"""
    result = {
        "success": False,
        "uid": uid,
        "jwt_token": None,
        "account_uid": None,
        "region": None,
        "message": "",
        "timestamp": datetime.now().isoformat()
    }

    if not uid or not password:
        result["message"] = "UID and Password are required."
        return result

    if not uid.isdigit() or len(uid) < 8:
        result["message"] = "Invalid UID format."
        return result

    access_token, open_id = get_access_token(uid, password)
    if not access_token or not open_id:
        result["message"] = "Invalid UID or Password."
        return result

    response_hex = major_login_protobuf(access_token, open_id)
    if not response_hex:
        result["message"] = "Account may be banned or invalid."
        return result

    login_data = decrypt_major_response(response_hex)
    if not login_data:
        result["message"] = "Failed to decrypt response."
        return result

    jwt_token = login_data.token
    if not jwt_token:
        result["message"] = "No JWT token received."
        return result

    result["success"] = True
    result["jwt_token"] = jwt_token
    result["account_uid"] = str(login_data.account_uid)
    result["region"] = getattr(login_data, 'region', 'IND')
    result["message"] = "JWT generated successfully!"

    return result


# ==================== PREMIUM HTML PAGE ====================
HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obscura JWT GENERATOR</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0f;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Rajdhani', sans-serif;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            right: -50%;
            bottom: -50%;
            background: 
                radial-gradient(ellipse at 20% 50%, rgba(255,0,100,0.08), transparent 50%),
                radial-gradient(ellipse at 80% 50%, rgba(100,0,255,0.08), transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(0,200,255,0.05), transparent 50%);
            animation: bgFloat 20s ease-in-out infinite alternate;
            z-index: 0;
            pointer-events: none;
        }
        @keyframes bgFloat {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(2%, -2%) rotate(3deg); }
        }
        .container {
            background: rgba(10, 10, 20, 0.92);
            border-radius: 28px;
            padding: 45px 40px;
            max-width: 580px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 40px 100px rgba(0,0,0,0.8), 0 0 80px rgba(255,0,100,0.03);
            position: relative;
            z-index: 1;
            backdrop-filter: blur(30px);
        }
        .container::before {
            content: '';
            position: absolute;
            top: -1px; left: -1px; right: -1px; bottom: -1px;
            border-radius: 29px;
            background: linear-gradient(135deg, rgba(255,0,100,0.15), rgba(100,0,255,0.15), rgba(0,200,255,0.1));
            z-index: -1;
            opacity: 0.5;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header .logo { display: inline-block; margin-bottom: 8px; }
        .header .logo .icon { font-size: 32px; color: #ff0066; margin-right: 8px; }
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff0066, #cc00ff, #6600ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 3px;
            display: inline-block;
        }
        .header .subtitle {
            color: rgba(255,255,255,0.3);
            font-size: 13px;
            letter-spacing: 5px;
            margin-top: 6px;
            font-weight: 300;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            color: rgba(255,255,255,0.5);
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        .form-group .input-wrap {
            position: relative;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
            transition: all 0.3s ease;
            overflow: hidden;
        }
        .form-group .input-wrap:focus-within {
            border-color: rgba(255,0,100,0.3);
            box-shadow: 0 0 30px rgba(255,0,100,0.04);
            background: rgba(255,255,255,0.05);
        }
        .form-group .input-wrap .icon-left {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255,255,255,0.15);
            font-size: 14px;
            pointer-events: none;
        }
        .form-group input {
            width: 100%;
            padding: 15px 16px 15px 44px;
            background: transparent;
            border: none;
            color: #e0e0e0;
            font-size: 15px;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 500;
            letter-spacing: 0.5px;
            outline: none;
        }
        .form-group input::placeholder { color: rgba(255,255,255,0.15); font-weight: 300; }
        .form-group input:-webkit-autofill {
            -webkit-box-shadow: 0 0 0 1000px rgba(10,10,20,0.95) inset !important;
            -webkit-text-fill-color: #e0e0e0 !important;
        }
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 3px;
            background: linear-gradient(135deg, #ff0066, #cc00ff);
            color: #fff;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            position: relative;
            overflow: hidden;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(255,0,100,0.25); }
        .btn:active { transform: scale(0.97); }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
        .btn .btn-text { position: relative; z-index: 1; }
        .result-box {
            margin-top: 28px;
            border-radius: 16px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 20px;
            display: none;
            animation: fadeSlide 0.4s ease;
        }
        .result-box.show { display: block; }
        @keyframes fadeSlide {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-box .result-header {
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 14px; padding-bottom: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .result-box .result-header .status-icon { font-size: 20px; }
        .result-box .result-header .status-text { font-size: 15px; font-weight: 600; letter-spacing: 0.5px; }
        .result-box .result-header .status-text.success { color: #00e676; }
        .result-box .result-header .status-text.error { color: #ff1744; }
        .result-box .info-row {
            display: flex; justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            font-size: 13px; align-items: center;
        }
        .result-box .info-row:last-child { border-bottom: none; }
        .result-box .info-row .label { color: rgba(255,255,255,0.35); font-weight: 300; letter-spacing: 1px; font-size: 12px; }
        .result-box .info-row .value {
            color: #d0d0d0; font-weight: 500; text-align: right;
            max-width: 60%; word-break: break-all; font-size: 13px;
        }
        .result-box .info-row .value.token-value {
            font-family: 'Courier New', monospace;
            font-size: 11px; color: #ff66aa;
            max-width: 70%;
            background: rgba(255,0,100,0.05);
            padding: 4px 8px; border-radius: 6px;
        }
        .result-box .copy-section { margin-top: 14px; display: flex; gap: 8px; }
        .result-box .copy-section .copy-btn {
            flex: 1; padding: 9px;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            background: rgba(255,255,255,0.02);
            color: rgba(255,255,255,0.4);
            font-family: 'Rajdhani', sans-serif;
            font-size: 12px; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease;
            letter-spacing: 1px; text-align: center;
        }
        .result-box .copy-section .copy-btn:hover {
            background: rgba(255,255,255,0.06); color: #fff;
            border-color: rgba(255,255,255,0.12);
        }
        .result-box .copy-section .copy-btn.copied {
            border-color: #00e676; color: #00e676;
            background: rgba(0,230,118,0.05);
        }
        .footer {
            text-align: center; margin-top: 22px;
            color: rgba(255,255,255,0.08); font-size: 11px;
            letter-spacing: 3px; font-weight: 300;
        }
        .footer .brand {
            background: linear-gradient(135deg, #ff0066, #cc00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .loader {
            display: none; width: 28px; height: 28px;
            border: 2px solid rgba(255,255,255,0.05);
            border-top-color: #ff0066;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            margin: 0 auto 4px;
        }
        .loader.show { display: block; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .api-badge {
            text-align: center; margin-top: 14px; padding: 10px;
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.03);
        }
        .api-badge code {
            color: rgba(255,255,255,0.2); font-size: 11px;
            font-family: 'Courier New', monospace; letter-spacing: 0.5px;
        }
        .api-badge code .highlight { color: #ff66aa; }
        @media (max-width: 500px) {
            .container { padding: 28px 18px; }
            .header h1 { font-size: 22px; letter-spacing: 2px; }
            .form-group input { font-size: 14px; padding: 13px 14px 13px 40px; }
            .btn { font-size: 13px; padding: 14px; }
            .result-box .info-row { flex-direction: column; gap: 2px; align-items: flex-start; }
            .result-box .info-row .value { max-width: 100%; text-align: left; }
            .result-box .copy-section { flex-direction: column; }
            .result-box .info-row .value.token-value { max-width: 100%; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">
            <span class="icon"><i class="fas fa-crown"></i></span>
            <h1>NIROB JWT</h1>
        </div>
        <div class="subtitle">PREMIUM TOKEN GENERATOR</div>
    </div>

    <form id="jwtForm" onsubmit="generateJWT(event)">
        <div class="form-group">
            <label><i class="fas fa-user"></i> UID</label>
            <div class="input-wrap">
                <span class="icon-left"><i class="fas fa-id-card"></i></span>
                <input type="text" id="uid" placeholder="Enter Free Fire UID" required>
            </div>
        </div>
        <div class="form-group">
            <label><i class="fas fa-lock"></i> PASSWORD</label>
            <div class="input-wrap">
                <span class="icon-left"><i class="fas fa-key"></i></span>
                <input type="password" id="password" placeholder="Enter Free Fire Password" required>
            </div>
        </div>
        <button type="submit" class="btn" id="submitBtn">
            <span class="btn-text"><i class="fas fa-bolt"></i> GENERATE JWT</span>
        </button>
    </form>

    <div class="loader" id="loader"></div>

    <div class="result-box" id="resultBox">
        <div class="result-header">
            <span class="status-icon" id="statusIcon"><i class="fas fa-check-circle"></i></span>
            <span class="status-text" id="statusText">Success</span>
        </div>
        <div class="info-row">
            <span class="label"><i class="fas fa-user"></i> UID</span>
            <span class="value" id="resultUid">-</span>
        </div>
        <div class="info-row">
            <span class="label"><i class="fas fa-id-badge"></i> Account UID</span>
            <span class="value" id="resultAccountUid">-</span>
        </div>
        <div class="info-row">
            <span class="label"><i class="fas fa-globe"></i> Region</span>
            <span class="value" id="resultRegion">-</span>
        </div>
        <div class="info-row">
            <span class="label"><i class="fas fa-ticket-alt"></i> JWT Token</span>
            <span class="value token-value" id="resultToken">-</span>
        </div>
        <div class="copy-section">
            <button class="copy-btn" onclick="copyToken()"><i class="fas fa-copy"></i> COPY TOKEN</button>
            <button class="copy-btn" onclick="copyAll()"><i class="fas fa-copy"></i> COPY ALL</button>
        </div>
    </div>

    <div class="api-badge">
        <code>API: <span class="highlight">/NIROB?uid={UID}&password={PASS}</span></code>
    </div>

    <div class="footer">
        <span class="brand">NIROB</span> &bull; PREMIUM JWT API
    </div>
</div>

<script>
    async function generateJWT(event) {
        event.preventDefault();
        const uid = document.getElementById('uid').value.trim();
        const password = document.getElementById('password').value.trim();
        const submitBtn = document.getElementById('submitBtn');
        const loader = document.getElementById('loader');
        const resultBox = document.getElementById('resultBox');
        
        if (!uid || !password) {
            showResult(false, 'Please fill in both UID and Password.', {});
            return;
        }
        
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').textContent = 'GENERATING...';
        loader.classList.add('show');
        resultBox.classList.remove('show');
        
        try {
            const response = await fetch('/NIROB', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, password })
            });
            const data = await response.json();
            showResult(data.success, data.message, data);
        } catch (error) {
            showResult(false, 'Network error. Please try again.', {});
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = 'GENERATE JWT';
            loader.classList.remove('show');
        }
    }
    
    function showResult(success, message, data) {
        const resultBox = document.getElementById('resultBox');
        const statusIcon = document.getElementById('statusIcon');
        const statusText = document.getElementById('statusText');
        
        statusIcon.innerHTML = success ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>';
        statusText.textContent = message;
        statusText.className = 'status-text ' + (success ? 'success' : 'error');
        
        document.getElementById('resultUid').textContent = data.uid || '-';
        document.getElementById('resultAccountUid').textContent = data.account_uid || '-';
        document.getElementById('resultRegion').textContent = data.region || '-';
        document.getElementById('resultToken').textContent = data.jwt_token || '-';
        
        resultBox.classList.add('show');
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function copyToken() {
        const token = document.getElementById('resultToken').textContent;
        if (token && token !== '-') {
            navigator.clipboard.writeText(token).then(() => {
                const btn = event.target.closest('.copy-btn');
                btn.textContent = 'COPIED!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'COPY TOKEN';
                    btn.classList.remove('copied');
                }, 2000);
            });
        }
    }
    
    function copyAll() {
        const uid = document.getElementById('resultUid').textContent;
        const accountUid = document.getElementById('resultAccountUid').textContent;
        const region = document.getElementById('resultRegion').textContent;
        const token = document.getElementById('resultToken').textContent;
        if (token && token !== '-') {
            const text = `UID: ${uid}\\nAccount UID: ${accountUid}\\nRegion: ${region}\\nJWT Token: ${token}`;
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.target.closest('.copy-btn');
                btn.textContent = 'COPIED!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'COPY ALL';
                    btn.classList.remove('copied');
                }, 2000);
            });
        }
    }
</script>
</body>
</html>'''


# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/NIROB', methods=['GET', 'POST'])
def nirob():
    if request.method == 'GET':
        uid = request.args.get('uid', '').strip()
        password = request.args.get('password', '').strip()
    else:
        data = request.get_json(silent=True) or {}
        uid = str(data.get('uid', '')).strip()
        password = str(data.get('password', '')).strip()

    if not uid or not password:
        response = {'success': False, 'message': 'UID and Password are required.'}
    else:
        response = generate_jwt(uid, password)

    resp = jsonify(response)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api', methods=['GET', 'POST'])
def api():
    if request.method == 'GET':
        uid = request.args.get('uid', '').strip()
        password = request.args.get('password', '').strip()
    else:
        data = request.get_json(silent=True) or {}
        uid = str(data.get('uid', '')).strip()
        password = str(data.get('password', '')).strip()

    if not uid or not password:
        response = {'success': False, 'message': 'UID and Password are required.'}
    else:
        response = generate_jwt(uid, password)

    resp = jsonify(response)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# ==================== LOCAL RUN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
