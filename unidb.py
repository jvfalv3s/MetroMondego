import psycopg2
from flask import Flask, request, jsonify
#import jwt # PyJWT ainda nao usei em nada
#import datetime tambem nao usei, mas pode ser util para expirar tokens depois de um tempo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

def get_db_connection():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="Oxe2urubu2*",
            host="localhost",
            port="5432",
            database="postgres"
        )
        return connection
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

# 1. USER AUTHENTICATION (PUT /dbproj/user)
# Rota para Login
@app.route('/dbproj/user', methods=['PUT'])
def login():
    data = request.get_json()
    print(f"Tentativa de login para: {data.get('username')}")
    email = data.get('username') # O email é o username
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Busca o usuário e sua role
    cur.execute("SELECT id, role FROM app_user WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    
    if user:
        # Simulando um token simples
        token = f"TOKEN_USER_{user[0]}" 
        return jsonify({"status": 200, "errors": None, "results": token}), 200
    
    return jsonify({"status": 400, "errors": "Login falhou", "results": None}), 400

# Ponto 2: Add Administrator (PUT)
@app.route('/dbproj/register/admin', methods=['PUT'])
def register_admin():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Busca o próximo ID disponível manualmente
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM app_user")
        next_id = cur.fetchone()[0]

        # 2. Insere na tabela pai (app_user) usando o next_id, tava dando drama quanto aos ids
        cur.execute(
            "INSERT INTO app_user (id, name, email, password, role) VALUES (%s, %s, %s, %s, 'admin')",
            (next_id, data['name'], data['email'], data['password'])
        )
        
        # 3. Insere na tabela filha (admin) usando o mesmo ID
        cur.execute("INSERT INTO admin (id) VALUES (%s)", (next_id,))
        
        conn.commit()
        return jsonify({"status": 200, "errors": None, "results": {"user_id": next_id}}), 200

    except Exception as e:
        conn.rollback()
        print(f"ERRO DETALHADO: {e}") # Isso ajuda você a ver o erro no terminal
        return jsonify({"status": 500, "errors": str(e), "results": None}), 500
    finally:
        cur.close()
        conn.close()

# Ponto 3: Add Customer (POST)
@app.route('/dbproj/register/customer', methods=['POST'])
def register_customer():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    
    #gambiarra para inserir na tabela app_user e customer ao mesmo tempo, já que o id é o mesmo e não temos SERIAL/Sequence no banco (problema que quero resolver depois)
    try:
        # 1. Calcular o próximo ID manualmente (Já que não usamos SERIAL/Sequence no banco)
        cur.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM "app_user"')
        next_id = cur.fetchone()[0]
        
        # 2. Inserir na tabela pai (app_user) passando o ID calculado
        cur.execute(
            'INSERT INTO "app_user" (id, name, email, password, role) VALUES (%s, %s, %s, %s, %s)',
            (next_id, data['name'], data['email'], data['password'], 'customer')
        )
        
        # 3. Inserir na tabela filha (customer) usando o MESMO ID
        cur.execute(
            'INSERT INTO "customer" (id, nif, phone, wallet_balance, customer_type) VALUES (%s, %s, %s, %s, %s)',
            (next_id, data['nif'], data['phone'], 0.0, 'regular')
        )
        
        conn.commit()
        return jsonify({"status": 200, "errors": None, "results": {"user_id": next_id}}), 200
        
    except Exception as e:
        conn.rollback()
        print("ERRO NO REGISTRO:", e)
        return jsonify({"status": 500, "errors": str(e), "results": None}), 500
    finally:
        cur.close()
        conn.close()
        
#************** todos de joao*****************# 

# validacao antes de chegar na base, diretamente aqui no webserver.

#melhorar a validacao e as mensagens de erros
#implementacao dos tokens jwt

  
#todo: ponto 4: Update	line	operation	settings.	Update	a	given	line	with	new	data

#todo: ponto 5: update fare price

#todo: ponto 6: broadcast notice

#todo: ponto 7: create promotion/discount rule
#*********************************************#


if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
    
#todo: 
#implementar os outros endpoints seguindo a mesma estrutura, e depois pensar em como usar o JWT para autenticação e autorização.
#Lembre-se de fechar as conexões e cursores após cada operação para evitar vazamentos de recursos.
#alterar os nomes dos endpois para seguir o padrao da database, por exemplo /dbproj/register/app_user e nao app_user, e assim por diante.