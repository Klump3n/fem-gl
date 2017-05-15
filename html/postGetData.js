

function postDataPromise(postString) {
    // Return a promise for XHR data
    return new Promise(function(resolve, reject) {
	      var xhr = new XMLHttpRequest;
	      xhr.responseType = 'text';
	      xhr.open('POST', postString, true);
	      xhr.onload = function() {
	          if (xhr.status === 200) {
		            // Tries to get the shader source
                var result = xhr.responseText;
		            resolve(JSON.parse(result));
	          } else {
		            // If unsuccessful return an error
		            reject(Error('postGetData() - ERROR with '+postString));
	          }
	      };
	      xhr.onerror = function() {
	          // Maybe we have more severe problems. Also return an error then
	          reject(Error('postGetData() - network issues'));
	      };
	      // Send the request
	      xhr.send();
    });
}

