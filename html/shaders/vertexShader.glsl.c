#version 300 es

// an attribute is an input (in) to a vertex shader.
// It will receive data from a buffer
in vec4 a_position;
in vec4 a_color;
in float a_temp;

uniform mat4 u_transform;

out vec4 v_color;
out float v_temp;

// all shaders have a main function
void main() {

  // gl_Position is a special variable a vertex shader
  // is responsible for setting
  gl_Position = u_transform * a_position;
  /* gl_Position = a_position; */

  v_color = a_color;
  v_temp = a_temp;
}
