class Store {
    get(key, default_value="") {
        if(key.includes(".")) {
            // ie user.Role.Group.Description
            const keys = key.split(".");
            let obj = null;
            const max = keys.length - 1;
            keys.forEach((k, idx) => {
                if(idx < max) {
                    if(!obj) obj = JSON.parse(localStorage.getItem(k));
                    else obj = obj[k];
                }
            });
            if(obj !== null) return obj[keys[max]] || default_value;
            else return default_value;
        } else
            return JSON.parse(localStorage.getItem(key) || default_value);
    }

    set(key, data) {
        const data_string = JSON.stringify(data);
        localStorage.setItem(key, data_string);
        return data_string;
    }

    remove(key) {
        localStorage.removeItem(key);
    }
}

const store = new Store();

export default store
