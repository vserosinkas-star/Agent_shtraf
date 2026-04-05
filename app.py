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
            return jsonify({'error': 'Нет валидных записей (проверьте колонки: plate, sts, brand)'}), 400

        # Вставка в Supabase
        result = supabase.table('cars').insert(records).execute()
        return jsonify({'success': True, 'count': len(result.data)}), 200

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['POST'])
def add_single_vehicle():
    try:
        data = request.get_json()
        plate = str(data.get('plate', '')).strip().upper()
        sts = str(data.get('sts', '')).strip().upper()
        brand = str(data.get('brand', '')).strip()

        if not all([plate, sts, brand]):
            return jsonify({'error': 'Заполните все поля'}), 400

        result = supabase.table('cars').insert({
            'plate_number': plate,
            'sts_number': sts,
            'brand': brand
        }).execute()
        return jsonify({'success': True}), 201

    except Exception as e:
        print(f"❌ Ошибка добавления: {e}")
        return jsonify({'error': str(e)}), 500
