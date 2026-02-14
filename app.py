from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuração
DATABASE = 'rifa.db'
SENHA_ADMIN = 'admin123'  # MUDE ISSO!

# Animais do Jogo do Bicho
ANIMAIS = {
    1: '🦩', 2: '🦩', 3: '🦩', 4: '🦩',
    5: '🦅', 6: '🦅', 7: '🦅', 8: '🦅',
    9: '🐎', 10: '🐎', 11: '🐎', 12: '🐎',
    13: '🦋', 14: '🦋', 15: '🦋', 16: '🦋',
    17: '🐕', 18: '🐕', 19: '🐕', 20: '🐕',
    21: '🐐', 22: '🐐', 23: '🐐', 24: '🐐',
    25: '🐏', 26: '🐏', 27: '🐏', 28: '🐏',
    29: '🐫', 30: '🐫', 31: '🐫', 32: '🐫',
    33: '🐍', 34: '🐍', 35: '🐍', 36: '🐍',
    37: '🐇', 38: '🐇', 39: '🐇', 40: '🐇',
    41: '🐴', 42: '🐴', 43: '🐴', 44: '🐴',
    45: '🐘', 46: '🐘', 47: '🐘', 48: '🐘',
    49: '🐓', 50: '🐓', 51: '🐓', 52: '🐓',
    53: '🐈', 54: '🐈', 55: '🐈', 56: '🐈',
    57: '🐊', 58: '🐊', 59: '🐊', 60: '🐊',
    61: '🦁', 62: '🦁', 63: '🦁', 64: '🦁',
    65: '🐒', 66: '🐒', 67: '🐒', 68: '🐒',
    69: '🐖', 70: '🐖', 71: '🐖', 72: '🐖',
    73: '🦚', 74: '🦚', 75: '🦚', 76: '🦚',
    77: '🦃', 78: '🦃', 79: '🦃', 80: '🦃',
    81: '🐃', 82: '🐃', 83: '🐃', 84: '🐃',
    85: '🐯', 86: '🐯', 87: '🐯', 88: '🐯',
    89: '🐻', 90: '🐻', 91: '🐻', 92: '🐻',
    93: '🦌', 94: '🦌', 95: '🦌', 96: '🦌',
    97: '🐄', 98: '🐄', 99: '🐄', 0: '🐄'
}

def init_db():
    """Inicializar banco de dados"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS numeros (
            numero INTEGER PRIMARY KEY,
            nome TEXT,
            telefone TEXT,
            pago INTEGER DEFAULT 0,
            data_reserva TEXT,
            data_pagamento TEXT
        )
    ''')
    
    # Inserir números se não existirem
    for i in range(1, 101):
        num = 0 if i == 100 else i
        c.execute('INSERT OR IGNORE INTO numeros (numero) VALUES (?)', (num,))
    
    conn.commit()
    conn.close()

def get_db():
    """Obter conexão com o banco"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rotas da API
@app.route('/')
def index():
    """Página pública"""
    return send_from_directory('static', 'index.html')

@app.route('/admin')
def admin():
    """Painel administrativo"""
    return send_from_directory('static', 'admin.html')

@app.route('/api/numeros', methods=['GET'])
def get_numeros():
    """Obter todos os números"""
    conn = get_db()
    numeros = conn.execute('SELECT * FROM numeros ORDER BY numero').fetchall()
    conn.close()
    
    resultado = []
    for num in numeros:
        resultado.append({
            'numero': num['numero'],
            'nome': num['nome'],
            'telefone': num['telefone'],
            'pago': num['pago'],
            'animal': ANIMAIS.get(num['numero'], '🐄'),
            'data_reserva': num['data_reserva'],
            'data_pagamento': num['data_pagamento']
        })
    
    return jsonify(resultado)

@app.route('/api/reservar', methods=['POST'])
def reservar_numero():
    """Reservar um número"""
    data = request.json
    numero = data.get('numero')
    nome = data.get('nome')
    telefone = data.get('telefone')
    
    if not nome or not telefone:
        return jsonify({'erro': 'Nome e telefone são obrigatórios'}), 400
    
    conn = get_db()
    
    # Verificar se já está reservado
    existente = conn.execute(
        'SELECT nome FROM numeros WHERE numero = ?', 
        (numero,)
    ).fetchone()
    
    if existente and existente['nome']:
        conn.close()
        return jsonify({'erro': 'Este número já foi reservado'}), 400
    
    # Reservar
    conn.execute(
        'UPDATE numeros SET nome = ?, telefone = ?, data_reserva = ? WHERE numero = ?',
        (nome, telefone, datetime.now().isoformat(), numero)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'sucesso': True, 'mensagem': 'Número reservado com sucesso!'})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Login do admin"""
    data = request.json
    senha = data.get('senha')
    
    if senha == SENHA_ADMIN:
        return jsonify({'sucesso': True})
    else:
        return jsonify({'erro': 'Senha incorreta'}), 401

@app.route('/api/admin/marcar-pago', methods=['POST'])
def marcar_pago():
    """Marcar número como pago"""
    data = request.json
    numero = data.get('numero')
    pago = data.get('pago', 1)
    senha = data.get('senha')
    
    if senha != SENHA_ADMIN:
        return jsonify({'erro': 'Não autorizado'}), 401
    
    conn = get_db()
    
    if pago:
        conn.execute(
            'UPDATE numeros SET pago = 1, data_pagamento = ? WHERE numero = ?',
            (datetime.now().isoformat(), numero)
        )
    else:
        conn.execute(
            'UPDATE numeros SET pago = 0, data_pagamento = NULL WHERE numero = ?',
            (numero,)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'sucesso': True})

@app.route('/api/admin/remover', methods=['POST'])
def remover_reserva():
    """Remover reserva"""
    data = request.json
    numero = data.get('numero')
    senha = data.get('senha')
    
    if senha != SENHA_ADMIN:
        return jsonify({'erro': 'Não autorizado'}), 401
    
    conn = get_db()
    conn.execute(
        'UPDATE numeros SET nome = NULL, telefone = NULL, pago = 0, data_reserva = NULL, data_pagamento = NULL WHERE numero = ?',
        (numero,)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'sucesso': True})

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """Obter estatísticas"""
    conn = get_db()
    
    disponiveis = conn.execute('SELECT COUNT(*) as total FROM numeros WHERE nome IS NULL').fetchone()['total']
    vendidos = conn.execute('SELECT COUNT(*) as total FROM numeros WHERE nome IS NOT NULL AND pago = 0').fetchone()['total']
    pagos = conn.execute('SELECT COUNT(*) as total FROM numeros WHERE pago = 1').fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'disponiveis': disponiveis,
        'vendidos': vendidos,
        'pagos': pagos,
        'total': pagos * 100
    })

@app.route('/api/admin/reset', methods=['POST'])
def reset_rifa():
    """Resetar toda a rifa"""
    data = request.json
    senha = data.get('senha')
    
    if senha != SENHA_ADMIN:
        return jsonify({'erro': 'Não autorizado'}), 401
    
    conn = get_db()
    conn.execute('UPDATE numeros SET nome = NULL, telefone = NULL, pago = 0, data_reserva = NULL, data_pagamento = NULL')
    conn.commit()
    conn.close()
    
    return jsonify({'sucesso': True})

if __name__ == '__main__':
    init_db()
    print('=' * 50)
    print('🎲 SERVIDOR DE RIFA INICIADO! 🎲')
    print('=' * 50)
    print('📱 Página Pública: http://localhost:5000')
    print('🔐 Painel Admin: http://localhost:5000/admin')
    print(f'🔑 Senha Admin: {SENHA_ADMIN}')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
