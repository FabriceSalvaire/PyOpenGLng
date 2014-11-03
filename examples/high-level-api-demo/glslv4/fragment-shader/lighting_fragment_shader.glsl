/* *********************************************************************************************** */

// #shader_type fragment

#version 400

/* *********************************************************************************************** */

in VertexAttributes
{
  // vec3 front_colour;
  // vec3 back_colour;
  vec3 transformed_normal;
  vec4 eye_coordinates;
} vertex;

/* *********************************************************************************************** */

layout( location = 0 ) out vec4 fragment_colour;

/* *********************************************************************************************** */

struct LightInfo {
  vec4 Position; // Light position in eye coordinates
  vec3 La; // Ambient light intensity
  vec3 Ld; // Diffuse light intensity
  vec3 Ls; // Specular light intensity
};

struct MaterialInfo {
  vec3 Ka; // Ambient reflectivity
  vec3 Kd; // Diffuse reflectivity
  vec3 Ks; // Specular reflectivity
  float Shininess; // Specular shininess factor
};

uniform LightInfo light = LightInfo(vec4(10, 10, 10, 1),
				    vec3(1, 0, 0),
				    vec3(1, 0, 0),
				    vec3(1, 0, 0));

uniform MaterialInfo material = MaterialInfo(vec3(.25),
					     vec3(.5),
					     vec3(.0),
					     .1);

/* *********************************************************************************************** */

vec3
phong_model(vec4 position, vec3 normal)
{
  vec3 s = normalize(vec3(light.Position - position)); // incident light vector
  vec3 r = reflect(-s, normal); // reflected light vector
  vec3 v = normalize(-position.xyz); // camera vector (in eye coordinates the viewer is at the origin)

  // if the flux is negative then the incoming light is coming from inside the surface.
  float flux = max(dot(s, normal), 0.);

  vec3 ambient = light.La * material.Ka;
  vec3 diffuse = light.Ld * material.Kd * flux;
  vec3 specular = vec3(0.);
  if (flux > 0.)
    {
      float specular_flux = max(dot(r, v), 0.);
      specular = light.Ls * material.Ks * pow(specular_flux, material.Shininess);
    }

  return ambient + diffuse + specular;
}

/* *********************************************************************************************** */

void main()
{
  /*
  if (gl_FrontFacing)
    fragment_colour = vec4(vertex.front_colour, 1.);
  else
    fragment_colour = vec4(vertex.back_colour, 1.);
  */

  // fragment_colour = vec4(vertex.front_colour, 1.);

  vec3 colour = phong_model(vertex.eye_coordinates, vertex.transformed_normal);
  fragment_colour = vec4(colour, 1.);
}

/* *********************************************************************************************** *
 *
 * End
 *
 * *********************************************************************************************** */
