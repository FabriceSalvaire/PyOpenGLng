import PyOpenGLng.Wrapper as Wrapper

# Use 'check_api_number' set to False since we don't have an OpenGL context here
GL = Wrapper.init(api_number='3.0', check_api_number=False)

GL.glViewport.manual()
GL.glViewport.help()
