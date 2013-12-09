/***************************************************************************************************
 *
 * Display the OpenGL implementation version.
 *
 * This code comes from Mesa 3D glxinfo.c
 *
 ***************************************************************************************************/

/*
 * Copyright (C) 1999-2006  Brian Paul   All Rights Reserved.
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * BRIAN PAUL BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
 * AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <assert.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <GL/gl.h>
#include <GL/glx.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define ELEMENTS(array) (sizeof(array) / sizeof(array[0]))

/** list of known OpenGL versions */
static const struct
{
  int major, minor;
} gl_versions[] =
{
  {1, 0},
  {1, 1},
  {1, 2},
  {1, 3},
  {1, 4},
  {1, 5},
  {2, 0},
  {2, 1},
  {3, 0},
  {3, 1},
  {3, 2},
  {3, 3},
  {4, 0},
  {4, 1},
  {4, 2},
  {4, 3},
  {4, 4},
  {0, 0} /* end of list */
};

#define NUM_GL_VERSIONS ELEMENTS(gl_versions)


/**
 * GL Error checking/warning.
 */
static void
CheckError (int line)
{
  int n;
  n = glGetError ();
  if (n)
    printf ("Warning: GL error 0x%x at line %d\n", n, line);
}


/** Is extension 'ext' supported? */
static int
extension_supported (const char *ext, const char *extensionsList)
{
  const char *p = strstr (extensionsList, ext);
  if (p)
    {
      /* check that next char is a space or end of string */
      int extLen = strlen (ext);
      if (p[extLen] == 0 || p[extLen] == ' ')
	return 1;
    }
  return 0;
}


/**
 * Choose a simple FB Config.
 */
static GLXFBConfig *
choose_fb_config (Display * dpy, int scrnum)
{
  int fbAttribSingle[] = {
    GLX_RENDER_TYPE, GLX_RGBA_BIT,
    GLX_RED_SIZE, 1,
    GLX_GREEN_SIZE, 1,
    GLX_BLUE_SIZE, 1,
    GLX_DOUBLEBUFFER, False,
    None
  };

  int fbAttribDouble[] = {
    GLX_RENDER_TYPE, GLX_RGBA_BIT,
    GLX_RED_SIZE, 1,
    GLX_GREEN_SIZE, 1,
    GLX_BLUE_SIZE, 1,
    GLX_DOUBLEBUFFER, True,
    None
  };

  GLXFBConfig *configs;
  int nConfigs;

  configs = glXChooseFBConfig (dpy, scrnum, fbAttribSingle, &nConfigs);
  if (!configs)
    configs = glXChooseFBConfig (dpy, scrnum, fbAttribDouble, &nConfigs);

  return configs;
}


static Bool CreateContextErrorFlag;

static int
create_context_error_handler (Display * dpy, XErrorEvent * error)
{
  (void) dpy;
  (void) error->error_code;
  CreateContextErrorFlag = True;
  return 0;
}


/**
 * Try to create a GLX context of the given version with flags/options.
 * Note: A version number is required in order to get a core profile
 * (at least w/ NVIDIA).
 */
static GLXContext
create_context_flags (Display * dpy, GLXFBConfig fbconfig, int major, int minor,
		      int contextFlags, int profileMask, Bool direct)
{
#ifdef GLX_ARB_create_context
  static PFNGLXCREATECONTEXTATTRIBSARBPROC glXCreateContextAttribsARB_func = 0;
  static Bool firstCall = True;
  int (*old_handler) (Display *, XErrorEvent *);
  GLXContext context;
  int attribs[20];
  int n = 0;

  if (firstCall)
    {
      /* See if we have GLX_ARB_create_context_profile and get pointer to
       * glXCreateContextAttribsARB() function.
       */
      const char *glxExt = glXQueryExtensionsString (dpy, 0);
      if (extension_supported ("GLX_ARB_create_context_profile", glxExt))
	{
	  glXCreateContextAttribsARB_func = (PFNGLXCREATECONTEXTATTRIBSARBPROC)
	    glXGetProcAddress ((const GLubyte *) "glXCreateContextAttribsARB");
	}
      firstCall = False;
    }

  if (!glXCreateContextAttribsARB_func)
    return 0;

  /* setup attribute array */
  if (major)
    {
      attribs[n++] = GLX_CONTEXT_MAJOR_VERSION_ARB;
      attribs[n++] = major;
      attribs[n++] = GLX_CONTEXT_MINOR_VERSION_ARB;
      attribs[n++] = minor;
    }
  if (contextFlags)
    {
      attribs[n++] = GLX_CONTEXT_FLAGS_ARB;
      attribs[n++] = contextFlags;
    }
#ifdef GLX_ARB_create_context_profile
  if (profileMask)
    {
      attribs[n++] = GLX_CONTEXT_PROFILE_MASK_ARB;
      attribs[n++] = profileMask;
    }
#endif
  attribs[n++] = 0;

  /* install X error handler */
  old_handler = XSetErrorHandler (create_context_error_handler);
  CreateContextErrorFlag = False;

  /* try creating context */
  context = glXCreateContextAttribsARB_func (dpy, fbconfig, 0,	/* share_context */
					     direct, attribs);

  /* restore error handler */
  XSetErrorHandler (old_handler);

  if (CreateContextErrorFlag)
    context = 0;

  if (direct)
    if (!glXIsDirect (dpy, context))
      {
	glXDestroyContext (dpy, context);
	return 0;
      }

  return context;
#else
  return 0;
#endif
}


