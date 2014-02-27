/* *********************************************************************************************** */

// #shader_type geometry

#version 330
#extension GL_EXT_geometry_shader4 : enable

/* *********************************************************************************************** */

#include(../include/model_view_projection_matrix.glsl)

/* *********************************************************************************************** */

uniform float line_width = .1;
uniform float stipple_factor = .1;

/* *********************************************************************************************** */

layout(lines) in;
layout(triangle_strip, max_vertices=4) out;

/* *********************************************************************************************** */

in VertexAttributesIn
{
  vec2 position;
  vec4 colour;
} vertexIn[];

/* *********************************************************************************************** */

out VertexAttributes
{
  vec4 colour;
  float stipple_position;
} vertex;

/* *********************************************************************************************** */

void emit_vertex(vec2 position)
{
  gl_Position =  model_view_projection_matrix * vec4(position, 0, 1);
  EmitVertex();
}

/* *********************************************************************************************** */

void main()
{
  vertex.colour = vertexIn[0].colour;

  vec2 pos0 = vertexIn[0].position;
  vec2 pos1 = vertexIn[1].position;

  vec2 dir = normalize(pos1 - pos0);
  vec2 normal = vec2(-dir.y, dir.x);
  vec2 offset = normal * line_width * viewport_scale;

  float segmentLength = length((pos1 - pos0) * inverse_viewport_scale);
  float stipple_position0 = 0;
  float stipple_position1 = segmentLength / (stipple_factor * 16);

  vertex.stipple_position = stipple_position0;
  emit_vertex(pos0 + offset);
  vertex.stipple_position = stipple_position1;
  emit_vertex(pos1 + offset);
  vertex.stipple_position = stipple_position0;
  emit_vertex(pos0 - offset);
  vertex.stipple_position = stipple_position1;
  emit_vertex(pos1 - offset);
  EndPrimitive();
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
