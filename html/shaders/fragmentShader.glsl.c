#version 300 es

// fragment shaders don't have a default precision so we need
// to pick one. mediump is a good default. It means "medium precision"
precision mediump float;

in vec4 v_color;
in float v_temp;

// we need to declare an output for the fragment shader
out vec4 outColor;

float color_exp(in float temp, in float center, in float sigma){
  return exp(-(float(temp) - center)*(float(temp) - center)/(2.*sigma*sigma));
}

float blue(in float temp){
  return color_exp(temp, 1., 2.2);
}

float green(in float temp){
  return color_exp(temp, 0.5, .2);
}

float red(in float temp){
  return color_exp(temp, 1., .2);
}

void main() {
  outColor.r = red(v_temp);
  outColor.g = green(v_temp);
  outColor.b = blue(v_temp);
  outColor.a = 1.0;
  outColor = v_color;
}
