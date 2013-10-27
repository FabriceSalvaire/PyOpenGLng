/* *********************************************************************************************** */

// #shader_type fragment

#version 300 es

/* *********************************************************************************************** */

// #version 150 required for using interface blocks
in vec4 vertex_colour;

/* *********************************************************************************************** */

out vec4 fragment_colour;

/* *********************************************************************************************** */

void main()
{
  fragment_colour = vertex_colour;
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
