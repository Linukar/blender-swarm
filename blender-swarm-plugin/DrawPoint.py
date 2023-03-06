import bpy
import gpu
import mathutils

from gpu_extras.batch import batch_for_shader

coordsLine = [(1, 1, 1), (-2, 0, 0), (-2, -1, 3), (0, 1, 1)]
shaderLine = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
batchLine = batch_for_shader(shaderLine, 'LINES', {"pos": coordsLine})


def drawLines():
    shaderLine.bind()
    shaderLine.uniform_float("color", (1, 1, 0, 1))
    batchLine.draw(shaderLine)
    print("drawLine")


vertex_shader = '''
    uniform mat4 viewProjectionMatrix;
    uniform vec3 position;

    in vec3 offset;

    void main()
    {
        gl_Position = viewProjectionMatrix * vec4(position + offset, 1.0f);
    }
'''

fragment_shader = '''
    uniform vec3 color;

    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(color, 1.0);
    }
'''

coords = [(-0.05, 0, 0), (0.05, 0, 0), (0, 0, 0.08)]
shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
batch = batch_for_shader(shader, 'TRIS', {"offset": coords})


def drawPoint(position: mathutils.Vector, color: tuple[float, float, float]):
    shader.bind()
    matrix = gpu.matrix.get_projection_matrix() @ gpu.matrix.get_model_view_matrix()
    shader.uniform_float("viewProjectionMatrix", matrix)
    shader.uniform_float("color", color)
    shader.uniform_float("position", position.to_tuple())
    batch.draw(shader)
