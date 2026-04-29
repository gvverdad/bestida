import view from "./view"
import breadcrumbs from "./breadcrumb"

export const routes = [
    { path: "/home", title: "Home" },
    { path: "/grid/:programId", title: "Grid" },
    { path: "/form/:programId", title: "Form" },
    { path: "/script/:programId", title: "Script" },
    { path: "/spoolviewer/:title/:filename", title: "Spool Viewer" },
    { path: "/imageviewer/:title/:filename", title: "Image Viewer" },
    { path: "/main", title: "Main Layout" },
    { path: "/profile", title: "Profile" },
    { path: "/bookmarks", title: "Bookmarks" },
    { path: "/notifications", title: "Notifications" },
    { path: "/setlocale", title: "Set Locale" },
    { path: "/settimezone", title: "Set Timezone" },
    { path: "/changepassword", title: "Change Password" },
    { path: "/changecompany", title: "Change Company" },
    { path: "/jobqueues", title: "Job Queues" },
    { path: "/spooler", title: "Spoolers" },
    { path: "/launcher", title: "Launcher" },
    { path: "/audit", title: "Audit" },
    { path: "/purgejobs", title: "Purge Job Queues" },
    { path: "/purgespool", title: "Purge Spoolers" },
    { path: "/purgenotifications", title: "Purge Notifications" },
    { path: "/purgeworkfiles", title: "Purge Workfiles" },
    { path: "/importtables", title: "Import Tables" },
    { path: "/exportreleasetables", title: "Export Release Tables" },
    { path: "/importreleasetables", title: "Import Release Tables" },
    { path: "/copycompanydata", title: "Copy Company Data" },
    { path: "/dumpdatabase", title: "Dump Database" },
    { path: "/notfound", title: "Page Not Found" }
];


export async function Router() {
    function pathToRegex(path) {
        return new RegExp("^" + path.replace(/\//g, "\\/").replace(/:\w+/g, "(.+)") + "$");
    }

    const potentialMatches = routes.map(route => {
        return {
            route,
            result: location.pathname.match(pathToRegex(route.path))
        };
    });

    let match = potentialMatches.find(potentialMatch => potentialMatch.result !== null);
    /* Route not found  */
    if (!match) {
        match = {route: routes[routes.length - 1], result: [routes[routes.length - 1].path]};
    }
    if(match.route.path === "/main") {
        // home
        match = {route: routes[0], result: [routes[0].path]};
    }

    await view.getHtml(match);
}

export function navigateTo(url) {
    history.pushState(null, null, url);
    Router();
}
