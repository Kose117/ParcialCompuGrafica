import random
from OpenGL.GL import *

from GLApp.Mesh.Light.BaseTextureMesh import BaseTextureMesh

class Mesh:
    def __init__(self):
        self.vertices = []
        self.textures = []
        self.normals = []

def load_mesh(filename, body):
    v = []
    vt = []
    vn = []

    mesh = Mesh()

    with open(filename, "r") as f:
        line = f.readline()
        while line:
            words = line.split(" ")
            if words[0] == "v":
                v.append(read_vertex_data(words))
            elif words[0] == "vt":
                vt.append(read_texcoord_data(words))
            elif words[0] == "vn":
                vn.append(read_normal_data(words, body))
            elif words[0] == "f":
                read_face_data(words, v, vt, vn, mesh)
            line = f.readline()

        print(f'Loaded {len(mesh.vertices)} ')
    return mesh.vertices, mesh.textures, mesh.normals


def read_vertex_data(words):
    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]


def read_texcoord_data(words):
    return [
        float(words[1]),
        float(words[2])
    ]


def read_normal_data(words, body):
    if body == "Box":
        return [
            -float(words[1]),
            -float(words[2]),
            -float(words[3])
        ]
    else:
        return [
            float(words[1]),
            float(words[2]),
            float(words[3])
        ]


def read_face_data(words: str, v, vt, vn, mesh):
    triangleCount = len(words) - 3
    for i in range(triangleCount):
        make_corner(words[1], v, vt, vn, mesh)
        make_corner(words[2 + i], v, vt, vn, mesh)
        make_corner(words[3 + i], v, vt, vn, mesh)


def make_corner(corner_description: str, v, vt, vn, mesh: Mesh):
    v_vt_vn = corner_description.split("/")
    mesh.vertices.append(v[int(v_vt_vn[0]) - 1])
    mesh.textures.append(vt[int(v_vt_vn[1]) - 1])
    mesh.normals.append(vn[int(v_vt_vn[2]) - 1])


class ObjTextureMesh(BaseTextureMesh):
    def __init__(self, program_id, filename, texture_filename):
        vertices, vertex_uvs, vertex_normals = load_mesh(filename, "Box")
        colors = []
        for i in range(len(vertices)):
            colors.append([1, 1, 1])
        draw_type_aux = GL_TRIANGLES
        super().__init__(program_id, vertices, vertex_uvs, vertex_normals, colors, draw_type_aux, texture_filename)