/**
 * Try to create a GLX context of the newest version.
 */
static GLXContext
create_context_with_config (Display * dpy, GLXFBConfig config, Bool coreProfile, Bool direct)
{
  GLXContext ctx = 0;

  if (coreProfile)
    {
      /* Try to create a core profile, starting with the newest version of
       * GL that we're aware of.  If we don't specify the version
       */
      int i;
      for (i = NUM_GL_VERSIONS - 2; i > 0; i--)
	{
	  /* don't bother below GL 3.0 */
	  if (gl_versions[i].major == 3 && gl_versions[i].minor == 0)
	    return 0;
	  printf("Try to create a context for version %u.%u\n", gl_versions[i].major, gl_versions[i].minor);
	  ctx = create_context_flags (dpy, config,
				      gl_versions[i].major,
				      gl_versions[i].minor,
				      0x0, GLX_CONTEXT_CORE_PROFILE_BIT_ARB, direct);
	  if (ctx)
	    {
	      printf("  Context created\n"); // We know the version at this point
	      return ctx;
	    }
	}
      /* couldn't get core profile context */
      return 0;
    }

  /* GLX should return a context of the latest GL version that supports
   * the full profile.
   */
  ctx = glXCreateNewContext (dpy, config, GLX_RGBA_TYPE, NULL, direct);

  /* make sure the context is direct, if direct was requested */
  if (ctx && direct)
    if (!glXIsDirect (dpy, ctx))
      {
	glXDestroyContext (dpy, ctx);
	return 0;
      }

  return ctx;
}


static Bool
print_version (Display * dpy, int scrnum, Bool allowDirect, Bool coreProfile)
{
  Window win;
  XSetWindowAttributes attr;
  unsigned long mask;
  Window root;
  GLXContext ctx = NULL;
  XVisualInfo *visinfo = NULL;
  int width = 100, height = 100;
  GLXFBConfig *fbconfigs;
  const char *oglstring = coreProfile ? "OpenGL core profile" : "OpenGL";

  root = RootWindow (dpy, scrnum);

  /*
   * Choose FBConfig or XVisualInfo and create a context.
   */
  fbconfigs = choose_fb_config (dpy, scrnum);
  if (fbconfigs)
    {
      // coreProfile = False;
      ctx = create_context_with_config (dpy, fbconfigs[0], coreProfile, allowDirect);
      // We can know the version at this point
      visinfo = glXGetVisualFromFBConfig (dpy, fbconfigs[0]);
      XFree (fbconfigs);
    }

  if (!visinfo)
    {
      fprintf (stderr, "Error: couldn't find RGB GLX visual or fbconfig\n");
      return False;
    }

  if (!ctx)
    {
      if (!coreProfile)
	fprintf (stderr, "Error: glXCreateContext failed\n");
      XFree (visinfo);
      return False;
    }

  /*
   * Create a window so that we can just bind the context.
   */
  attr.background_pixel = 0;
  attr.border_pixel = 0;
  attr.colormap = XCreateColormap (dpy, root, visinfo->visual, AllocNone);
  attr.event_mask = StructureNotifyMask | ExposureMask;
  mask = CWBackPixel | CWBorderPixel | CWColormap | CWEventMask;
  win = XCreateWindow (dpy, root, 0, 0, width, height, 0, visinfo->depth, InputOutput, visinfo->visual, mask, &attr);

  if (glXMakeCurrent (dpy, win, ctx))
    {
      const char *glVersion = (const char *) glGetString (GL_VERSION);
      CheckError (__LINE__);
      printf ("%s version string: %s\n", oglstring, glVersion);
    }
  else
    fprintf (stderr, "Error: glXMakeCurrent failed\n");

  glXDestroyContext (dpy, ctx);
  XFree (visinfo);
  XDestroyWindow (dpy, win);
  XSync (dpy, 1);

  return True;
}


int
main (int argc, char *argv[])
{
  char *displayName = NULL;
  Display *dpy;
  dpy = XOpenDisplay (displayName);
  if (!dpy)
    {
      fprintf (stderr, "Error: unable to open display %s\n", XDisplayName (displayName));
      return -1;
    }

  int scrnum = 0;
  Bool allowDirect = True;
  Bool Coreprofile = True;
  print_version (dpy, scrnum, allowDirect, Coreprofile);

  XCloseDisplay (dpy);

  return 0;
}

/***************************************************************************************************
 *
 * End
 *
 ***************************************************************************************************/
