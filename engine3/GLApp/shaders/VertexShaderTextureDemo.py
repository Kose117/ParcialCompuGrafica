# archivo_principal.py
import numpy as np
import pygame
from OpenGL.GL import *
from GLApp.BaseApps.BaseScene import BaseScene
from GLApp.Camera.Camera import Camera
from GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from GLApp.Transformations.Transformations import identity_mat, scale, translate
from GLApp.Utils.Utils import create_program
from pelota import Pelota  

vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertexColor;
in vec3 vertexNormal;
in vec2 vertexUv;

uniform mat4 projectionMatrix;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;

out vec3 color;
out vec3 normal;
out vec3 fragPos;
out vec3 lightPos;
out vec3 viewPos;
out vec2 uv;
void main()
{
    lightPos = vec3(0, 0, 0);
    viewPos = vec3(inverse(modelMatrix) * vec4(viewMatrix[3][0], viewMatrix[3][1], viewMatrix[3][2], 1));
    gl_Position = projectionMatrix * inverse(viewMatrix) * modelMatrix * vec4(position, 1);
    normal = mat3(transpose(inverse(modelMatrix))) * vertexNormal;
    fragPos = vec3(modelMatrix * vec4(position, 1));
    color = vertexColor;
    uv = vertexUv;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 color;
in vec3 normal;
in vec3 fragPos;
in vec3 lightPos;
in vec3 viewPos;

in vec2 uv;
uniform sampler2D tex;

out vec4 fragColor;

void main(){

    vec3 lightColor = vec3(1, 1, 1);

    //ambient
    float a_strength = 0.1;
    vec3 ambient = a_strength * lightColor;

    //diffuse
    vec3 norm = normalize(normal);
    vec3 lightDirection = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDirection), 0);
    vec3 diffuse = diff * lightColor;

    //specular
    float s_strength = 0.8;
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = normalize(-lightDirection - norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = s_strength * spec * lightColor;

    fragColor = vec4(color * (ambient + diffuse + specular), 1);
    fragColor = fragColor * texture(tex, uv);
}
'''

class VertexShaderCameraDemo(BaseScene):

    def __init__(self, num_pelotas):
        super().__init__(1600, 800)
        self.vao_ref = None
        self.program_id = None
        self.ejes = None
        self.caja = None
        self.pelota_mesh = None
        self.pelotas = []
        self.num_pelotas = num_pelotas
        self.inicializar_pelotas()

    def initialize(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        self.caja = ObjTextureMesh(
            self.program_id,
            "../../assets/models/cube.obj",  
            "../../assets/textures/crate.png"  
        )
        self.pelota_mesh = ObjTextureMesh(
            self.program_id,
            "../../assets/models/Pelota.obj",
            "../../assets/textures/texturaPelota.jpg"
        )
        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())
        glEnable(GL_DEPTH_TEST)

    def inicializar_pelotas(self):
        def hay_solapamiento(pos, radio, pelotas):
            for pelota in pelotas:
                if np.linalg.norm(pos - pelota.posicion) < (radio + pelota.radio):
                    return True
            return False

        for _ in range(self.num_pelotas):
            while True:
                radio = np.random.uniform(0.1, 0.3)
                posicion = np.array([np.random.uniform(-1 + radio, 1 - radio),
                                     np.random.uniform(-1 + radio, 1 - radio),
                                     np.random.uniform(-1 + radio, 1 - radio)])
                if not hay_solapamiento(posicion, radio, self.pelotas):
                    break
            velocidad = np.array([np.random.uniform(-0.01, 0.01),
                                  np.random.uniform(-0.01, 0.01),
                                  np.random.uniform(-0.01, 0.01)])
            pelota = Pelota(radio, posicion, velocidad)
            self.pelotas.append(pelota)

    def dibujar_ejes(self):
        glBegin(GL_LINES)

        # Eje X (rojo)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-1000.0, 0.0, 0.0)
        glVertex3f(1000.0, 0.0, 0.0)

        # Eje Y (verde)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, -1000.0, 0.0)
        glVertex3f(0.0, 1000.0, 0.0)

        # Eje Z (azul)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, -1000.0)
        glVertex3f(0.0, 0.0, 1000.0)

        glEnd()

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        transformation = identity_mat()

        # Dibujar la caja
        caja_transformation = translate(identity_mat(), 0, 0, 0)
        caja_transformation = scale(caja_transformation, 4, 4, 4)
        self.caja.draw(caja_transformation)

        # Dibujar los ejes
        self.dibujar_ejes()

        # Dibujar las pelotas
        for i, pelota in enumerate(self.pelotas):
            pelota.mover()
            pelota.verificar_colision_con_paredes(self.caja)
            for j in range(i + 1, len(self.pelotas)):
                pelota.verificar_colision_con_otra_pelota(self.pelotas[j])
            pelota_transformation = translate(identity_mat(), *pelota.posicion)
            pelota_transformation = scale(pelota_transformation, pelota.radio, pelota.radio, pelota.radio)
            self.pelota_mesh.draw(pelota_transformation)


if __name__ == '__main__':
    num_pelotas = int(input("Ingrese el número de pelotas: "))
    VertexShaderCameraDemo(num_pelotas).main_loop()
