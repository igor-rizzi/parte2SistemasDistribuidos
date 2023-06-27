import requests
import json
from serialize import custom_jsonify
from flask import Flask, request, jsonify

# Carregar as informações do arquivo JSON
with open('vizinhos.json') as file:
    data = json.load(file)

# Configurações do servidor
ID = data['id']  # ID do servidor atual
PORT = data['port']  # Porta do servidor atual
VIZINHOS = data['vizinhos']  # Vizinhos do servidor atual

# Dicionário para armazenar os vizinhos visitados
vizinhos_visitados = {}

# Endpoint do servidor para receber as requisições
app = Flask(__name__)

@app.route('/objeto', methods=['GET'])
def get_objeto():
    objeto_id = request.args.get('_id')
    objeto = buscar_objeto_localmente(objeto_id)

    if objeto:
        return custom_jsonify(objeto)

    # Se o objeto não estiver disponível localmente, encaminhar a solicitação para os vizinhos
    if not vizinhos_visitados:
        vizinhos_visitados[ID] = True

    fila_vizinhos = []

    # Adicionar os vizinhos iniciais à fila
    for vizinho in VIZINHOS:
        vizinho_id = vizinho['id']
        if vizinho_id not in vizinhos_visitados:
            fila_vizinhos.append(vizinho_id)

    while fila_vizinhos:
        vizinho_id = fila_vizinhos.pop(0)

        # Marcar o vizinho como visitado
        vizinhos_visitados[vizinho_id] = True

        # Fazer a solicitação HTTP para o vizinho
        vizinho_port = get_vizinho_port(vizinho_id)
        response = requests.get(f"http://localhost:{vizinho_port}/objeto?_id={objeto_id}")

        # Verificar se o objeto foi encontrado no vizinho
        if response.status_code == 200:
            return response.json()

        # Adicionar os vizinhos do vizinho atual à fila
        for vizinho in VIZINHOS:
            vizinho_id = vizinho['id']
            if vizinho_id not in vizinhos_visitados:
                fila_vizinhos.append(vizinho_id)

    # Se nenhum vizinho possuir o objeto, retornar uma resposta de objeto não encontrado
    return jsonify({'message': 'Objeto não encontrado'})

# Função para obter a porta do vizinho com base no ID
def get_vizinho_port(vizinho_id):
    for vizinho in VIZINHOS:
        if vizinho['id'] == vizinho_id:
            return vizinho['port']

    return None


from pymongo import MongoClient
# Função para buscar o objeto localmente no banco de dados
def buscar_objeto_localmente(objeto_id):
    client = MongoClient(data["mongo_uri"])
    db = client[data["database"]]
    collection = db["listingsAndReviews"]
    resultado = collection.find_one({"_id": objeto_id})
    client.close()
    return resultado



if __name__ == '__main__':
    app.run(port=PORT)