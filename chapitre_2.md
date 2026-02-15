#  🙤 **PARTIE 2** 🙧

# Extraction structurée des indices géographiques dans les métadonnées des photographies d'[Eugène Atget](https://fr.wikipedia.org/wiki/Eug%C3%A8ne_Atget)


🙑 Au-delà de son volume, l'œuvre d'Eugène Atget frappe par la méticulosité de son classement. Véritable archiviste de son propre travail, l’auteur a systématiquement indexé ses clichés, les structurant en séries et en albums thématiques. Chaque cliché est doté d'un titre décrivant son sujet et sa localisation, souvent très précisément.

Ces titres, systématiquement relevés et transcrits, font parti des métadonnées associées à chaque photographie. Les archivistes ne se sont cependant pas arrêté là et ont enrichi la description structurée de chaque cliché avec des thèmes issus du thésaurus Rameau.

La richesse géographique de ces métadonnées permet aujourd'hui d'envisager une cartographie du fonds dans l’espace parisien. Cette approche, image par image, offrirait un parcours inédit au cœur de la capitale et renouvellerait notre regard sur l’œuvre du photographe.

🙑 **Rappel**. Dans la [partie 1](https://github.com/HueyNemud/tnah-2026-partie1), nous avons exploré le graphe de connaissances de la bibliothèque nationale de France, publié sur data.bnf.fr, analysé le schéma de métadonnées *WEMI* utilisé pour structurer les métadonnées descriptives des œuvres, et extrait pour chaque photographie un graphe RDF contenant les métadonnées la décrivant. Dans le chapitre 4, les graphes individuels des photographies ont été enregistrés au format Turtle sur le disque, dans un dossier nommé `photographies/`

**⚠️ Prérequis**
- Avoir terminé la partie 1.
- Le dossier `photographies/` doit exister dans le répertoire de la partie 1 et doit contenir les fichiers `<ark>.ttl` de chaque photographie assignée à votre équipe.

<hr/>

##  🙤 Objectifs
Cette seconde partie guide la mise en place d'un processus d'extraction de l'information géographique contenue dans les métadonnées des photographies d'Eugène Atget récoltées dans la première partie.

 Elle se décompose en deux étapes :

1. D'abord enrichir les graphes de métadonnées des photographies avec les **thèmes Rameau** qui leurs sont associés, afin d'obtenir le plus possible d'indications géographiques. Cette première étape est l'occasion d'un **exercice de lecture de code** Python.

2. Ensuite, **extraire l'information géographique pertinente** dans le titre et des thèmes de chaque photographie pour obtenir un ensemble d'indications de localisation qui pourront être utilisé pour placer la photographie dans Paris et ses alentours. Cette tâche de **traitement automatique du langage naturel** sera réalisé avec un **grand modèle de langage génératif**.

Légende des pictogrammes utilisés :

| Picto. | Légende                                   |
| ------ | ----------------------------------------- |
| 🎬      | Action à réaliser : à vous de jouer !     |
| 💡      | Suggestion d'action complémentaire        |
| ⚠️      | Avertissement                             |
| ℹ️      | Information supplémentaire ou astuce      |
| 📚      | Ressources : documentation, article, etc. |
 
<hr/>

##  🙤 Chapitre 2 : extraction structurée de l'information géographique contenue dans les métadonnées des photographies

### Motivation
Le premier chapitre a permis d'ajouter à chaque graphe de photographie les informations textuelles des thèmes Rameau associés.
Par exemple :
```raw
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
```

On repère de nombreuses informations géographiques qui renseignent plus ou moins précisément sur la localisation de cette photographie:
1. Le **titre** de la photo contient un toponyme, « Au Soleil d'or », ainsi qu'une adresse postal : « 84 S.t Sauveur »
2. Les **thèmes Rameau** donnent une série d'indices géographiques supplémentaires, ex. « Paris (France) -- Rue Saint-Sauveur »

En lisant ces métadonnées, un humain peut immédiatement identifier une **hiérarchie spatiale** : 
```raw
📍 France [pays]
└── 🏙️ Paris [ville]
    └── 🛣️ rue Saint-Sauveur [rue]
        └── 🏠 n° 84 rue Saint-Sauveur [adresse]
            └── ☀️ « Au Soleil d'or » [lieu dit / enseigne]
```

Avoir une hiérarchie spatiale est extrêmement précieux pour le géocodage car on peut alors chercher à localiser une photo au niveau le plus fin, puis remonter dans la hiérarchie si cela n'est pas possible, par exemple parce que le lieu a disparu.
C'est aussi un moyen élégant de regrouper les photos par niveau de granularité spatiale.

Cette opération qui couple lecture, identification de l'information utile et déduction d'une hiérarchie est intuitive pour un humain, mais est en réalité assez complexe pour une machine. En effet, elle repose sur une compréhension contextuelle des thèmes et implique une connaissance implicite. 
Pour une machine, "Paris (France)" est juste une chaîne de caractère.
Comprendre que le texte "84 [quatre-vingt-quatre] Rue S.t Sauveur" correspond à une adresse et peut être normalisé en "84 rue Saint-Sauveur" nécessite de coder des règles spécifiques, ce qui devient rapidement à la fois lourd et fragile.
 
Heureusement, les **grands modèles de langages (LLMs)** offrent une alternative particulièrement adaptée à ce genre de tache qui mêle compréhension, extraction et génération, grâce à leurs capacités de raisonnement de haut niveau.

Pour des raisons de simplicité, l'expérimentation sera réalisée avec les modèles de **[Mistral](https://mistral.ai/fr)**.

### Un *prompt* naïf pour extraire une hiérarchie géographique dans les titres et thèmes d'une photographie.

Un grand modèle de langage peut être guidé par des instructions pour réaliser une tâche de traitement de données sans qu'il soit nécessaire de l'entraîner spécialement sur cette tâche.

Ces instructions sont rassemblées dans un texte donné au modèle  nommé **prompt**. 
S'il n'existe pas de "bible" de la rédaction de prompt, il y a quand même des règles générales qui décrivent la structure générale d'un prompt basique :

> a. Assigner un rôle au modèle pour la tache.
> b. Décrire la tâche à réaliser
> c. Si nécessaire, donner des règles spécifiques pour gérer les cas complexes, ambigus, etc.

Voici un *prompt* simpliste que l'on pourrait utiliser pour extraire et organiser l'information géographique des titres et thèmes d'une photographie : 
```raw
# Rôle
Tu es un expert en extraction d'information géographique dans des métadonnées patrimoniales.

# Tâche
Ta tâche est d'analyser un ensemble de métadonnées textuelles décrivant une photographie et d'extraire la liste des entités géographiques présentes.

# Règles
Règle spécifique : organise les entités de la plus précise à la plus générale.

Les métadonnées à analyser seront données dans le prochain input.
```

> ℹ️ Notez qu'on ne donne ici **aucun exemple** de traitement. Cette stratégie "brute" s'appelle **0-shot prompting**, par opposition au **few-shot prompting** où l'on fournit quelques exemples dans le prompt.

On peut directement essayer ce prompt en utilisant le modèle "chatbot" grand-public de Mistral, disponible à l'adresse https://chat.mistral.ai

> 🎬 Rendez-vous sur https://chat.mistral.ai, donnez le prompt ci-dessus au modèle, puis donnez le bloc de métadonnées au début de la section **Motivation**. Le modèle renvoit-il quelque chose qui vous semple directement utilisable dans un programme informatique ? Extrait-il toute l'information géographique, nom du lieu "Au Soleil d'or" compris ? Que se passe t-il si vous donnez plusieurs fois de suite les mêmes métadonnées ?

Vous l'aurez compris, ce *prompt* est beaucoup trop naïf pour fonctionner correctement. 
Un LLM, aussi puissant qu'il est, n'est pas dans votre tête - il faut le guider beaucoup plus strictement.

Il manque plusieurs éléments critiques :

1. le modèle est libre d'ajouter du texte supplémentaire dans sa réponse ;
2. on ne contraint pas le format de réponse ;
3. on explicite jamais la hiérarchie exacte à extraire.

### Un *prompt* un peu moins naïf grâce au *few-shot prompting* 

À l'heure actuelle, la manière la plus simple de contraindre fortement un LLM à produire ce que l'on souhaite consiste à lui donner des exemples.
En effet, les LLMs sont extrêmement guidés par les exemples, bien plus que par toute explication complexe qu'on pourrait leur fournir.
Cette stratégie qui consiste à donner des exemples dans les instructions à un modèle, avant d'envoyer les véritables données à traite est nommée *few-shot prompting*.

Avec un seul exemple, on peut expliquer au modèle à la fois le **format souhaité** ainsi que **la hiérarchie spatiale** attendue de façon très simple : il suffit d'ajouter au *prompt* un extrait de métadonnées à traiter, ainsi que le résultat attendu.

Disons que, lorsqu'on donne les métadonnées d'une photo au LLM, on souhaite récupérer une hiérarchie au format JSON, avec les niveaux suivants :
- Toponyme : le nom du lieu précis. S'il est présent, il est généralement dans le titre ;
- Adresse : adresse postale, donnée dans le titre également ;
- Voie : dans le titre ou les thèmes Rameau ;
- Ville : généralement dans les thèmes Rameau ;
- Pays : dans les thèmes Rameau également, ou doit être déduit.

Bien sûr, des champs peuvent être absents, il s'agit d'une hiérarchie maximale.

Voici un exemple de métadonnées, puis le résultat d'extraction attendu au format JSON :
```raw
=== PHOTO : Au Bon Puits : Rue Michel Le Comte 36 (Disparu en 1904), [photographie] ===
Lien : http://data.bnf.fr/ark:/12148/cb40268303v#about
Thèmes assignés:
 • « Vin -- Industrie et commerce » - altLabels : « Commerce vinicole », « Industrie viticole », « Commerce viticole », « Production viticole », « Production vinicole », « Industrie vinicole »
 • « Paris (France) -- Rue Michel-le-Comte » - altLabels : « Rue Michel-le-Comte (Paris, France) », « Michel-le-Comte, Rue (Paris, France) »
 • « Paris (France) »
 • « Enseignes » - altLabels : « Signes et indications », « Enseignes commerciales »
 • « Ferronnerie d'art » - altLabels : « Ferronnerie architecturale », « Ferrures », « Serrurerie d'art », « Ferronneries », « Fer forgé, Objets en », « Fer ornemental », « Ferronnerie décorative », « Ferronnerie (architecture) », « Fer forgé », « Objets en fer forgé »
 ```

```json
{
	"toponyme": "Au Bon Puits",
	"adresse": "36 rue Michel Le Comte",
	"voie": "rue Michel Le Comte",
	"ville": "Paris",
	"pays": "France"
}
```

 > 🎬 Reprenez le prompt naïf, et améliorez-le en ajoutant une section "# Exemple" contenant cet exemple d'entrée et de sortie attendue.
 > Réappliquez le traitement aux métadonnées de la section **Motivation**.
 > Le résultat devrait cette fois correspondre à ce qu'on attend, un extrait de JSON contenant la hiérarchie géographique extraite : 
 > ```json
 > { "toponyme": "Au Soleil d'or", "adresse": "84 rue Saint-Sauveur", "voie": "rue Saint-Sauveur", "ville": "Paris", "pays": "France" }
 > ```

 > 💡 Donnez à nouveau les mêmes métadonnées au LLM, plusieurs fois de suite. Est-ce que contenu et le résultat est stable ?

Ce prompt produit des résultats de qualité suffisante pour passer à l'automatisation du traitement des métadonnées grâce à Mistral... et Python 🙂

### Extraction structurée avec Mistral
 
 Il est possible d’interagir avec les modèles de Mistral en Python grâce à la bibliothèque `mistralai`.

> 🎬 Installez dès maintenant le package avec :
> ```bash
> uv add mistralai
> ```

Pour apprendre à utiliser cette bibliothèque, intéressons-nous directement au cas d'usage qui nous intéresse : **l'extraction d'information structurée** des dans textes.

> 🎬 Rendez-vous dans la documentation générale de Mistral, sur https://docs.mistral.ai, et cherchez dans le menu gauche l'entrée *Structured Output*.
> Lisez le texte de la  petite page "Structured Outputs" qui s'ouvre et répondez à ces deux questions :
> 1. Quel format structuré est géré par les modèles Mistral ?
> 2. Quelles sont les deux possibilités disponibles pour faire de l'extraction structurée ?

Commençons par ne pas suivre les conseils de Mistral en choisissant le **JSON mode**, plus simple pour des débutants.

> 🎬 Rendez-vous sur la page de description de ce mode en suivant le lien [JSON: To enforce a JSON output](https://docs.mistral.ai/capabilities/structured_output/json_mode) sur la page *Structured Output*, ou en cliquant sur le sous-menu *JSON Mode* dans le panneau gauche.
> Lisez la courte documentation en faisant attention à bien selectionner l'onglet "Python" pour voir l'exemple ... en Python  😉

> 🎬 Dans le répertoire de la partie 2, créez un nouveau fichier de script Python nommé `extract_geohierarchy.py` puis collez-y le code Python donné sous la section *How to generate JSON consistently* de la page de documentation.
> Ajouter en fin de fichier la ligne suivante pour afficher la réponse du modèle :
> ```python
> print(chat_response.choices[0].message.content)
> ```

Avant de pouvoir tester ce script, il faut d'abord renseigner votre **clé API Mistral**.
On voir dans l'extrait de code cette ligne : 
```python
api_key  =  os.environ["MISTRAL_API_KEY"]
```
Cela signifie que la valeur de la clé est lue depuis la **variable d'environnement** `MISTRAL_API_KEY`.
Il faut donc la déclarer dans votre session de terminal avant de pouvoir exécuter le script.

> 🎬 Dans votre session de terminal, déclarez votre clé Mistral ainsi :
> ```bash
> export MISTRAL_API_KEY=votre_clé_mistral_ici
> ```
> Vous pouvez ensuite lancer le script Python :
> ```bash
> uv run extract_geohierarchy.py
> ```

Vous devriez obtenir le résultat suivant :

```bash
❯ uv run ./extract_geohierarchy.py
{
  "meal": "Boeuf Bourguignon",
  "ingredients": [
    "beef",
    "red wine (Burgundy)",
    "onions",
    "carrots",
    "garlic",
    "mushrooms",
    "bacon",
    "bouquet garni",
    "beef stock",
    "butter",
    "flour",
    "salt",
    "pepper"
  ]
}
```