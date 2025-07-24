def detectar_expressoes(landmarks, calibrador, right_hand=None, left_hand=None):
    if not calibrador.calibrado():
        return []

    expressoes_detectadas = []
    lm = landmarks.landmark

    regioes_labios = [0, 13, 14]

    def bloqueado(hand):
        for i in regioes_labios:
            for ponto in hand:
                if abs(ponto.x - lm[i].x) < 0.07 and abs(ponto.y - lm[i].y) < 0.07:
                    return True
        return False

    bloqueado_labios = (
        (right_hand and bloqueado(right_hand)) or
        (left_hand and bloqueado(left_hand))
    )

    if not bloqueado_labios:
        labios_comprimidos = abs(lm[0].y - ((lm[13].y + lm[14].y) / 2)) < 0.012
        if labios_comprimidos:
            expressoes_detectadas.append("Lábios comprimidos")

    return expressoes_detectadas
