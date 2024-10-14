from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# 定义获取 Token 的接口 URL
TOKEN_URL = 'https://token.oaifree.com/api/auth/refresh'

# HTML 模板内容，内嵌在 Python 代码中
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RT 转 AT</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        .center {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 90%; /* 响应式调整 */
            max-width: 400px;
            padding: 30px 20px;
            background: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-radius: 8px;
        }
        h2 { 
            font-size: 24px; 
            margin-bottom: 15px; 
        }
        .input-wrapper {
            position: relative;
            margin-bottom: 20px;
            width: 100%; /* 确保宽度一致 */
        }
        .input-wrapper input {
            width: 100%; 
            height: 45px;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 16px;
            background-color: #f9f9f9;
            box-sizing: border-box;
        }
        .input-wrapper label {
            position: absolute;
            top: 14px;
            left: 14px;
            transition: all 0.3s;
            color: #aaa;
        }
        .input-wrapper input:focus + label,
        .input-wrapper input:not(:placeholder-shown) + label {
            top: -8px;
            left: 12px;
            font-size: 14px;
            color: #0f9977;
        }
        button {
            width: 100%; 
            padding: 15px;
            border: none;
            border-radius: 8px;
            background-color: #0f9977;
            color: white;
            cursor: pointer;
            font-size: 18px;
            margin-top: 10px;
        }
        button:hover { 
            background-color: #0c7b61; 
        }
        #access_token {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            word-wrap: break-word;
            height: 100px; /* 增加高度 */
            font-size: 16px;
            overflow-y: auto;
            box-sizing: border-box;
            width: 100%; /* 与输入框对齐 */
        }
        button[disabled] {
            background-color: #ccc;
            color: #666;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="center">
        <h2>refreshToken 转 AccessToken</h2>
        <div class="input-wrapper">
            <input type="text" id="refresh_token" placeholder=" " required>
            <label for="refresh_token">Refresh Token</label>
        </div>
        <button type="button" onclick="getToken()">获取 Access Token</button>
        <div id="access_token"></div>
        <button id="copy-button" type="button" onclick="copyAccessToken()" disabled>复制 Access Token</button>
        <button id="go-share-token" type="button" onclick="goShareToken()" disabled>分享 Token</button>
    </div>
    <script>
        async function getToken() {
            const refreshToken = document.getElementById('refresh_token').value;
            const accessTokenEl = document.getElementById('access_token');
            const copyButton = document.getElementById('copy-button');
            const goShareTokenEl = document.getElementById('go-share-token');
            accessTokenEl.innerText = '';

            try {
                const response = await fetch('/get_token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ refresh_token: refreshToken })
                });

                const result = await response.json();
                if (response.ok) {
                    accessTokenEl.innerText = result.access_token;
                    copyButton.removeAttribute('disabled');
                    goShareTokenEl.removeAttribute('disabled');
                } else {
                    accessTokenEl.innerText = result.error;
                    copyButton.setAttribute('disabled', 'disabled');
                    goShareTokenEl.setAttribute('disabled', 'disabled');
                }
            } catch (error) {
                accessTokenEl.innerText = '请求失败，请稍后重试';
            }
        }

        function copyAccessToken() {
            const accessToken = document.getElementById('access_token').innerText;
            if (!accessToken) return;

            navigator.clipboard.writeText(accessToken).then(() => {
                alert('Access Token 已复制到剪贴板');
            }).catch(err => {
                alert('复制失败，请手动复制');
            });
        }

        function goShareToken() {
            const accessToken = document.getElementById('access_token').innerText;
            if (!accessToken) {
                alert('请先获取 Access Token');
                return;
            }
            window.open('https://chat.oaifree.com/token', '_blank');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """渲染主页界面。"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_token', methods=['POST'])
def get_token():
    """根据 refresh token 获取 access token。"""
    refresh_token = request.form.get('refresh_token')
    response = requests.post(
        TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
        data={'refresh_token': refresh_token}
    )
    result = response.json()

    if 'access_token' in result:
        return jsonify({'access_token': result['access_token']})
    else:
        error_message = result.get('detail', '获取失败，请检查 Refresh Token 是否正确')
        return jsonify({'error': error_message}), 400

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8080, debug=False)
