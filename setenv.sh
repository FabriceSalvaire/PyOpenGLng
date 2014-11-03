####################################################################################################

# PyOpenGL > 3.0.1
source ${HOME}/python-virtual-env/standard/bin/activate
append_to_python_path_if_not /usr/local/stow/python2.7/lib/python2.7/site-packages
append_to_python_path_if_not /usr/local/stow/python2.7/lib64/python2.7/site-packages
append_to_python_path_if_not $HOME/pyglfw-cffi
append_to_python_path_if_not ${PWD}

append_to_ld_library_path_if_not /usr/local/stow/freetype-2.5.2/lib

####################################################################################################
# 
# End
# 
####################################################################################################
