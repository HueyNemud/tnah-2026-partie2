import base64
from enum import Enum
import hashlib
import json
from pyvis.network import Network
from rdflib import Literal, Graph


def generate_graph_from_rdf(rdf_graph, width="100%", height="600px", notebook=False):
    # Palette Kawaii Soft épurée
    colors = {
        "bg": "#ffffff",  # Blanc pur pour la clarté
        "text": "#6E665E",  # Gris chaud doux (plus soft que le noir)
        "sakura": "#FFC1CC",  # Rose (Expression)
        "sky": "#A2D2FF",  # Bleu (Sujets)
        "matcha": "#C1E1C1",  # Vert (Littéraux)
        "cream": "#FEE1A8",  # Jaune (Objets)
        "line": "#E8E8E8",  # Lignes très discrètes
    }

    net = Network(
        height=height,
        width=width,
        bgcolor=colors["bg"],
        font_color=colors["text"],  # type: ignore
        notebook=notebook,
        cdn_resources="remote",
    )

    added_nodes = set()

    def safe_id(value):
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    for s, p, o in rdf_graph:
        s_str, p_str, o_str = str(s), str(p), str(o)
        s_id = s_str
        o_id = safe_id(o_str) if isinstance(o, Literal) else o_str

        s_label = s_str.split("/")[-1]
        p_label = p_str.split("/")[-1].split("#")[-1]
        o_label = o_str.split("/")[-1].split("#")[-1]

        # --- Nœuds : Bulles colorées sans bordures ---
        if s_id not in added_nodes:
            is_expr = s_str.endswith("#Expression")
            net.add_node(
                s_id,
                label=s_label,
                title=s_str,
                color=colors["sakura"] if is_expr else colors["sky"],
                shape="dot",
                size=15,
                borderWidth=0,
                font={"size": 14, "face": "Arial Rounded MT Bold, sans-serif"},
            )
            added_nodes.add(s_id)

        if o_id not in added_nodes:
            is_lit = isinstance(o, Literal)
            net.add_node(
                o_id,
                label=o_label,
                color=colors["matcha"] if is_lit else colors["cream"],
                shape="dot",
                size=10 if is_lit else 13,
                borderWidth=0,
                font={"size": 12, "face": "Arial Rounded MT Bold, sans-serif"},
            )
            added_nodes.add(o_id)

        # --- Arêtes : Fines et claires ---
        net.add_edge(
            s_id,
            o_id,
            label=p_label,
            color={"color": colors["line"], "highlight": colors["sakura"]},
            width=2,
            arrows={"to": {"enabled": True, "scaleFactor": 0.3}},
            font={
                "size": 9,
                "color": "#B0B0B0",
                "strokeWidth": 0,
            },  # Pas d'encadré texte
        )

    options = {
        "nodes": {
            "font": {"strokeWidth": 0, "align": "top"},  # Suppression contour texte
            "shadow": {
                "enabled": True,
                "color": "rgba(0,0,0,0.05)",
                "size": 7,
                "x": 3,
                "y": 3,
            },
        },
        "edges": {
            "smooth": {"type": "continuous", "roundness": 0.4},
            "font": {
                "strokeWidth": 0
            },  # Assure qu'il n'y a pas de fond derrière le texte des liens
        },
        "physics": {
            "forceAtlas2Based": {"gravitationalConstant": -100, "springLength": 120},
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 100},
        },
        "interaction": {"hover": True, "navigationButtons": False},
    }

    net.set_options(json.dumps(options))
    return net


def save_graph_html(
    graph, output_filename="graph.html", width="100%", height="400px", notebook=False
):
    net = generate_graph_from_rdf(graph, width=width, height=height, notebook=notebook)
    net.write_html(output_filename)


def show_graph(graph, notebook=False, width="100%", height="400px"):
    net = generate_graph_from_rdf(graph, width=width, height=height, notebook=notebook)
    html_content = net.generate_html()

    data_uri = (
        "data:text/html;base64," + base64.b64encode(html_content.encode()).decode()
    )
    from IPython.display import display, IFrame

    display(IFrame(src=data_uri, width=width, height=height))


class TEAMS(Enum):
    HERISSON = "🦔"
    RENARD = "🦊"
    POUSSIN = "🐥"
    PANDA = "🐼"
    GRENOUILLE = "🐸"
    KOALA = "🐨"
    TORTUE = "🐢"
    HIBOU = "🦉"
    CANARD = "🦆"
    LAPIN = "🐇"
    SERPENT = "🐍"
    FOURMI = "🐜"
    ABEILLE = "🐝"
    PAPILLON = "🦋"
    SCARABEE = "🪲"
    CIGALE = "🦗"
    CRABE = "🦀"
    POISSON = "🐟"
    PIEUVRE = "🐙"
    LOUTRE = "🦦"
    OTARIE = "🦭"
    MANCHOT = "🐧"
    LICORNE = "🦄"
    BALEINE = "🐋"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<ÉQUIPE.{self.name}: {self.value}>"

    def get_team(self, n):
        try:
            return list(TEAMS)[n - 1]
        except IndexError:
            return "Invalid index: the team does not exist."


def your_team(subgraph: Graph, team: TEAMS) -> str:
    # On utilise simplement la taille du sous-graphe généré
    nb_triplets = len(subgraph)

    separator = "✨" + " — " * 15 + "✨"

    content = f"""
{separator}
### **🐾 BIENVENUE DANS L'ÉQUIPE {team.name} {team.value} 🐾**
💎 Vous avez reçu un fragment du graphe original.
📦 **Volume assigné** : **{nb_triplets}** triplets de photographies.
🚀 Bonne chance  !
{separator}
"""
    return content


def assign_to_team(g: Graph, total_teams: int, team_number: int) -> Graph:
    # Figer l'ordre des triplets pour empêcher les redondances entre équipes
    all_triples = sorted(list(g))
    total_triples = len(all_triples)

    triples_per_team = total_triples // total_teams
    start_index = (team_number - 1) * triples_per_team

    # Gestion du dernier bloc pour couvrir tout le graphe
    if team_number == total_teams:
        end_index = total_triples
    else:
        end_index = start_index + triples_per_team

    subgraph = Graph()
    for triple in all_triples[start_index:end_index]:
        subgraph.add(triple)

    return subgraph
