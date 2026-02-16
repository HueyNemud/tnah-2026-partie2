# 🙤 **PARTIE 2** 🙧
# Extraction structurée des indices géographiques dans les métadonnées des photographies d'[Eugène Atget](https://fr.wikipedia.org/wiki/Eug%C3%A8ne_Atget) 

🙑 Au-delà de son volume, l'œuvre d'Eugène Atget frappe par la méticulosité de son classement. Véritable archiviste de son propre travail, l’auteur a systématiquement indexé ses clichés, les structurant en séries et en albums thématiques. Chaque cliché est doté d'un titre décrivant son sujet et sa localisation, souvent très précisément.

Ces titres, systématiquement relevés et transcrits, font parti des métadonnées associées à chaque photographie. Les archivistes ne se sont cependant pas arrêté là et ont enrichi la description structurée de chaque cliché avec des thèmes issus du thésaurus Rameau.

La richesse géographique de ces métadonnées permet aujourd'hui d'envisager une cartographie du fonds dans l’espace parisien. Cette approche, image par image, offrirait un parcours inédit au cœur de la capitale et renouvellerait notre regard sur l’œuvre du photographe.

🙑 **Rappel**. Dans la [partie 1](https://github.com/HueyNemud/tnah-2026-partie1), nous avons exploré le graphe de connaissances de la bibliothèque nationale de France, publié sur data.bnf.fr, analysé le schéma de métadonnées *WEMI* utilisé pour structurer les métadonnées descriptives des œuvres, et extrait pour chaque photographie un graphe RDF contenant les métadonnées la décrivant. Dans le chapitre 4, les graphes individuels des photographies ont été enregistrés au format Turtle sur le disque, dans un dossier nommé `photographies/`

## ⚠️ Prérequis

- Avoir terminé la partie 1.
- Le dossier `photographies/` doit exister dans le répertoire de la partie 1 et doit contenir les fichiers `<ark>.ttl` de chaque photographie assignée à votre équipe.

<hr/>

## 🙤 Objectifs

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

## 🙤 Chapitre 1 : enrichissement des graphes de photographies avec leurs thèmes Rameau

### Préparation

> 🎬 Copiez le dossier `photographies/` de la partie 1 vers le répertoire de la partie 2. Vérifiez qu'il contient bien l'ensemble de fichiers `.ttl` des graphes des photographies assignées à votre équipe.

### Motivation

Le dernier chapitre de la partie 1 a abouti à la création d'une multitudes de petits graphes contenant chacun les métadonnées d'une photographie, stockés dans un répertoire `photographies/`. Chacun contient deux ressources  décrivant la photographie suivant le modèle *WEMI* : sa **manifestation** et son **expression**. La dernière, de type **skos:Concept**, représente la notice documentaire de l’œuvre et fait le pont avec le catalogue général de la BnF.

Le graphe de la photographie `https://catalogue.bnf.fr/ark:/12148/cb40268288s` (Intérieur de M.r A., Industriel [Image fixe] : Rue Lepic) contient par exemple :

```turtle
# -------------------
# Représente la notice documentaire de la photographie
# -------------------
<http://data.bnf.fr/ark:/12148/cb40268288s> a skos:Concept ;
    dcterms:created "1990-10-19" ;
    dcterms:modified "2022-12-13" ;
    foaf:focus <http://data.bnf.fr/ark:/12148/cb40268288s#about> .

# -------------------
# La ressource de type Manifestation
# -------------------
<http://data.bnf.fr/ark:/12148/cb40268288s#about> a <http://rdaregistry.info/Elements/c/#C10007>, <http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation> ;
    ns7:FRBNF 40268288 ;
    dcterms:date "1910/1911" ;
    dcterms:description "1 photogr. pos. sur papier albuminé : d'après négatif sur verre au gélatinobromure ; 22,6 x 17,6 cm (épr.)" ;
    dcterms:subject <http://data.bnf.fr/ark:/12148/cb11932931q>,
        <http://data.bnf.fr/ark:/12148/cb11939981z>,
        <http://data.bnf.fr/ark:/12148/cb11940294d>,
        <http://data.bnf.fr/ark:/12148/cb11978491g>,
        <http://data.bnf.fr/ark:/12148/cb13162676c>,
        <http://data.bnf.fr/ark:/12148/cb166888940> ;
    dcterms:title "Intérieur de M.r A., Industriel : Rue Lepic, [photographie]" ;
    ns3:P30016 <https://gallica.bnf.fr/ark:/12148/btv1b105069316> ;
    ns3:P30139 <http://data.bnf.fr/ark:/12148/cb40268288s#Expression> ;
    ns3:P30279 "France" ;
    ns2:P60470 "Technique de l'image : photographie positive. - papier albuminé. - procédé au bromure d'argent. - verre. Note : Num. de nég. coupé dans l'épr. en b. à dr." ;
    ns4:note "Technique de l'image : photographie positive. - papier albuminé. - procédé au bromure d'argent. - verre. Note : Num. de nég. coupé dans l'épr. en b. à dr." ;
    ns5:electronicReproduction <https://gallica.bnf.fr/ark:/12148/btv1b105069316> ;
    ns5:expressionManifested <http://data.bnf.fr/ark:/12148/cb40268288s#Expression> ;
    rdfs:seeAlso <https://catalogue.bnf.fr/ark:/12148/cb40268288s> .

# -------------------
# La ressource de type Expression
# -------------------
<http://data.bnf.fr/ark:/12148/cb40268288s#Expression> a <http://rdaregistry.info/Elements/c/#C10006>,
        <http://rdvocab.info/uri/schema/FRBRentitiesRDA/Expression> ;
    ns6:r530 <http://data.bnf.fr/ark:/12148/cb11889340k#about> ;
    ns1:pht <http://data.bnf.fr/ark:/12148/cb11889340k#about> ;
    dcterms:contributor <http://data.bnf.fr/ark:/12148/cb11889340k#about> ;
    dcterms:language <http://id.loc.gov/vocabulary/iso639-2/fre> ;
    dcterms:subject <http://data.bnf.fr/ark:/12148/cb11932931q>,
        <http://data.bnf.fr/ark:/12148/cb11939981z>,
        <http://data.bnf.fr/ark:/12148/cb11940294d>,
        <http://data.bnf.fr/ark:/12148/cb11978491g>,
        <http://data.bnf.fr/ark:/12148/cb13162676c>,
        <http://data.bnf.fr/ark:/12148/cb166888940> ;
    dcterms:type dcmitype:StillImage ;
    owl:sameAs <http://data.bnf.fr/ark:/12148/cb40268288s#frbr:Expression> .
```

> 🎬 Dans ce graphe, repérez :
>
> - quelle **propriété** représente le **titre** et quelle est la **ressource** qui porte cette information.
> - quelle **propriété** représente les **thèmes RAMEAU** associés à la photographie et quelles sont les **ressources** qui portent cette information. N'hésitez pas à ouvrir les URIs dans votre navigateur pour trouver lesquelles identifient des thèmes Rameau.

Sur la page de présentation d'un thème, par exemple data.bnf.fr/ark:/12148/cb166888940, on voit qu'il possède un titre ainsi de nombreuses autres informations : domaine, relations liées, formes alternatives, concepts plus généraux ou plus précis, etc.

Le titre et les formes alternatives sont particulièrement intéressantes car, lorsque le thème est géographique, c'est là qu'on va trouver des indications spatiales qu'on pourra mettre à profit pour une phase ultérieure de géocodage.

L'enjeu est donc de **récupérer ces informations** et **enrichir chaque graphe de photographie** avec les titres et les formes alternatives des thèmes rameaux qui lui sont associés.

### Anatomie d'un script Python pour automatiser l'enrichissement des graphes

Dans le dossier courant se trouve un fichier nommé `fetch_themes.py` qui définit un ensemble de fonctions Python. Elles forment des briques élémentaires de traitement que l'on peut assembler pour former un algorithme d'enrichissement complet d'un graphe de photographie.

> 🎬 Ouvrez ce fichier dans votre IDE et parcourez le une première fois globalement pour comprendre son organisation générale.
> Après cette première lecture:
>
> 1. reportez ici ou dans un fichier texte les **signatures des fonctions** du fichier, c'est à dire leur nom, leurs paramètres et leur type de leur retour s'il existe.
> 2. Collectivement, dessinez le **graphe de flux** de l'enrichissement d'un graphe. Le point de départ est un fichier `.ttl` d'un graphe de photographie, et on veut arriver à un nouveau fichier `.ttl` enrichi qui contient les titres et les noms alternatifs des thèmes Rameau associés à la photographie. Comment chaîner les différentes fonctions disponibles pour passer de l'état initial à l'état enrichi ?

Tracer le graphe de flux d'une donnée permet de comprendre comment les différentes fonctions doivent être agencées en un algorithme d'enrichissement d'un graphe.

> 🎬 Collectivement, écrivez sous la forme d'un pseudo-code l'algorithme complet d'enrichissement :
>
> 1. d'un seul graphe de photographie : on part d'un fichier `photographies/<ark>.ttl` et on doit arriver à un fichier `photographies_avec_themes/<ark>.ttl`
> 2. tous les graphes de photographies du dossier `photographies/` : même logique que 1. mais avec tous les fichiers `.ttl`

Une fois l'algorithme écrit :

> 🎬Ouvrez le fichier `main.txt` : il contient le point d'entrée d'un script Python qui implémente l'algorithme d'enrichissement pour tous les graphes de photographies.
>
> 1. Copiez son contenu et collez le dans `fetch_themes.py` juste après le bloc  `# --- D. POINT D'ENTRÉE DU SCRIPT`
> 2. Implémentez l'algorithme d'enrichissement à l'intérieur de la boucle principale.

### Enrichissement des graphes

Doté de son point d'entrée, le fichier `fetch_themes.py` est maintenant un script Python exécutable depuis le terminal.
Une fois lancé, il enrichira le nombre de graphes fixés par la valeur de `graph_processing_limit`.

> 🎬 Exécutez une première fois le script sur 3 fichiers, en définissant `graph_processing_limit = 3`.
>
> ```bash
> uv run fetch_themes.py
> ```
>
> Un fois certain.e.s que le script fonctionne correctement, retirez la limite de traitement puis relancez le script.
> Ouvrez finalement quelques uns des fichiers `.html` de vos graphe enrichis pour vérifier qu'ils contiennent bien les titres et labels des thèmes Rameau récupérés.

<hr/>

### 🏁 Fin du chapitre 1

 Ce premier chapitre a permis de découvrir et comprendre un fichier Python "professionnel" contenant un code d'enrichissement des graphes produits dans la partie 1.
 Cet enrichissement permet de récupérer de nombreuses informations sur une photographie, donc certaines contenant des indices géographiques pouvant servir au géocodage.

Il est temps de passer au **chapitre 2** pour apprendre à extraite spécifiquement cette information géographique pour pouvoir l'exploiter par la suite.
