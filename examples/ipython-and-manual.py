import PyOpenGLng.Wrapper as Wrapper

# Use 'check_api_number' set to False since we don't have an OpenGL context here
GL = Wrapper.init(api_number='3.1', profile='core', check_api_number=False)

#GL.glViewport.manual()
#GL.glViewport.help()
