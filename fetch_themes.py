"""
Ce script a pour objectif d'enrichir les graphes RDF des photographies
avec les labels des thèmes Rameau associés à ces photographies.
"""

# ----------------------------------------------------------------------------------------------------------------------------------------
# --- A. IMPORTS
# ----------------------------------------------------------------------------------------------------------------------------------------

# Annotations de type
from typing import Iterable

# os et pathlib pour la gestion des fichiers et des chemins
import os
from pathlib import Path

# Modules et fonctions utiles pour interagir avec les graphes RDF et le point d'accès SPARQL de la BnF
from SPARQLWrapper import JSONLD, SPARQLWrapper
from rdflib.namespace import DCTERMS
from rdflib import RDF, SKOS, Graph, Node, URIRef
from utils import save_graph_html

# ----------------------------------------------------------------------------------------------------------------------------------------
# --- B. CONFIGURATION GLOBALE
# ----------------------------------------------------------------------------------------------------------------------------------------

# Point d'accès SPARQL de la BnF pour interroger les données Rameau
DATA_BNF_ENDPOINT = "https://data.bnf.fr/sparql"

# ----------------------------------------------------------------------------------------------------------------------------------------
# --- C. FONCTIONS PRINCIPALES
# ----------------------------------------------------------------------------------------------------------------------------------------


def setup_bnf_sparql_wrapper() -> SPARQLWrapper:
    """
    Crée un objet SPARQLWrapper pour interroger le point d'accès SPARQL de la BnF.

    Returns:
        SPARQLWrapper: Un objet SPARQLWrapper configuré.
    """
    endpoint = SPARQLWrapper(DATA_BNF_ENDPOINT)
    endpoint.setTimeout(60)
    return endpoint


def import_turtle_file(turtle_file: Path) -> Graph:
    """
    Charge un graphe RDF à partir d'un fichier Turtle sur le disque.

    Args:
        turtle_file (Path): Le chemin vers le fichier Turtle à charger.

    Returns:
        Graph: Un objet Graph contenant les données RDF chargées depuis le fichier.
    """
    g = Graph()
    g.parse(turtle_file, format="turtle")
    return g


def identify_photo_resource(graph: Graph) -> Node:
    """
    Extrait la ressource de type Manifestation décrivant la photo.
    Le prédicat utilisé est RDA:manifestation (http://rdaregistry.info/Elements/c/#C10007)
    Args:
        graph (Graph): Le graphe RDF à partir duquel extraire l'URI de la photo.
    Returns:
        Node: Le noeud du graphe RDF correspondant à la ressource de type RDA:manifestation décrivant la photo.
    """
    photo_uri = graph.value(
        predicate=RDF.type, object=URIRef("http://rdaregistry.info/Elements/c/#C10007")
    )
    if not photo_uri:
        raise ValueError("Aucune ressource de type RDA:manifestation dans le graphe.")
    return photo_uri


def get_rameau_themes(graph: Graph) -> list[Node]:
    """
    Retourne les sujets associés à une photographie dans son graphe.
    Les sujets sont liés à la photographie via la propriété DCTERMS.subject :
    [ sujets Rameau ] -- DCTERMS.subject --> [ photographie ]

    Args:
        graph (Graph): Le graphe RDF d'une photographie.
    Returns:
        list[Node]: Une liste de noeuds du graphe RDF correspondant aux sujets Rameau associés à la photographie.
    """
    manifestation = identify_photo_resource(graph)
    return list(graph.objects(subject=manifestation, predicate=DCTERMS.subject))


