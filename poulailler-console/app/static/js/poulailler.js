var poulailler = {
    // liste des modules
    module: [],
    // ajoute an module à la liste et créé le bloc correspondant
    add_module: function(module_name, id, display_name) {
        this.module.push({
            "name": module_name,
            "id": id
        })
        var e = document.createElement("div");
        e.setAttribute("class", "Miw(300px) Bd Bdc($pri) Mih(80px) M(5px)");
        e.setAttribute("id", id);
        var title = document.createElement("h2");
        title.setAttribute("class", "Bgc($pri) C($acc) M(0) P(10px) Ta(c) Pos(r)");
        title.innerText = display_name;
        e.appendChild(title);
        var img = document.createElement("img");
        img.setAttribute("src", "static/img/refresh.png");
        img.setAttribute("class", "Pos(a) End(10px) T(16px) Cur(p)");
        img.setAttribute("title", "Rafraichir");
        img.setAttribute("onclick", "javascript:poulailler.refresh('" + id + "', '" + module_name + "', 'GET');");
        title.appendChild(img);
        var content = document.createElement("div");
        content.setAttribute("class", "P(5px)");
        content.setAttribute("id", id + "-content");
        e.appendChild(content);
        document.getElementById("modules").appendChild(e);
    },
    // charge l'ensemble des modules de manière asynchrone
    load_modules: function() {
        poulailler.module.forEach(element => {
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.onreadystatechange = function() {
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                    poulailler.display(xmlHttp.response, element.id);
            }
            xmlHttp.open("GET", element.name, true);
            xmlHttp.send(null);
        });
    },
    // callback pour charger le html reçu dans le bloc adéquat
    display: function(content, id) {
        elem = document.getElementById(id + "-content");
        elem.innerHTML = content;
        // execution des scripts dans le contenu affiche
        scripts = Array.from(elem.getElementsByTagName("script"));
        scripts.forEach(function(e) {
            eval(e.innerText);
        });
    },
    refresh: function(id, url, verb) {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                poulailler.display(xmlHttp.response, id);
        }
        xmlHttp.open(verb, url, true);
        xmlHttp.send(null);
    }
};

//chargement des modules
document.addEventListener("DOMContentLoaded", poulailler.load_modules);