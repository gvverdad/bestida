import store from "./store"
import api from "./api"

class User {

    setup() {
        try {
            api.GET("/current_user")
                .then(response => {
                    store.set("user", response.data);
                    document.querySelectorAll("[data-company_name]").forEach(ele => {
                        ele.textContent = response.data.Company.Name;
                    });
                    document.querySelectorAll("[data-user_name]").forEach(ele => {
                        ele.textContent = response.data.Personal.FirstName + " " +
                                          response.data.Personal.LastName;
                    });
                    document.querySelectorAll("[data-user_group_role]").forEach(ele => {
                        ele.textContent = response.data.Role.Group.Description + "/" +
                                          response.data.Role.Description;
                    });
                    document.querySelectorAll("[data-gravatar]").forEach(ele => {
                        ele.src = response.data.Personal.GravatarId;
                    });
                });
        } catch (err) {
            const message = `user.setup ${err.status} ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }
}

const user = new User();

export default user