def fetch_themes_labels(themes: Iterable, databnf: SPARQLWrapper) -> Graph:
    """
    Interroge le point d'accès SPARQL de la BnF pour récupérer les labels des thèmes Rameau.
    Args:
        themes (Iterable): Les URIs des thèmes Rameau à interroger.
        databnf (SPARQLWrapper): L'objet SPARQLWrapper configuré pour interroger le point d'accès SPARQL de la BnF.
    Returns:
        Graph: Un graphe RDF contenant les labels des thèmes récupérés depuis la BnF
    """

    if not themes:
        print("Aucun thème Rameau à interroger.")
        return Graph()

    # On a pas besoin de tous les triples associés aux thèmes, mais uniquement de leurs label,
    # qui leurs sont associés via les propriétés SKOS : altLabel et prefLabel :
    # http://www.w3.org/2004/02/skos/core#prefLabel # "preferred label" : le label principal d'un thème.
    # http://www.w3.org/2004/02/skos/core#altLabel # label alternatif.

    # Concatèner les URIs des thèmes Rameau dans une chaîne de caractères pour
    # les injecter dans la requête SPARQL tous ensemble  et éviter de faire une requête SPARQL par thème.
    themes_formatted = " ".join([t.n3() for t in themes])

    # Une requête SPARQL de type CONSTRUCT
    # retourne un graphe RDF construit à partir des résultats de la clause WHERE.
    query = f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{
            VALUES ?s {{ {themes_formatted} }}
            VALUES ?p {{ skos:prefLabel skos:altLabel }}
            ?s ?p ?o .
        }}
    """

    print(f"Requête SPARQL construite :\n{query}")

    databnf.setQuery(query)

    # Forcer le format de retour en JSON-LD
    # pour récupérer un objet Graph directement à partir de la réponse de la requête SPARQL.
    databnf.setReturnFormat(JSONLD)

    results = databnf.queryAndConvert()

    # Garde-fou si jamais queryAndConvert change et ne retourne plus un objet Graph,
    # ou si le format de retour n'est plus JSON-LD ou RDF/XML
    if not isinstance(results, Graph):
        results = Graph().parse(data=results, format="json-ld")  # type: ignore

    return results


def build_summary_report(graph: Graph) -> str:
    """
    Construit un rapport de synthèse des thèmes associés à une photographie à partir de son graphe RDF.
    Args:
        graph (Graph): Le graphe RDF d'une photographie.
    Returns:
        str: Une chaîne de caractères contenant le rapport de synthèse.
    """
    # 1. Récupère l'URI de la photo et son titre
    photo_uri = graph.value(
        predicate=RDF.type, object=URIRef("http://rdaregistry.info/Elements/c/#C10007")
    )
    titre = graph.value(subject=photo_uri, predicate=DCTERMS.title)

    # 2. Prépare l'en-tête de l'infobox
    report = f"\n=== PHOTO : {titre} ===\n"
    report += f"Lien : {photo_uri}\n"
    report += "Thèmes assignés:\n"

    # 3. Pour chaque thème associé à la photo...
    for theme in graph.objects(subject=photo_uri, predicate=DCTERMS.subject):

        # ... on affiche le label principal du thème
        pref = graph.value(subject=theme, predicate=SKOS.prefLabel)
        report += f" • « {pref} »"

        # ... puis les alternatives
        altLabels = list(graph.objects(subject=theme, predicate=SKOS.altLabel))
        if altLabels:
            report += f" - altLabels : {', '.join(f'« {label} »' for label in altLabels)}"  # type: ignore
        report += "\n"

    # 4. Retourne le rapport de synthèse construit
    return report


def merge_labels_into_photo_graph(
    photo_graph: Graph, rameau_labels_graph: Graph
) -> Graph:
    """
    Ajoute les labels des thèmes Rameau au graphe RDF d'une photographie.
    Args:
        photo_graph (Graph): Le graphe RDF d'une photographie.
        rameau_labels_graph (Graph): Le graphe RDF contenant les labels des thèmes Rameau récupérés depuis la BnF.
    Returns:
        Graph: Le graphe RDF de la photographie enrichi avec les labels des thèmes Rameau.
    """

    return photo_graph + rameau_labels_graph


def export_to_turtle(graph: Graph, output_file: Path) -> None:
    """
    Enregistre un graphe RDF sur le disque au format Turtle.
    Args:
        graph (Graph): Le graphe RDF à enregistrer.
        output_file (Path): Le chemin vers le fichier Turtle où enregistrer le graphe.
    Returns:
        None: Cette fonction enregistre le graphe sur le disque et ne retourne rien.
    """
    graph.serialize(destination=output_file, format="turtle")


def export_graph_to_html(graph: Graph, output_file: Path) -> None:
    """Exporte un graphe RDF au format HTML pour visualisation."""
    save_graph_html(graph, output_file.as_posix(), height="600px", notebook=False)


# ----------------------------------------------------------------------------------------------------------------------------------------
# --- D. POINT D'ENTRÉE DU SCRIPT
# ----------------------------------------------------------------------------------------------------------------------------------------
