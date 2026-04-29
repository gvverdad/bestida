import api from "./api"
import { routes, navigateTo } from "./router"
import store from "./store"
import { menuItemClick, menu } from "./menu"
import view from "./view"
import { isNil, isNull } from "./utils"

class Breadcrumb {
    constructor() {
        this.remove_active_page = this.remove_active_page.bind(this);
        this.closePage = this.closePage.bind(this);

        this.isInit = false;
    }

    init() {
        this.isInit = true;

        let history_state = [];
        let active_page = null;
        document.querySelectorAll("[data-crumb]").forEach(crumb => {
            // cannot use crumb.href - cannot compare to stored path
            const path = crumb.getAttribute("data-crumb");
            if(crumb.getAttribute("data-active")) {
                active_page = crumb.getAttribute("data-active");
            }
            history_state.push({"path": path, "title": crumb.textContent});
        });

        if(history_state.length === 0) {
            history_state.push(routes[0]);  // home
        }
        store.set("history_state", history_state);
        if(isNull(active_page))
            active_page = history_state[0].path;

        store.set("active_page", active_page);
        document.querySelector('#close_page_button').addEventListener("click",
            (e) => {
                e.preventDefault();
                this.closePage();
            });
        navigateTo(active_page);
    }

    closePage() {
        if(!this.isInit) return null;

        const new_path = this.remove_active_page();
        if(new_path) {
            navigateTo(new_path);
        }
    }

    add(route, view_data) {
        if(!this.isInit) return null;

        const initPassword = document.getElementById("initPassword");

        const close_button = document.getElementById("close_page_button");
        const breadcrumb = document.getElementById("breadcrumb_list");

        if(route.result[0] === "/home") {
            close_button.classList.add("hidden");
        } else {
            // add item to breadcrumb
            let history_state = store.get("history_state", "[]");
            if(!history_state.find(obj => obj.path === route.result[0])) {
                const li = document.createElement('li');
                li.innerHTML = '<a class="normal-case" href="' + route.result[0] + '" data-link ' +
                ' data-crumb="' + route.result[0] + '">' + view_data.title + '</a>';
                breadcrumb.appendChild(li);
                // add onclick event
                li.lastChild.addEventListener("click", menuItemClick)
                // add to history_state
                history_state.push({path: route.result[0], title: view_data.title});
                history_state = store.set("history_state", history_state)
                try {
                    api.POST("/updateNavState", new URLSearchParams("history_state="+history_state));
                } catch (err) {
                    const message = `breadcrumb.add1 ${err.status} ${err.detail}`;
                    const toaster = document.querySelector("[data-toaster]");
                    toaster.show(message,"error");
                }
            }
            close_button.classList.remove("hidden");
        }
        store.set("active_page", route.result[0]);
        try {
            api.POST("/updateActivePage", new URLSearchParams("active_page="+route.result[0]));
        } catch (err) {
            const message = `breadcrumb.add2 ${err.status} ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
        // apply pointer-events to breadcrumbs items
        document.querySelectorAll("[data-crumb]").forEach(crumb => {
            if(initPassword) {
                crumb.classList.remove("pointer-events-auto", "font-medium");
                if(crumb.getAttribute("data-crumb") === route.result[0]) {
                    crumb.classList.add("pointer-events-none", "font-medium");
                    close_button.classList.add("hidden");
                } else {
                    crumb.classList.add("pointer-events-none", "font-light");
                }
            } else {
                if(crumb.getAttribute("data-crumb") === route.result[0]) {
                    crumb.classList.remove("pointer-events-auto", "font-light");
                    crumb.classList.add("pointer-events-none", "font-medium");
                } else {
                    crumb.classList.add("pointer-events-auto", "font-light");
                    crumb.classList.remove("pointer-events-none", "font-medium");
                }
            }
        });
        // link cancel page button to closePage
        const cancel = document.querySelector("[data-cancel_page]");
        if(cancel) {
            cancel.addEventListener("click", (e) => {
                e.preventDefault();
                this.closePage();
            });
        }
        // link submit page button to closePage
        const form = document.querySelector("[data-form]");
        if(form) {
            form.addEventListener("submit", async (e) => {
                e.preventDefault();

                try {
                    await view.submitForm(e.target);
                    this.closePage();
                } catch (err) {
                    const message = `breadcrumb.add3 ${err.status} ${err.detail} : ${route.route.title}`;
                    const toaster = document.querySelector("[data-toaster]");
                    toaster.show(message,"error");
                }
            });
        }
    }

    remove_active_page() {
        if(!this.isInit) return null;

        const active_page = store.get("active_page");

        let history_state = store.get("history_state", "[]");
        const history_index = history_state.findIndex(obj => obj.path === active_page);
        if(history_index < 1) {
            return null;
        }
        const new_path = history_state[history_index-1].path;

        // remove from breadcrumbs
        document.querySelectorAll('#breadcrumb_list li a').forEach(obj => {
            // there are 3 levels - ol li a - we need to remove the li of ol
            // obj is a
            if(obj.getAttribute("data-crumb") === history_state[history_index].path) {
                obj.parentNode.parentNode.removeChild(obj.parentNode);
            }
        });
        // remove from history_state
        history_state.splice(history_index, 1);
        history_state = store.set("history_state", history_state);
        store.set("active_page", new_path);
        try {
            api.POST("/updateNavState", new URLSearchParams("history_state="+history_state));
            api.POST("/updateActivePage", new URLSearchParams("active_page="+new_path));
        } catch (err) {
            const message = `breadcrumb.remove_active_page ${err.status} ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }

        return new_path;
    }

    resetApp() {
        const initPassword = document.getElementById("initPassword");
        if(initPassword) {
            menu.reset();
            initPassword.remove();
        }
    }
}

const breadcrumbs = new Breadcrumb();

export default breadcrumbs
