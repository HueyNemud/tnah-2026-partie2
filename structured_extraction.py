from mistralai import Mistral
from pathlib import Path
import time
from fetch_themes import import_turtle_file, build_summary_report
import os

from mistralai import ChatCompletionResponse


def save_to_json(chat_response: ChatCompletionResponse, turtle_file: Path):
    """Enregistre la réponse de l'API dans un fichier JSON."""
    import json

    output_file = turtle_file.with_suffix(".json")
    response_content = chat_response.choices[0].message.content
    with open(output_file, "w", encoding="utf-8") as file:
        json_object = json.loads(response_content)
        json.dump(json_object, file, ensure_ascii=False, indent=4)


api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

DIR = Path(__file__).parent / "photographies_avec_themes"
turtle_files = list(DIR.glob("*.ttl"))


SYSTEM_PROMPT = """
# Rôle
Tu es un expert en extraction d'information géographique dans des métadonnées patrimoniales.

# Tâche
À partir d'un résumé descriptif d'une photographie ancienne, tu dois :
1. identifier les entités géographiques qui renseignent sur **la localisation du sujet de la photographie** dans l'espace ;
2. lister ces entités les uns après les autres.

# Règles
- les entités doivent être triée de la plus précise à la plus générale.

# Exemple
**Résumé descriptif **
=== PHOTO : Au Soleil d'or : 84 [quatre-vingt-quatre] Rue S.t Sauveur (Modifié), [photographie] ===
Lien : http://data.bnf.fr/ark:/12148/cb40268281c#about
Thèmes assignés:
• « Dans l'art » - altLabels : « Représentation dans l'art », « Dans la sculpture », « Dans la peinture », « Représentation iconographique », « Dans les arts graphiques »
• « Cafés » - altLabels : « Cafés-bars », « Débits de boissons », « Estaminets », « Brasseries (cafés) », « Zincs (cafés) », « Bistrots », « Cafés publics », « Cafés (établissements) », « Bars »
• « Paris (France) »
• « Paris (France) -- Rue Saint-Sauveur » - altLabels : « Rue Saint-Sauveur (Paris, France) », « Saint-Sauveur, Rue (Paris, France) »
• « Enseignes » - altLabels : « Signes et indications », « Enseignes commerciales »
• « Ferronnerie d'art » - altLabels : « Serrurerie d'art », « Fer forgé, Objets en », « Fer ornemental », « Ferronnerie architecturale », « Ferrures », « Ferronneries », « Ferronnerie décorative », « Fer forgé », « Objets en fer forgé », « Ferronnerie (architecture) »
• « Soleil » - altLabels : « Physique solaire »

**Réponse JSON**
{
    "toponyme": "Au Soleil d'Or",
    "adresse": "84 rue Saint-Sauveur",
    "voie" : "rue Saint-Sauveur",
    "ville": "Paris",
    "pays": "France"
}


Le résumé à traiter sera donné dans le prochain input.
"""


for turtle_file in turtle_files:
    print(f"Processing {turtle_file}...")
    data = import_turtle_file(turtle_file)
    report = build_summary_report(data)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {"role": "user", "content": report},
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages,  # type: ignore
        response_format={
            "type": "json_object",
        },
    )

    print(chat_response.choices[0].message.content)
    save_to_json(chat_response, turtle_file)
    time.sleep(1.5)  # Pause pour éviter de surcharger l'API
