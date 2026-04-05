import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# 🔗 Подключение к Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@app.route('/')
def index():
    # Получаем автомобили из Supabase
    try:
        response = supabase.table('cars').select('*').order('created_at', desc=True).execute()
        # Преобразуем словари в кортежи, чтобы ваш шаблон (v[0], v[1]...) работал без изменений
        vehicles = [
            (v['id'], v['plate_number'], v['sts_number'], v['email'], None, v.get('description', ''))
            for v in response.data
        ]
    except Exception as e:
        print(f"❌ Ошибка загрузки авто: {e}")
        vehicles = []

    # Заглушки для штрафов (оставьте вашу логику)
    fines_unpaid = []
    fines_paid = []
    all_fines = []

    return render_template('index.html',
                           vehicles=vehicles,
                           fines_unpaid=fines_unpaid,
                           fines_paid=fines_paid,
                           all_fines=all_fines)

# 📥 Массовый импорт из Excel
@app.route('/api/vehicles/bulk', methods=['POST'])
def bulk_import_vehicles():
    try:
        data = request.get_json()
        if not data or 'vehicles' not in data:
            return jsonify({'error': 'Неверный формат. Ожидается { "vehicles": [...] }'}), 400

        records = []
        for v in data['vehicles']:
            plate = str(v.get('plate', '')).strip().upper()
            sts = str(v.get('sts', '')).strip().upper()
            email = str(v.get('email', '')).strip().lower()
            desc = str(v.get('description', '')).strip()
            
            if plate and sts and email:
                records.append({
                    'plate_number': plate,
                    'sts_number': sts,
                    'email': email,
                    'description': desc
                })

        if not records:
            return jsonify({'error': 'Нет валидных записей для импорта'}), 400

        # Вставка в Supabase (дубли пропустятся благодаря UNIQUE индексу)
        result = supabase.table('cars').insert(records).execute()
        
        return jsonify({
            'success': True,
            'message': f'✅ Добавлено {len(result.data)} авто',
            'count': len(result.data)
        }), 200

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return jsonify({'error': str(e)}), 500

# ➕ Одиночное добавление
@app.route('/api/vehicles', methods=['POST'])
def add_single_vehicle():
    try:
        data = request.get_json()
        plate = str(data.get('plate', '')).strip().upper()
        sts = str(data.get('sts', '')).strip().upper()
        email = str(data.get('email', '')).strip().lower()
        desc = str(data.get('description', '')).strip()

        if not all([plate, sts, email]):
            return jsonify({'error': 'Заполните номер, СТС и email'}), 400

        result = supabase.table('cars').insert({
            'plate_number': plate,
            'sts_number': sts,
            'email': email,
            'description': desc
        }).execute()

        return jsonify({'success': True, 'data': result.data[0]}), 201
    except Exception as e:
        print(f"❌ Ошибка добавления: {e}")
        return jsonify({'error': str(e)}), 500

# Ваши остальные маршруты (/pay, /edit, /history, /delete) остаются без изменений

if __name__ == '__main__':
    app.run(debug=True)