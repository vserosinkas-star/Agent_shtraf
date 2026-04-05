import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# 🔗 Подключение к Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    # Получаем автомобили из Supabase
    try:
        response = supabase.table('cars').select('*').order('created_at', desc=True).execute()
        vehicles = response.data  # Список словарей: [{'id': 1, 'plate_number': '...', ...}, ...]
    except Exception as e:
        print(f"❌ Ошибка загрузки авто: {e}")
        vehicles = []

    # Заглушки для штрафов (замените на вашу логику при необходимости)
    fines_unpaid = []
    fines_paid = []
    all_fines = []

    return render_template('index.html',
                           vehicles=vehicles,
                           fines_unpaid=fines_unpaid,
                           fines_paid=fines_paid,
                           all_fines=all_fines)

# ➕ Одиночное добавление
@app.route('/api/vehicles', methods=['POST'])
def add_single_vehicle():
    try:
        data = request.get_json()
        plate = str(data.get('plate', '')).strip().upper()
        sts = str(data.get('sts', '')).strip().upper()
        brand = str(data.get('brand', '')).strip()

        if not all([plate, sts, brand]):
            return jsonify({'error': 'Заполните все обязательные поля'}), 400

        result = supabase.table('cars').insert({
            'plate_number': plate,
            'sts_number': sts,
            'brand': brand
        }).execute()

        return jsonify({'success': True, 'data': result.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📦 Массовый импорт из Excel
@app.route('/api/vehicles/bulk', methods=['POST'])
def bulk_import_vehicles():
    try:
        data = request.get_json()
        vehicles = data.get('vehicles', [])
        if not vehicles:
            return jsonify({'error': 'Пустой список автомобилей'}), 400

        records = []
        for v in vehicles:
            plate = str(v.get('plate', '')).strip().upper()
            sts = str(v.get('sts', '')).strip().upper()
            brand = str(v.get('brand', '')).strip()
            
            if plate and sts and brand:
                records.append({
                    'plate_number': plate,
                    'sts_number': sts,
                    'brand': brand
                })

        if not records:
            return jsonify({'error': 'Нет валидных записей. Проверьте колонки: plate, sts, brand'}), 400

        # Вставка в Supabase (дубли пропустятся благодаря UNIQUE)
        result = supabase.table('cars').insert(records).execute()
        return jsonify({'success': True, 'count': len(result.data)}), 200

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return jsonify({'error': str(e)}), 500

# 🔗 Заглушки для старых ссылок, чтобы не было 404
@app.route('/pay/<int:fine_id>')
def pay_fine(fine_id): return jsonify({'status': 'pending'})

@app.route('/edit/<int:car_id>')
def edit_car(car_id): return jsonify({'status': 'pending'})

@app.route('/history/<int:car_id>')
def car_history(car_id): return jsonify({'status': 'pending'})

@app.route('/delete/<int:car_id>')
def delete_car(car_id): return jsonify({'status': 'pending'})

if __name__ == '__main__':
    app.run(debug=True)
