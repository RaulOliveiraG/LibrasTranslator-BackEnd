import webbrowser
from utils import calcular_distancia

def detectar_gestos(right_hand, left_hand):
    if not right_hand or not left_hand:
        return None

    mao_direita = [right_hand[i] for i in [4, 8, 12, 16, 20]]
    mao_esquerda = [left_hand[i] for i in [4, 8, 12, 16, 20]]

    distancias = [calcular_distancia([p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z])
                  for p1, p2 in zip(mao_direita, mao_esquerda)]

    media_dist = sum(distancias) / len(distancias)

    if media_dist < 0.07:
        return "gesto"

    return None

def executar_gesto(gesto_nome):
    if gesto_nome == "gesto!":
        print("gesto")

