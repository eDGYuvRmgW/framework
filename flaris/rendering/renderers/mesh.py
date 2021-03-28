"""Implements rendering meshes."""
from typing import List

import ctypes
import numpy as np
import OpenGL.GL as gl
import glm

from flaris.transform import Transform

from ..mesh import Mesh
from flaris.rendering.camera import Camera
from flaris.rendering.shader import Shader

__all__ = ["MeshRenderer"]

DEFAULT_VERTEX_SHADER = """
    #version 410 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aNormal;

    out vec3 Normal;

    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;

    void main()
    {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
        Normal = aNormal;
    }
"""

DEFAULT_FRAGMENT_SHADER = """
    #version 410 core
    out vec4 FragColor;

    in vec3 Normal;  

    void main()
    {
        FragColor = vec4(abs(Normal), 1.0);
    } 
"""

DEFAULT_MESH_SHADER = Shader.compile(vertex=DEFAULT_VERTEX_SHADER,
                                     fragment=DEFAULT_FRAGMENT_SHADER)


class MeshRenderer:  # pylint: disable=too-few-public-methods
    """A renderer for drawing meshes on the screen."""

    def __init__(self, camera: Camera, shader: Shader = DEFAULT_MESH_SHADER):
        """Initialize OpenGL buffer data."""
        self.camera = camera
        self.shader = shader

        vertices = np.array([
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.5, 0.5, -0.5, 0.0, 0.0, -1.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, -0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.5,
            0.5, 0.5, 0.0, 0.0, 1.0, 0.5, 0.5, 0.5, 0.0, 0.0, 1.0, -0.5, 0.5,
            0.5, 0.0, 0.0, 1.0, -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, -0.5, 0.5, 0.5,
            -1.0, 0.0, 0.0, -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, -0.5, -0.5, -0.5,
            -1.0, 0.0, 0.0, -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, -0.5, -0.5, 0.5,
            -1.0, 0.0, 0.0, -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0,
            0.0, 0.0, 0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.5, -0.5, -0.5, 1.0, 0.0,
            0.0, 0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.5,
            -0.5, -0.5, 0.0, -1.0, 0.0, 0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.5,
            -0.5, 0.5, 0.0, -1.0, 0.0, -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, -0.5,
            -0.5, -0.5, 0.0, -1.0, 0.0, -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.5,
            0.5, -0.5, 0.0, 1.0, 0.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.5, 0.5,
            0.5, 0.0, 1.0, 0.0, -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, -0.5, 0.5, -0.5,
            0.0, 1.0, 0.0
        ],
                            dtype=np.float32)

        self.vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices,
                        gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 24,
                                 ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 24,
                                 ctypes.c_void_p(12))
        gl.glEnableVertexAttribArray(1)

    def draw(self, mesh: Mesh, transform: Transform) -> None:
        """Draw a mesh on the screen.

        Args:
            transform: The position, rotation, and scale of the mesh.
            lights: A list of lights in the current scene.
        """
        gl.glUseProgram(self.shader.program)
        gl.glBindVertexArray(self.vao)

        model = glm.mat4(1.0)
        model = glm.translate(
            model,
            glm.vec3(transform.position.x, transform.position.y,
                     transform.position.z))

        model = glm.rotate(model, glm.radians(transform.rotation.x),
                           glm.vec3(1.0, 0.0, 0.0))
        model = glm.rotate(model, glm.radians(transform.rotation.y),
                           glm.vec3(0.0, 1.0, 0.0))
        model = glm.rotate(model, glm.radians(transform.rotation.z),
                           glm.vec3(0.0, 0.0, 1.0))

        model = glm.scale(
            model,
            glm.vec3(transform.scale.x, transform.scale.y, transform.scale.z))

        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader.program, "model"), 1,
            gl.GL_FALSE, glm.value_ptr(model))
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader.program, "view"), 1,
            gl.GL_FALSE, glm.value_ptr(self.camera.view))
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader.program, "projection"), 1,
            gl.GL_FALSE, glm.value_ptr(self.camera.projection))

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)
