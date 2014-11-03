/* *********************************************************************************************** */

// #shader_type vertex

#version 300 es

/* *********************************************************************************************** */

#include(model_view_projection_matrix.glsl)
#include(position_shader_program_interface.glsl)

/* *********************************************************************************************** */

// cannot initialize uniforms in GLSL ES 3.00 (GLSL 1.20 required).
uniform vec3 colour; // = vec3(1, 1, 1);

/* *********************************************************************************************** */

// #version 150 required for using interface blocks.
// GLSL ES 3.0 does not support interface blocks for shader inputs or outputs.
out highp vec4 vertex_colour;

/* *********************************************************************************************** */

void main()
{
  gl_Position = model_view_projection_matrix * vec4(position, 0, 1);
  vertex_colour = vec4(colour, 1);
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
