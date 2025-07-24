from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import base64
import numpy as np
import io
from PIL import Image
import time
from utils import analisar_maos, media_pontos
from gestos import detectar_gestos, executar_gesto
from calibracao import CalibradorFacial
from expressoes import detectar_expressoes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'libras_translator_secret_key'
CORS(app, origins="*")  # Permite requisições de qualquer origem

# Configuração do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuração do MediaPipe
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Variáveis globais para o estado do reconhecimento
calibrador = CalibradorFacial()
ultimo_status = {"direita": None, "esquerda": None}
tentativas_status = {
    "direita": {"valor": None, "contador": 0, "ultimo_tempo": 0},
    "esquerda": {"valor": None, "contador": 0, "ultimo_tempo": 0}
}

frames_para_confirmar = 3
intervalo_ms = 50

def process_image_data(image_data):
    """Processa dados de imagem base64 e retorna frame OpenCV"""
    try:
        # Remove o prefixo data:image/...;base64, se presente
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decodifica base64
        image_bytes = base64.b64decode(image_data)
        
        # Converte para PIL Image
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Converte para array numpy
        frame = np.array(pil_image)
        
        # Converte RGB para BGR (formato OpenCV)
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        return frame
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return None

def process_frame_logic(image_data):
    """Lógica principal de processamento de frame"""
    global ultimo_status, tentativas_status, calibrador
    
    # Processa a imagem
    frame = process_image_data(image_data)
    if frame is None:
        return {"error": "Erro ao processar imagem"}
    
    # Converte para RGB para o MediaPipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Processa com MediaPipe
    with mp_holistic.Holistic(
        static_image_mode=False, 
        model_complexity=0, 
        refine_face_landmarks=False
    ) as holistic:
        results = holistic.process(image)
    
    response_data = {
        "gestos": [],
        "expressoes": [],
        "status_maos": ultimo_status.copy(),
        "landmarks_detectados": {
            "face": results.face_landmarks is not None,
            "mao_direita": results.right_hand_landmarks is not None,
            "mao_esquerda": results.left_hand_landmarks is not None
        }
    }
    
    # Análise das mãos e posições
    if results.face_landmarks:
        lm = results.face_landmarks.landmark
        face_coords = [
            (lm[33].x + lm[263].x) / 2,
            (lm[33].y + lm[263].y) / 2,
            (lm[33].z + lm[263].z) / 2,
        ]
        
        profundidade_rosto = abs(face_coords[2])
        limite_base_xy = 0.25
        limite_base_z = 0.15
        peso_z = min(profundidade_rosto * 4.5, 0.9)
        peso_xy = 1.0 - peso_z
        limite = max(limite_base_xy * peso_xy, 0.05)
        limite_z = max(limite_base_z * peso_z, 0.03)
        
        right_coords = left_coords = None
        if results.right_hand_landmarks:
            right_coords = media_pontos(results.right_hand_landmarks.landmark, [0, 8])
        if results.left_hand_landmarks:
            left_coords = media_pontos(results.left_hand_landmarks.landmark, [0, 8])
        
        estados_atuais = analisar_maos(face_coords, right_coords, left_coords, limite=limite, limite_z=limite_z)
        tempo_atual = time.time() * 1000
        
        # Atualiza status das mãos
        for mao, estado_atual in estados_atuais.items():
            tentativa = tentativas_status[mao]
            
            if estado_atual != ultimo_status[mao]:
                if estado_atual == tentativa["valor"]:
                    if tempo_atual - tentativa["ultimo_tempo"] <= intervalo_ms:
                        tentativa["contador"] += 1
                    else:
                        tentativa["contador"] = 1
                else:
                    tentativa["valor"] = estado_atual
                    tentativa["contador"] = 1
                
                tentativa["ultimo_tempo"] = tempo_atual
                
                if tentativa["contador"] >= frames_para_confirmar:
                    ultimo_status[mao] = estado_atual
                    response_data["status_maos"][mao] = estado_atual
                    tentativa["contador"] = 0
                    tentativa["valor"] = None
            else:
                tentativa["contador"] = 0
                tentativa["valor"] = None
        
        # Detecção de gestos
        if results.right_hand_landmarks and results.left_hand_landmarks:
            gesto = detectar_gestos(results.right_hand_landmarks.landmark, results.left_hand_landmarks.landmark)
            if gesto:
                response_data["gestos"].append(gesto)
        
        # Calibração e detecção de expressões
        if not calibrador.calibrado():
            calibrador.calibrar(results.face_landmarks)
            response_data["calibracao_status"] = "calibrando"
        else:
            response_data["calibracao_status"] = "calibrado"
            expressoes = detectar_expressoes(
                results.face_landmarks,
                calibrador,
                right_hand=results.right_hand_landmarks.landmark if results.right_hand_landmarks else None,
                left_hand=results.left_hand_landmarks.landmark if results.left_hand_landmarks else None
            )
            response_data["expressoes"] = expressoes
    
    return response_data

