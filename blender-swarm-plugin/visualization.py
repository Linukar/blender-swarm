import bpy
import gpu
import mathutils

from gpu_extras.batch import batch_for_shader

shaderLine = gpu.shader.from_builtin('3D_UNIFORM_COLOR')


def drawLine(start: mathutils.Vector, end: mathutils.Vector):
    batchLine = batch_for_shader(shaderLine, 'LINES', {"pos": [start.to_tuple(), end.to_tuple()]})
    shaderLine.bind()
    shaderLine.uniform_float("color", (1, 1, 0, 1))
    batchLine.draw(shaderLine)


vertex_shader = '''
    uniform mat4 projection;
    uniform mat4 model;
    uniform mat4 view;

    in vec3 offset;

    void main()
    {
        gl_Position = projection * view * model * vec4(offset, 1.0f);
    }
'''

fragment_shader = '''
    uniform vec3 color;

    out vec4 FragColor;

    void main()
    {
        float gamma = 0.3;
        FragColor.rgb = pow(color.rgb, vec3(1.0/gamma));
    }
'''

coords = [(0, 0.05, 0), (0, -0.05, 0), (0.3, 0, 0)]
shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
batch = batch_for_shader(shader, 'TRIS', {"offset": coords})
scaleMultiplier = 0.09

def drawTriangle(position: mathutils.Vector, rotation: mathutils.Quaternion, color: tuple[float, float, float]):
    viewMat = gpu.matrix.get_model_view_matrix()
    cameraDistance = viewMat.translation.magnitude
    scale = cameraDistance * scaleMultiplier
    modelMat = mathutils.Matrix.LocRotScale(position, rotation, mathutils.Vector((scale, scale, scale)))

    shader.bind()
    shader.uniform_float("projection", gpu.matrix.get_projection_matrix())
    shader.uniform_float("view", viewMat)

    shader.uniform_float("color", color)
    shader.uniform_float("model", modelMat)
    batch.draw(shader)
