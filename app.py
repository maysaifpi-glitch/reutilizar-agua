from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Arquivo para armazenar as doações (simulando um banco de dados)
DATABASE_FILE = 'donations.json'

def load_donations():
    """Carrega as doações do arquivo JSON"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_donations(donations):
    """Salva as doações no arquivo JSON"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(donations, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Serve a página principal"""
    return render_template('index.html')

@app.route('/api/donations', methods=['GET'])
def get_donations():
    """Retorna todas as doações"""
    donations = load_donations()
    return jsonify(donations)

@app.route('/api/donations/active', methods=['GET'])
def get_active_donations():
    """Retorna apenas doações ativas (não aprovadas)"""
    donations = load_donations()
    active_donations = [d for d in donations if d['status'] != 'Aprovada']
    return jsonify(active_donations)

@app.route('/api/donations', methods=['POST'])
def create_donation():
    """Cria uma nova doação"""
    try:
        data = request.json
        print("Dados recebidos:", data)  # Para debug
        
        donation = {
            'id': int(datetime.now().timestamp() * 1000),
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'city': data.get('city', ''),
            'address': data.get('address', ''),
            'notes': data.get('notes', ''),
            'materials': data.get('materials', []),
            'quantities': data.get('quantities', []),
            'conditions': data.get('conditions', []),
            'status': 'Pendente',
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'created_at': datetime.now().isoformat()
        }
        
        donations = load_donations()
        donations.append(donation)
        save_donations(donations)
        
        return jsonify({'success': True, 'id': donation['id']})
    
    except Exception as e:
        print("Erro ao criar doação:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/donations/<int:donation_id>', methods=['PUT'])
def update_donation(donation_id):
    """Atualiza o status de uma doação"""
    data = request.json
    new_status = data.get('status')
    
    donations = load_donations()
    
    for donation in donations:
        if donation['id'] == donation_id:
            donation['status'] = new_status
            donation['updated_at'] = datetime.now().isoformat()
            break
    
    save_donations(donations)
    return jsonify({'success': True})

@app.route('/api/donations/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    """Remove uma doação"""
    donations = load_donations()
    donations = [d for d in donations if d['id'] != donation_id]
    save_donations(donations)
    
    return jsonify({'success': True})

@app.route('/api/donors')
def get_donors():
    """Retorna o registro completo de todos os doadores"""
    donations = load_donations()
    return jsonify(donations)

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas das doações"""
    donations = load_donations()
    
    stats = {
        'total': len(donations),
        'pending': len([d for d in donations if d['status'] == 'Pendente']),
        'approved': len([d for d in donations if d['status'] == 'Aprovada']),
        'in_analysis': len([d for d in donations if d['status'] == 'Em análise'])
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)