# Rotas HTTP (mantidas para compatibilidade)
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({"status": "ok", "message": "Servidor LibrasTranslator está funcionando"})

@app.route('/api/process-frame', methods=['POST'])
def process_frame():
    """Processa um frame de imagem para reconhecimento de gestos e expressões"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "Dados de imagem não fornecidos"}), 400
        
        result = process_frame_logic(data['image'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/api/reset-calibration', methods=['POST'])
def reset_calibration():
    """Reseta a calibração facial"""
    global calibrador
    calibrador = CalibradorFacial()
    return jsonify({"message": "Calibração resetada com sucesso"})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retorna o status atual do sistema"""
    return jsonify({
        "calibracao_status": "calibrado" if calibrador.calibrado() else "não calibrado",
        "status_maos": ultimo_status.copy(),
        "servidor": "ativo"
    })

# Eventos WebSocket
@socketio.on('connect')
def handle_connect():
    """Evento de conexão WebSocket"""
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'message': 'Conectado ao servidor LibrasTranslator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Evento de desconexão WebSocket"""
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('process_frame')
def handle_process_frame(data):
    """Processa frame via WebSocket"""
    try:
        if not data or 'image' not in data:
            emit('error', {'message': 'Dados de imagem não fornecidos'})
            return
        
        result = process_frame_logic(data['image'])
        
        if 'error' in result:
            emit('error', result)
        else:
            emit('frame_processed', result)
    
    except Exception as e:
        print(f"Erro no processamento WebSocket: {e}")
        emit('error', {'message': f'Erro interno do servidor: {str(e)}'})

@socketio.on('reset_calibration')
def handle_reset_calibration():
    """Reseta calibração via WebSocket"""
    global calibrador
    calibrador = CalibradorFacial()
    emit('calibration_reset', {'message': 'Calibração resetada com sucesso'})

@socketio.on('get_status')
def handle_get_status():
    """Retorna status via WebSocket"""
    status = {
        "calibracao_status": "calibrado" if calibrador.calibrado() else "não calibrado",
        "status_maos": ultimo_status.copy(),
        "servidor": "ativo"
    }
    emit('status_update', status)

if __name__ == '__main__':
    print("Iniciando servidor LibrasTranslator com WebSocket...")
    print("Servidor rodando em: http://0.0.0.0:5000")
    print("WebSocket disponível em: ws://0.0.0.0:5000")
    print("\nEndpoints HTTP disponíveis:")
    print("  GET  /api/health - Verificação de saúde")
    print("  POST /api/process-frame - Processar frame de imagem")
    print("  POST /api/reset-calibration - Resetar calibração")
    print("  GET  /api/status - Status do sistema")
    print("\nEventos WebSocket disponíveis:")
    print("  connect - Conexão estabelecida")
    print("  process_frame - Processar frame de imagem")
    print("  reset_calibration - Resetar calibração")
    print("  get_status - Obter status do sistema")
    print("  disconnect - Desconexão")
    
    # Executa o servidor com SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)