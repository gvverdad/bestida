class SVG {
    constructor() {
        this.path = "/static/icons/";
    }

    render(doc=document) {
        doc.querySelectorAll("[data-icon]").forEach(container => {
            const svgFileName = container.textContent;
            container.innerHTML = "";

            fetch(`${this.path}${svgFileName}.svg`)
                .then((response) => response.text())
                .then((svgText) => {
                    container.innerHTML = svgText;
                })
            .catch((error) => {
                console.error(`Error loading SVG: ${error}`);
            });
        });
    }

    get(svgFileName) {
        return fetch(`${this.path}${svgFileName}.svg`)
                .then((response) => response.text())
                .then((svgText) => {
                    return svgText;
                })
            .catch((error) => {
                console.error(`Error loading SVG: ${error}`);
                return null;
        });
    }
}

const svg = new SVG();

export default svg
