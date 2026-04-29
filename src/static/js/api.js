class API {
    constructor() {
        this.fetchAPI = this.fetchAPI.bind(this);
        this.doFetch = this.doFetch.bind(this);

        this.GET = this.GET.bind(this);
        this.POST = this.POST.bind(this);
        this.PUT = this.PUT.bind(this);
        this.DELETE = this.DELETE.bind(this);
    }

    parseJSON(response) {
        if (response === null || response.status === 204 || response.status === 205) {
            return null;
        }
        const content_type = response.headers.get("content-type");
        if (content_type && content_type.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            return response.text();
        }
    }

    checkStatus(response) {
        //console.log("request.checkstatus");
        //console.log(response.status);
        //console.log(response.headers);
        //console.log(response.url);
        if(response.ok) {
            if (response.redirected) {
                // Handle redirection
                window.location.href = response.url; // Redirect to the new URL
                return null;
            } else {
                return response;
            }
        } else {
            //console.log(response.status);
            //console.log(response.statusText);
            // https://stackoverflow.com/questions/49784371/fetch-api-get-error-messages-from-server-rather-than-generic-messages/49794801
            return response.json().then(err => {
                                        const error = {
                                            'detail': err.detail || response.statusText,
                                            'status': response.status,
                                            'statusText': response.statusText
                                        };
                                        console.log("api.checkStatus error:", error);
                                        return Promise.reject(error);
                                     });
        }
    }

    async fetchAPI(requestURL, options) {
        /***********************
        // make fetch synchronous-looking
        try {
            const response = await fetch(requestURL, options);
            await this.checkStatus(response);
            const data = await this.parseJSON(response);
            return data;
        } catch (error) {
            throw error; // Propagate the error
        }
        ************************/
        return fetch(requestURL, options)
            .then(this.checkStatus)
            .then(this.parseJSON);
            //.then(data => {console.log("fetch.data");
            //               console.log(data);
            //               return data;}
            //     );
    }

    doFetch(method, endPoint, data, type) {
        let options = {
            method: method,
            headers: {
                    "Accept": "application/json, text/html",
            },
        };
        if(data) {
            if(type === "form") {
                options.headers["Content-Type"] = "application/x-www-form-urlencoded";
                options.body = data
            } else if(type === "file") {
                options.headers["enctype"] = "multipart/form-data";
                options.body = data
            } else { // type === "json"
                options.headers["Content-Type"] = "application/json";
                options.body = JSON.stringify(data);
            }
        }

        return this.fetchAPI(endPoint, options);
    }

    GET(endPoint, data=null, type="form") {
        return this.doFetch("GET", endPoint, data, type);
    }

    POST(endPoint, data=null, type="form") {
        return this.doFetch("POST", endPoint, data, type);
    }

    PUT(endPoint, data=null, type="form") {
        return this.doFetch("PUT", endPoint, data, type);
    }

    DELETE(endPoint, data=null, type="form") {
        return this.doFetch("DELETE", endPoint, data, type);
    }
}

const api = new API();

export default api
