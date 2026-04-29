import api from "./api"
import { navigateTo } from "./router"
import store from "./store"
import { isEmpty, isNil, isNull } from "./utils"

export function menuItemClick(event) {
    event.preventDefault();

    // close source element
    // check if from main_menu
    const ele = document.querySelector("#menu-drawer");
    if(ele && ele.checked) {
        // close main-menu drawer
        ele.checked = false;
    } else {
        // close user-menu dropdown
        event.target.blur();
    }
    // make sure event.target is data-link
    let href = event.target.href;
    if(!href) {
        let target = event.target;
        while (target && target !== document) {
            if (target.tagName === 'A') {
                // Found an <a> element
                href = target.href;
                break;
            }
            target = target.parentNode;
        }
    }
    navigateTo(href);
}

function menuClick(event) {
    if(event.target.matches("[data-link]")) {
        // clicked a menu-item
        return;
    }
    let menu_state = store.get("menu_state", "[]");
    // get closest details tag - click event is on summary tag
    const obj = event.target.closest("[data-menu]");
    const open = obj.hasAttribute("open");
    const menu_id = obj.id.replace("menu-","").trim();

    if(!open) {
        if(!menu_state.includes(menu_id)) {
            // add
            menu_state.push(menu_id);
        }
    } else {
        if(menu_state.includes(menu_id)) {
            // remove
            menu_state.splice(menu_state.indexOf(menu_id), 1);
        }
    }
    menu_state = store.set("menu_state", menu_state);
    try {
        api.POST("/updateMenuState", new URLSearchParams("menu_state="+menu_state));
    } catch (err) {
        const message = `menu.menuClick ${err.status} ${err.detail}`;
        const toaster = document.querySelector("[data-toaster]");
        toaster.show(message,"error");
    }
}

class Menu {
    init() {
        const initPassword = document.getElementById("initPassword");
        if(isNil(initPassword)) this.reset()
        else {
            document.querySelectorAll("[data-link]").forEach(item => {
                item.classList.add("pointer-events-none");
            });
        };

        // Menu state
        let menu_state = [];
        // data-menu is clicked in summary tag not details tag
        document.querySelectorAll("[data-menu]").forEach(detail => {
            detail.addEventListener("click", menuClick);
            if(detail.hasAttribute("open")) {
                const menu_id = detail.id.replace("menu-","").trim();
                menu_state.push(menu_id);
            }
        });
        store.set("menu_state", menu_state);
    }

    reset() {
        document.querySelectorAll("[data-link]").forEach(item => {
            item.addEventListener("click", menuItemClick);
            item.classList.remove("pointer-events-none");
        });
    }

    async refreshBookmarks(menu = null) {
        if(isNull(menu)) {
            await api.GET("/bookmarksMenu").then(data => { menu = data });
        }

        const ul = document.querySelector('[data-main_menu]');
        // remove existing bookmark menu items
        let details = document.getElementById("menu-bookmarks"); // details
        let open = false;
        if(details) {
            open = details.hasAttribute("open");
            ul.removeChild(details.parentNode);  // li
        }
        // now populate
        if(!isEmpty(menu)) {
            details = document.createElement("details");
            details.setAttribute("data-menu", true);
            details.id = "menu-bookmarks";
            if(open) details.setAttribute("open", true);
            details.addEventListener("click", menuClick);

            const summary = document.createElement("summary");
            summary.textContent = "Bookmarks";
            details.appendChild(summary);

            const bul = document.createElement("ul");
            menu.forEach(item => {
                const li = document.createElement("li");

                const a = document.createElement("a");
                a.href = item.url;
                a.textContent = item.title;
                a.setAttribute("data-link", true);
                a.setAttribute("data-bookmark", true);
                a.addEventListener("click", menuItemClick);

                li.appendChild(a);
                bul.appendChild(li);
            });
            details.appendChild(bul);

            const li = document.createElement("li");
            li.appendChild(details);

            ul.insertBefore(li, ul.firstChild);
        }
    }
}

export const menu = new Menu();
