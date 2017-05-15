/*
 * fem-gl -- getting to terms with WebGL and JavaScript
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
var dataHasChanged = false;
var indexed_arrays;

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
function glRoutine(gl, vs, fs, indexed_arrays, model_metadata) {

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

    var bufferInfo = twgl.createBufferInfoFromArrays(gl, indexed_arrays, drawType=gl.DYNAMIC_DRAW);

    var testBuffer = twgl.createBufferFromTypedArray(gl, indexed_arrays, drawType=gl.DYNAMIC_DRAW);

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    var uniforms = {
        u_transform: twgl.m4.identity() // mat4
    };

	  gl.enable(gl.CULL_FACE);
	  gl.enable(gl.DEPTH_TEST);

    var now = 0,
        then = 0,
        dt = 0;

    var transformationMatrix = twgl.m4.identity();


    function drawScene(now) {

        if (dataHasChanged) {
            console.log('Reloading');
            bufferInfo = twgl.createBufferInfoFromArrays(gl, indexed_arrays, drawType=gl.DYNAMIC_DRAW);
            dataHasChanged = false;
        };

        dt = (now - then)*.001;    // Conversion to seconds
        var dist = dt*Math.PI/180;  // in radiant

        // Update the model view
        uniforms.u_transform = modelMatrix.updateView();

        gl.useProgram(programInfo.program);
        twgl.setBuffersAndAttributes(gl, programInfo, bufferInfo);
        twgl.setUniforms(programInfo, uniforms);
        twgl.drawBufferInfo(gl, bufferInfo);

        window.requestAnimationFrame(drawScene);

        // Advance the time after drawing the frame
        then = now;

    }
    drawScene(now);
}

function edit_indexed_arrays(nodepath, elementpath, timestep) {
    // var nodepath = 'object a/fo/00.1/mesh/case.nodes.bin';
    // var elementpath = 'object a/fo/00.1/mesh/case.dc3d8.bin';

    var node_file;
    var index_file;
    var meta_file;

    var timestep_data;

    var meshPromise = postDataPromise('/mesher_init?nodepath='+nodepath+'&elementpath='+elementpath);

    meshPromise.then(function(value){

        node_file = value['surface_nodes'];
        index_file = value['surface_indexfile'];
        meta_file = value['surface_metadata'];

        var initialTimestepDataPromise = postDataPromise('/get_timestep_data?timestep='+timestep);

        initialTimestepDataPromise.then(function(value){
            timestep_data = value['timestep_data'];

            indexed_arrays = {
                indices: {              // NOTE: This must be named indices or it will not work.
                    numComponents: 1,
                    data: index_file,
                    drawType: gl.DYNAMIC_DRAW
                },
                a_position: {
                    numComponents: 3,
                    data: node_file,
                    drawType: gl.DYNAMIC_DRAW
                },
                a_temp: {
                    numComponents: 1,
                    type: gl.FLOAT,
                    normalized: false,
                    data: new Float32Array(
                        timestep_data
                    ),
                    drawType: gl.DYNAMIC_DRAW
                }
            };
            dataHasChanged = true;
        });
    });
}

function main() {
    // Init WebGL.
    gl = grabCanvas("webGlCanvas");

    // // -----

    // var nodepath = 'object a/fo/00.1/mesh/case.nodes.bin';
    // var elementpath = 'object a/fo/00.1/mesh/case.dc3d8.bin';

    // var node_file;
    // var index_file;
    // var meta_file;

    // var timestep_data;

    // var meshPromise = postDataPromise('/mesher_init?nodepath='+nodepath+'&elementpath='+elementpath);

    // meshPromise.then(function(value){

    //     node_file = value['surface_nodes'];
    //     index_file = value['surface_indexfile'];
    //     meta_file = value['surface_metadata'];

    //     timestep='40.1';

    //     var initialTimestepDataPromise = postDataPromise('/get_timestep_data?timestep='+timestep);

    //     initialTimestepDataPromise.then(function(value){
    //         timestep_data = value['timestep_data'];
    //         console.log(index_file);
    //         console.log(indexed_arrays);
    //         indexed_arrays = {
    //             indices: {              // NOTE: This must be named indices or it will not work.
    //                 numComponents: 1,
    //                 data: index_file
    //             },
    //             a_position: {
    //                 numComponents: 3,
    //                 data: node_file
    //             },
    //             a_temp: {
    //                 numComponents: 1,
    //                 type: gl.FLOAT,
    //                 normalized: false,
    //                 data: new Float32Array(
    //                     timestep_data
    //                 )
    //             }
    //         };
    //         console.log(indexed_arrays);
    //         loadShaders();
    //     });
    // });

    // // -----

    var node_file;
    var index_file;
    var meta_file;

    var timestep_data;

    var dodec_node_promise = getDataSourcePromise("data/dodecahedron.triangles");
    var dodec_index_promise = getDataSourcePromise("data/dodecahedron.indices");
    var dodec_colour_promise = getDataSourcePromise("data/dodecahedron.colors");

    Promise.all([dodec_node_promise, dodec_index_promise, dodec_colour_promise]).then(function(value) {
        node_file = value[0].split(',');
        index_file = value[1].split(',');
        meta_file = [0.0, 0.0, 0.0];
        timestep_data = value[2].split(',');

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

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl,
                  vertexShaderSource, fragmentShaderSource,
                  indexed_arrays, metaSource
                 );
    }

    // // Promise to load the data from file.
    // var trianglePromise = getDataSourcePromise("data/welding_sim.triangles");
    // var temperaturePromise = getDataSourcePromise("data/welding_sim.temperatures");
    // var indexPromise = getDataSourcePromise("data/welding_sim.indices");
    // var metaPromise = getDataSourcePromise("data/welding_sim.metafile");



    // var temperaturePromise_new = getDataSourcePromise("data/welding_sim_new.temperatures");

    // // Once all the promises are resolved...
    // Promise.all(
    //     [
    //         trianglePromise,
    //         temperaturePromise,
    //         indexPromise,
    //         metaPromise,
    //         vertexShaderPromise,
    //         fragmentShaderPromise,
    //         temperaturePromise_new,
    //         meshPromise,
    //         initialTimestepDataPromise
    //     ]
    //     // ... then ...
    // ).then(function(value) {
    //     // ... assign data to variables and ...
    //     // var triangleSource = value[0];
    //     var triangleSource = node_file;

    //     var temperatureSource = value[1];

    //     // var indexSource = value[2];
    //     var indexSource = index_file;
    //     var metaSource = meta_file;
    //     // var metaSource = value[3];

    //     var vertexShaderSource = value[4];
    //     var fragmentShaderSource = value[5];

    //     // Temporary..
    //     // var temperatureSource_new = value[6];
    //     var temperatureSource_new = timestep_data;

    //     // ... generate an array for web gl to display, then ...
    //     indexed_arrays = {
    //         indices: {              // NOTE: This must be named indices or it will not work.
    //             numComponents: 1,
    //             // data: indexSource.split(',')
    //             data: indexSource
    //         },
    //         a_position: {
    //             numComponents: 3,
    //             data: triangleSource
    //             // data: triangleSource.split(',')
    //         },
    //         a_color: {          // Old kid on the block.
    //             numComponents: 3,
    //             type: gl.UNSIGNED_BYTE,
    //             normalized: true,
    //             data: new Uint8Array(
    //                 temperatureSource.split(',')
    //             )
    //         },
    //         a_temp: {           // New kid on the block.
    //             numComponents: 1,
    //             type: gl.FLOAT,
    //             normalized: false,
    //             data: new Float32Array(
    //                 temperatureSource_new.split(',')
    //             )
    //         }

    //     };

    //     // ... call the GL routine (i.e. do the graphics stuff)
    //     glRoutine(gl,
    //               vertexShaderSource, fragmentShaderSource,
    //               indexed_arrays, metaSource
    //              );
    // });
};
