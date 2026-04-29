import api from "./api"
import { Router, navigateTo } from "./router"
import breadcrumbs from "./breadcrumb"
import { menu } from "./menu"
import store from "./store"
import user from "./user"
import svg from "./svg"

import "./components/datatable/datatable"
import "./components/form/form"
import "./components/script/script"
import "./components/document/document"
import "./components/checkbox"
import "./components/combobox"
import "./components/container"
import "./components/datetime"
import "./components/dialog"
import "./components/home"
import "./components/input"
import { myNotifications } from "./components/notification"
import "./components/spooler"
import "./components/stepper"
import "./components/submittaskform"
import "./components/tabs"
import "./components/toaster"
import "./components/uploadimage"
import "./components/viewers"


function toggleTheme(event) {
    setupTheme();
}

async function setupTheme(init=false) {
    const themes = {};
    try {
        await api.GET("/themes").then(response => {
            for (const t of response.data) {
                themes[t[0]] = t[1];
            }
        });
    } catch (err) {
        const message = `app.setupTheme1 ${err.status} ${err.detail}`;
        const toaster = document.querySelector("[data-toaster]");
        toaster.show(message,"error");
    }

    let theme = document.querySelector("html").getAttribute("data-theme");
    let theme_key = "dark";
    const ele_dark_theme = document.getElementById("dark_theme");
    const ele_light_theme = document.getElementById("light_theme");
    const ele_menu_swap = document.getElementById("menu_swap_theme");
    if(theme === themes["dark"]) {
        theme_key = "light";
        if(init) {
            ele_menu_swap.checked = false;
            ele_dark_theme.classList.add("hidden");
            ele_light_theme.classList.remove("hidden");
        } else {
            document.querySelector("html").setAttribute("data-theme", themes["light"]);
            ele_menu_swap.checked = true;
        }
    } else {
        theme_key = "dark";
        if(init) {
            ele_menu_swap.checked = true;
            ele_dark_theme.classList.remove("hidden");
            ele_light_theme.classList.add("hidden");
        } else {
            document.querySelector("html").setAttribute("data-theme", themes["dark"]);
            ele_menu_swap.checked = false;
        }
    }
    if(!init) {
        ele_dark_theme.classList.toggle("hidden");
        ele_light_theme.classList.toggle("hidden");

        try {
            await api.POST("/changeTheme", new URLSearchParams("theme="+theme_key));
            user.setup();
        } catch (err) {
            const message = `app.setupTheme2 ${err.status} ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }
};

// Function to enable popstate listener
function enablePopstateListener() {
    window.addEventListener('popstate', Router);
}

// Function to disable popstate listener
function disablePopstateListener() {
    window.removeEventListener('popstate', Router);
}

document.addEventListener("DOMContentLoaded", () => {
    // render svg
    svg.render();
    // minimal layout
    const minimal = document.querySelector("[data-minimal]");
    if(minimal) {
        disablePopstateListener();
        store.remove("active_page");
        store.remove("history_state");
        store.remove("menu_state");

        let theme = "dark";
        if(store.get("user.Settings.Theme")) {
            theme = store.get("user.Settings.Theme")[1];
        }
        document.querySelector("html").setAttribute("data-theme", theme);
    } else { // app layout
        // Theme
        setupTheme(true);
        document.querySelectorAll("[data-toggleTheme]").forEach(theme => {
            theme.addEventListener("click", toggleTheme);
        });
        // menu
        menu.init();
        // copyright
        document.getElementById("current_year").innerHTML = new Date().getFullYear();
        // setup user data
        user.setup();
        // breadcrumbs
        breadcrumbs.init();
        // user navigates with the back and forward buttons.
        enablePopstateListener();
        // enable notifications
        myNotifications.enable();
    }
});

window.addEventListener("beforeunload", (event) => {
    // disable notifications
    myNotifications.disable();
});