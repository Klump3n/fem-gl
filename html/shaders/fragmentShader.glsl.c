#version 300 es
#extension GL_OES_standard_derivatives : enable

// fragment shaders don't have a default precision so we need
// to pick one. mediump is a good default. It means "medium precision"
precision mediump float;

/* in vec4 v_color; */
in float v_temp;
in vec3 v_bc;
in vec4 v_gl_Position;

// we need to declare an output for the fragment shader
out vec4 outColor;

/* Definition of color palette as per http://www.dhondt.de/
 * n   r   g   b
 * 
 * 1  191   0   0
 * 2  223  64   0
 * 3  255 128   0
 * 4  255 191   0
 * 5  255 255   0
 * 6  212 234   0
 * 7  170 212   0
 * 8  127 191   0
 * 9   85 170   0
 * 10  43 149   0
 * 11   0 128   0
 * 12   0 159  26
 * 13   0 191  51
 * 14   0 223  76
 * 15   0 255 102
 * 16   0 191 128
 * 17   0 128 153
 * 18   0  64 178
 * 19   0   0 204
 * 20  64   0 230
 * 21 128   0 255
 *
 * */

float color_exp(in float temp, in float center, in float sigma){
  return exp(-(float(temp) - center)*(float(temp) - center)/(2.*sigma*sigma));
}

float blue(in float temp){
  return color_exp(temp, -200., 100.);
}

float green(in float temp){
  return color_exp(temp, 20., 200.);
}

float red(in float temp){
  return color_exp(temp, 400., 300.);
}

/* From http://codeflow.org/entries/2012/aug/02/easy-wireframe-display-with-barycentric-coordinates/ */
float edgeFactor(){
  vec3 d = fwidth(v_bc);
  /* if (any(greaterThan(d, vec3(20.0)))) { */
  /*     d = vec3(0.0); */
  /*   } */
  vec3 a3 = smoothstep(vec3(0.0), d*0.5, v_bc);
  return min(min(a3.x, a3.y), a3.z);
}

void main() {

  vec3 outval = mix(vec3(0.0), vec3(red(v_temp), green(v_temp), blue(v_temp)), edgeFactor());
  outColor = vec4(outval, 1.0);

  /* vec3 rgb = vec3(red(v_temp), green(v_temp), blue(v_temp)); */
  /* vec3 oneoverz_rgb = 1.0*(1.0 - edgeFactor()) * vec3(red(v_temp), green(v_temp), blue(v_temp)); */
  /* outColor = vec4(rgb - oneoverz_rgb, 1.0); */

  /* outColor = vec4(0.0, 0.0, 0.0, (1.0-edgeFactor())*0.95); */
}
