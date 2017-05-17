/*
 * fem-gl -- Display FEM raw data in a browser
 * Copyright (C) 2017 Matthias Plock <matthias.plock@bam.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

var gl;

// Make the array for holding web gl data global.
var vertexDataHasChanged = false;
var fragmentDataHasChanged = false;
var indexed_arrays;
var model_metadata;

function grabCanvas(canvasElementName) {
    // Select the canvas element from the html
    var webGlCanvas = document.getElementById(canvasElementName);

    // Create a webGl2 context if possible
    var gl = twgl.getContext(webGlCanvas);

    // Check if WebGL 2.0, if not throw error
    function isWebGL2(gl) {
        return gl.getParameter(gl.VERSION).indexOf("WebGL 2.0") == 0;
    }
    if (isWebGL2(gl) != true) {
        console.log("No WebGL2");
        Error("No WebGL2");
    }

    return gl;
}

// This is called with established context and shaders loaded
function glRoutine(gl, vs, fs) {

    var programInfo = twgl.createProgramInfo(gl, [vs, fs]);

    var modelMatrix = new ModelMatrix(gl);

    // var centerModel = new Float32Array(model_metadata.split(','));
    var centerModel = model_metadata;

    var scaleTheWorldBy = 150;
    var tarPos = twgl.v3.mulScalar(centerModel, scaleTheWorldBy);
    var camPos = twgl.v3.create(tarPos[0], tarPos[1], 550); // Center the z-axis over the model
    var up = [0, -1, 0];

    modelMatrix.placeCamera(camPos, tarPos, up);

    // Place the center of rotation into the center of the model
    modelMatrix.translateWorld(twgl.v3.negate(centerModel));

    // Automate this...
    modelMatrix.scaleWorld(scaleTheWorldBy);

    var bufferInfo = twgl.createBufferInfoFromArrays(gl, indexed_arrays);

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    var uniforms = {
        u_transform: twgl.m4.identity() // mat4
    };

	  gl.enable(gl.CULL_FACE);
	  gl.enable(gl.DEPTH_TEST);

    var transformationMatrix = twgl.m4.identity();

    function drawScene(now) {

        // Check if our data has been updated at some point.
        if (vertexDataHasChanged) {
            // Update the buffer.
            bufferInfo = twgl.createBufferInfoFromArrays(gl, indexed_arrays);

            // Center the new object.
            centerModel = model_metadata;
            modelMatrix.translateWorld(twgl.v3.negate(centerModel));

            vertexDataHasChanged = false;
        } else if (fragmentDataHasChanged){
            bufferInfo = twgl.createBufferInfoFromArrays(gl, indexed_arrays);
            fragmentDataHasChanged = false;
        };

        // Update the model view
        uniforms.u_transform = modelMatrix.updateView();

        gl.useProgram(programInfo.program);
        twgl.setBuffersAndAttributes(gl, programInfo, bufferInfo);
        twgl.setUniforms(programInfo, uniforms);
        twgl.drawBufferInfo(gl, bufferInfo);

        window.requestAnimationFrame(drawScene);

    }
    drawScene();
}

function update_timestep_data(object_name, field, timestep) {
    var timestep_promise = postDataPromise(
        '/get_timestep_data?object_name=' + object_name +
            '&field=' + field + '&timestep='+timestep);
    var timestep_data;

    timestep_promise.then(function(value){
        timestep_data = value['timestep_data'];

        indexed_arrays['a_temp']['data'] = new Float32Array(timestep_data);

        fragmentDataHasChanged = true;
    });
}

function edit_indexed_arrays(object_name, field, nodepath, elementpath, timestep) {

    var node_file;
    var index_file;
    var meta_file;

    var timestep_data;

    var meshPromise = postDataPromise('/mesher_init?nodepath='+nodepath+'&elementpath='+elementpath);

    meshPromise.then(function(value){

        node_file = value['surface_nodes'];
        index_file = value['surface_indexfile'];
        meta_file = value['surface_metadata'];

        var initialTimestepDataPromise = postDataPromise(
            '/get_timestep_data?object_name=' + object_name +
                '&field=' + field + '&timestep='+timestep);

        initialTimestepDataPromise.then(function(value){
            timestep_data = value['timestep_data'];

            indexed_arrays = {
                indices: {              // NOTE: This must be named indices or it will not work.
                    numComponents: 1,
                    data: index_file
                },
                a_position: {
                    numComponents: 3,
                    data: node_file
                },
                a_temp: {
                    numComponents: 1,
                    type: gl.FLOAT,
                    normalized: false,
                    data: new Float32Array(
                        timestep_data
                    )
                }
            };

            model_metadata = meta_file;

            vertexDataHasChanged = true;
        });
    });
}

function main() {
    // Init WebGL.
    gl = grabCanvas("webGlCanvas");

    var node_file;
    var index_file;
    var meta_file;

    var timestep_data;

    var dodec_promise = getDataSourcePromise("data/dodecahedron.json");
    dodec_promise.then(function(value) {
        var parsed_json = JSON.parse(value);
        node_file = parsed_json['vertices'];
        index_file = parsed_json['indices'];
        timestep_data = parsed_json['colours'];
        meta_file = [0.0, 0.0, 0.0];

        loadShaders();
    });

    var vertexShaderSource;
    var fragmentShaderSource;

    function loadShaders() {
        var vertexShaderPromise = getDataSourcePromise("shaders/vertexShader.glsl.c");
        var fragmentShaderPromise = getDataSourcePromise("shaders/fragmentShader.glsl.c");

        Promise.all([vertexShaderPromise, fragmentShaderPromise]).then(function(value) {
            vertexShaderSource = value[0];
            fragmentShaderSource = value[1];

            prepareArrays();
        });
    }

    function prepareArrays() {

        var triangleSource = node_file;
        var indexSource = index_file;
        var metaSource = meta_file;
        var temperatureSource = timestep_data;

        indexed_arrays = {
            indices: {              // NOTE: This must be named indices or it will not work.
                drawType: gl.DYNAMIC_DRAW,
                numComponents: 1,
                data: indexSource
            },
            a_position: {
                drawType: gl.DYNAMIC_DRAW,
                numComponents: 3,
                data: triangleSource
            },
            a_temp: {
                drawType: gl.DYNAMIC_DRAW,
                numComponents: 1,
                type: gl.FLOAT,
                normalized: false,
                data: new Float32Array(
                    temperatureSource
                )
            }
        };

        // Set model metadata.
        model_metadata = meta_file;

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl,
                  vertexShaderSource, fragmentShaderSource,
                  metaSource
                 );
    }
};
