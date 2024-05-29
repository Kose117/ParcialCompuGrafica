import numpy as np


class Pelota:
    def __init__(self, radio, posicion, velocidad):
        self.radio = radio
        self.posicion = np.array(posicion, dtype=np.float32)
        self.velocidad = np.array(velocidad, dtype=np.float32)

    def mover(self):
        self.posicion += self.velocidad

    def verificar_colision_con_paredes(self, caja):
        limites_caja = [(-2, 2), (-2, 2), (-2, 2)]
        for i in range(3):
            if self.posicion[i] - self.radio < limites_caja[i][0]:
                self.posicion[i] = limites_caja[i][0] + self.radio
                self.velocidad[i] *= -1
            if self.posicion[i] + self.radio > limites_caja[i][1]:
                self.posicion[i] = limites_caja[i][1] - self.radio
                self.velocidad[i] *= -1

    def verificar_colision_con_otra_pelota(self, otra):
        distancia = np.linalg.norm(self.posicion - otra.posicion)
        if distancia < self.radio + otra.radio:
            n = (self.posicion - otra.posicion) / distancia
            v_relativa = self.velocidad - otra.velocidad
            v_normal = np.dot(v_relativa, n) * n
            self.velocidad -= v_normal
            otra.velocidad += v_normal
