import cv2
import mediapipe as mp
import time
from utils import analisar_maos, media_pontos
from gestos import detectar_gestos, executar_gesto
from calibracao import CalibradorFacial
from expressoes import detectar_expressoes

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

calibrador = CalibradorFacial()
ultimo_status = {"direita": None, "esquerda": None}
tentativas_status = {
    "direita": {"valor": None, "contador": 0, "ultimo_tempo": 0},
    "esquerda": {"valor": None, "contador": 0, "ultimo_tempo": 0}
}

frames_para_confirmar = 3
intervalo_ms = 50

with mp_holistic.Holistic(static_image_mode=False, model_complexity=0, refine_face_landmarks=False) as holistic:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Erro ao acessar a câmera.")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

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
                        print(f"mão {mao} {estado_atual}")
                        tentativa["contador"] = 0
                        tentativa["valor"] = None
                else:
                    tentativa["contador"] = 0
                    tentativa["valor"] = None

            if results.right_hand_landmarks and results.left_hand_landmarks:
                gesto = detectar_gestos(results.right_hand_landmarks.landmark, results.left_hand_landmarks.landmark)
                if gesto:
                    executar_gesto(gesto)

            # Calibração e expressão
            if not calibrador.calibrado():
                calibrador.calibrar(results.face_landmarks)
            else:
                expressoes = detectar_expressoes(
                    results.face_landmarks,
                    calibrador,
                    right_hand=results.right_hand_landmarks.landmark if results.right_hand_landmarks else None,
                    left_hand=results.left_hand_landmarks.landmark if results.left_hand_landmarks else None
                )
                for i, e in enumerate(expressoes):
                    cv2.putText(image, e, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Desenhar landmarks
        if results.face_landmarks:
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION)
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        cv2.imshow("Reconhecimento", image)

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
