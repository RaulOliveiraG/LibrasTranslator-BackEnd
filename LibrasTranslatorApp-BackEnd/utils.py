import numpy as np

def calcular_distancia(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p2 - p1)

def classificar_distancia(face, hand, limite=0.2, limite_z=0.12):
    xy_dist = np.linalg.norm(np.array(face[:2]) - np.array(hand[:2]))
    z_dist = abs(face[2] - hand[2])
    if z_dist < limite_z:
        return "perto"
    elif xy_dist < limite:
        return "perto"
    else:
        return "longe"

def analisar_maos(face, right_hand=None, left_hand=None, limite=0.2, limite_z=0.12):
    resultados = {}
    if right_hand is not None:
        resultados['direita'] = classificar_distancia(face, right_hand, limite, limite_z)
    if left_hand is not None:
        resultados['esquerda'] = classificar_distancia(face, left_hand, limite, limite_z)
    return resultados

def media_pontos(landmarks, indices):
    pontos = [landmarks[i] for i in indices]
    xs = [p.x for p in pontos]
    ys = [p.y for p in pontos]
    zs = [p.z for p in pontos]
    return [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)]
