var poulailler = {
    // liste des modules
    module: [],
    // ajoute an module à la liste et créé le bloc correspondant
    add_module: function(module_name, id) {
        this.module.push({
            "name": module_name,
            "id": id
        })
        var e = document.createElement("div");
        e.setAttribute("class", "Miw(300px) Bd Bdc($pri) Mih(80px) M(5px)");
        e.setAttribute("id", id);
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
        elem = document.getElementById(id);
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