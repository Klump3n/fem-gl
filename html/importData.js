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

function getXHRPromise(dataFile) {
    // Return a promise for XHR data
    return new Promise(function(resolve, reject) {
	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('GET', dataFile, true);
	      xhr.onload = function() {
	          if (xhr.status === 200) {
		            // Tries to get the shader source
		            resolve(xhr.responseText);
	          } else {
		            // If unsuccessful return an error
		            reject(Error('getXHRPromise() - Could not load ' + dataFile));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('getXHRPromise() - network issues'));
	      };
	      // Send the request
	      xhr.send();
    });
}


function getDataSourcePromise(dataPath){
    // Load the data from a file via xhr
    return new Promise(function(resolve, revoke) {
        // Var that will hold the loaded string
        var dataSource;

        // Promise to load data from XHR
        var dataPromise = getXHRPromise(dataPath);

        // Promise to assign the loaded data to the source variable
        var assignDataToVar = dataPromise.then(function(value) {
            // console.log("Loading " + dataPath);
            dataSource = value;
        });

        // Once everything is loaded resolve the promise
        assignDataToVar.then(function() {
            resolve(dataSource);
        });
    });
}
