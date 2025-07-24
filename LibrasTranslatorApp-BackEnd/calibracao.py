class CalibradorFacial:
    def __init__(self):
        self.dados = {}

    def calibrado(self):
        return all(k in self.dados for k in [
            "centro_olhos_y",
            "dist_sobrancelha_direita",
            "dist_sobrancelha_esquerda"
        ])

    def calibrar(self, face_landmarks):
        lm = face_landmarks.landmark
        self.dados["centro_olhos_y"] = (lm[33].y + lm[263].y) / 2
        self.dados["dist_sobrancelha_direita"] = self.dados["centro_olhos_y"] - lm[70].y
        self.dados["dist_sobrancelha_esquerda"] = self.dados["centro_olhos_y"] - lm[63].y
        print("Calibração feita!")

    def get(self, chave):
        return self.dados.get(chave)
