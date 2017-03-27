/*
 * fem-gl-toying -- getting to terms with WebGL and JavaScript
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
function glRoutine(gl, vs, fs,
                   model_triangles, model_temperatures, model_indices, model_metadata) {
    var programInfo = twgl.createProgramInfo(gl, [vs, fs]);

    var indexed_arrays = {
        indices: {              // NOTE: This must be named indices or it will not work.
            numComponents: 1,
            data: model_indices.split(',')
        },
        a_position: {
            numComponents: 3,
            data: model_triangles.split(',')
        },
        a_color: {
            numComponents: 3,
            type: gl.UNSIGNED_BYTE,
            normalized: true,
            data: new Uint8Array(
                model_temperatures.split(',')
            )
        }
    };


    var modelMatrix = new ModelMatrix(gl);

    var centerModel = new Float32Array(model_metadata.split(','));

    var scaleTheWorldBy = 150;
    var tarPos = twgl.v3.mulScalar(centerModel, scaleTheWorldBy);
    var camPos = twgl.v3.create(tarPos[0], tarPos[1], 110); // Center the z-axis over the model
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

    var now = 0,
        then = 0,
        dt = 0;


    var transformationMatrix = twgl.m4.identity();

    function drawScene(now) {

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

function main() {
    // Init WebGL.
    var gl = grabCanvas("webGlCanvas");

    // Promise to load the data from file.
    var trianglePromise = getDataSourcePromise("data/welding_sim.triangles");
    var temperaturePromise = getDataSourcePromise("data/welding_sim.temperatures");
    var indexPromise = getDataSourcePromise("data/welding_sim.indices");
    var metaPromise = getDataSourcePromise("data/welding_sim.metafile");

    var vertexShaderPromise = getDataSourcePromise("shaders/vertexShader.glsl.c");
    var fragmentShaderPromise = getDataSourcePromise("shaders/fragmentShader.glsl.c");

    // Once all the promises are resolved...
    Promise.all(
        [
            trianglePromise,
            temperaturePromise,
            indexPromise,
            metaPromise,
            vertexShaderPromise,  // 2
            fragmentShaderPromise, // 3
        ]
        // ... then ...
    ).then(function(value) {
        // ... assign data to variables and ...
        var triangleSource = value[0];
        var temperatureSource = value[1];
        var indexSource = value[2];
        var metaSource = value[3];
        var vertexShaderSource = value[4];
        var fragmentShaderSource = value[5];

        // ... call the GL routine (i.e. do the graphics stuff)
        glRoutine(gl,
                  vertexShaderSource, fragmentShaderSource,
                  triangleSource, temperatureSource, indexSource, metaSource
                 );
    });
};
