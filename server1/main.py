import requests
import json
from serialize import custom_jsonify

# Carregar as informações do arquivo JSON
with open('vizinhos.json') as file:
    data = json.load(file)

# Configurações do servidor
ID = data['id']  # ID do servidor atual
PORT = data['port']  # Porta do servidor atual
VIZINHOS = data['vizinhos']  # Vizinhos do servidor atual

# Endpoint do servidor para receber as requisições
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/objeto', methods=['GET'])
def get_objeto():
    objeto_id = request.args.get('_id')
    print(objeto_id)
    objeto = buscar_objeto_localmente(objeto_id)

    if objeto:
        return custom_jsonify(objeto)

    # Se o objeto não estiver disponível localmente, encaminhar a solicitação para os vizinhos
    vizinhos_visitados = set()  # Manter o controle dos vizinhos já visitados
    fila_vizinhos = []

    # Adicionar os vizinhos iniciais à fila
    for vizinho in VIZINHOS:
        fila_vizinhos.append((vizinho['id'], vizinho['port'], 0))  # (id, porta, nível)

    while fila_vizinhos:
        vizinho_id, vizinho_port, nivel = fila_vizinhos.pop(0)

        # Verificar se já visitamos esse vizinho anteriormente
        if vizinho_id in vizinhos_visitados:
            continue

        # Marcar o vizinho como visitado
        vizinhos_visitados.add(vizinho_id)

        # Fazer a solicitação HTTP para o vizinho
        response = requests.get(f"http://localhost:{vizinho_port}/objeto?_id={objeto_id}")

        # Verificar se o objeto foi encontrado no vizinho
        if response.status_code == 200:
            return response.json()

        # Adicionar os vizinhos do vizinho atual à fila (apenas se o nível não exceder um limite pré-definido)
        if nivel < 2:
            for vizinho in data['vizinhos']:
                fila_vizinhos.append((vizinho['id'], vizinho['port'], nivel + 1))

    # Se nenhum vizinho possuir o objeto, retornar uma resposta de objeto não encontrado
    return jsonify({'message': 'Objeto não encontrado'})


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