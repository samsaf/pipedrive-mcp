# Guide d'utilisation — Serveur MCP Pipedrive

Ce serveur connecte Claude directement à votre CRM Pipedrive. Vous pouvez gérer vos contacts, deals, organisations, leads et activités en langage naturel.

---

## Configuration

### Claude Desktop

1. Ouvrez **Settings** > **Développeur** > **Modifier la config**
2. Ajoutez dans `mcpServers` :

```json
{
  "mcpServers": {
    "pipedrive": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://pipedrive-mcp-server.vercel.app/mcp",
        "--header",
        "Authorization: Bearer VOTRE_TOKEN"
      ]
    }
  }
}
```

3. Redémarrez Claude Desktop
4. Vous devriez voir les outils Pipedrive (icône marteau) en bas du chat

### Claude Code

```bash
claude mcp add pipedrive --transport http https://pipedrive-mcp-server.vercel.app/mcp -H "Authorization: Bearer VOTRE_TOKEN"
```

> Demandez le token d'accès (`VOTRE_TOKEN`) à votre administrateur.

---

## Ce que vous pouvez faire

### 1. Personnes (Contacts)

#### Chercher une personne
> "Cherche le contact Jean Dupont dans Pipedrive"
>
> "Trouve tous les contacts de l'organisation Acme"
>
> "Recherche les personnes dont l'email contient @google.com"

#### Consulter une fiche personne
> "Montre-moi les détails du contact #42"
>
> "Affiche les infos de Marie Martin avec ses champs personnalisés"

#### Créer un contact
> "Crée un nouveau contact : Pierre Durand, email pierre@example.com, téléphone 06 12 34 56 78, organisation #15"
>
> "Ajoute un contact Jean Petit avec le label 'VIP' dans le champ personnalisé customer_type"

#### Modifier un contact
> "Change l'email de la personne #123 en nouveau@email.com"
>
> "Mets à jour le téléphone du contact Jean Dupont"
>
> "Mets le champ personnalisé 'lead_source' à 'Salon 2026' pour le contact #45"

#### Supprimer un contact
> "Supprime le contact #789"

---

### 2. Deals (Affaires)

#### Lister les deals
> "Montre-moi tous les deals en cours"
>
> "Liste les deals du pipeline 'Ventes France' au statut 'open'"
>
> "Affiche les deals mis à jour cette semaine"
>
> "Quels sont les deals de Marie (owner #5) ?"

#### Chercher un deal
> "Cherche le deal 'Licence logiciel Acme'"
>
> "Trouve les deals liés à l'organisation #200"

#### Consulter un deal
> "Montre-moi les détails du deal #311"
>
> "Affiche le deal #50 avec le champ personnalisé 'Linkedin like'"

#### Créer un deal
> "Crée un deal 'Renouvellement contrat Acme' à 15000€, pipeline Ventes, stage Négociation, lié à l'organisation #42"
>
> "Nouveau deal : 'Licence SaaS' pour 5000 USD, probabilité 75%, date de clôture prévue le 30/06/2026"

#### Modifier un deal
> "Passe le deal #311 en statut 'won'"
>
> "Change la valeur du deal #42 à 20000€"
>
> "Mets le champ personnalisé 'Linkedin like' à 1 sur le deal #311"
>
> "Déplace le deal #100 au stage 'Proposition envoyée'"

#### Supprimer un deal
> "Supprime le deal #789"

#### Gérer les produits d'un deal
> "Mets à jour le produit #5 du deal #42 : prix unitaire 500€, quantité 10"
>
> "Retire le produit #5 du deal #42"

---

### 3. Organisations

#### Lister les organisations
> "Montre-moi toutes les organisations"
>
> "Liste les organisations mises à jour depuis le 1er mars"

#### Chercher une organisation
> "Cherche l'organisation 'Ahead Digital'"
>
> "Trouve les organisations dont l'adresse contient 'Paris'"

#### Consulter une organisation
> "Affiche les détails de l'organisation #100"

#### Créer une organisation
> "Crée l'organisation 'Startup XYZ', adresse '10 rue de Rivoli, Paris', industrie 'Tech'"

#### Modifier une organisation
> "Change le nom de l'organisation #100 en 'Nouveau Nom SA'"
>
> "Mets à jour l'adresse de l'organisation #50"

#### Supprimer une organisation
> "Supprime l'organisation #200"

#### Gérer les followers
> "Ajoute l'utilisateur #5 comme follower de l'organisation #100"
>
> "Retire le follower #12 de l'organisation #100"

---

### 4. Leads (Prospects)

#### Lister les leads
> "Montre-moi tous les leads actifs"
>
> "Liste les leads archivés"
>
> "Quels sont les leads de l'utilisateur #3 ?"

#### Chercher un lead
> "Cherche le lead 'Prospect ABC'"

#### Consulter un lead
> "Affiche les détails du lead adf21080-0e10-11eb-879b-05d71fb426ec"

> **Note** : les leads utilisent des identifiants UUID, pas des numéros.

#### Créer un lead
> "Crée un lead 'Nouveau prospect' à 5000€, lié à la personne #123"
>
> "Nouveau lead : 'Contact Salon Tech', organisation #50, date de clôture prévue 15/09/2026"

#### Modifier un lead
> "Passe le lead 'Prospect ABC' en archivé"
>
> "Change la valeur du lead à 10000€"
>
> "Mets la visibilité du lead à 'toute l'entreprise'"

#### Supprimer un lead
> "Supprime le lead adf21080-0e10-11eb-879b-05d71fb426ec"

#### Consulter les labels et sources
> "Quels sont les labels de leads disponibles ?"
>
> "Liste les sources de leads Pipedrive"

---

### 5. Activités (Tâches, Appels, Réunions)

#### Lister les activités
> "Montre-moi mes activités à venir"
>
> "Liste les activités liées au deal #42"
>
> "Quelles sont les activités de la personne #123 ?"

#### Consulter une activité
> "Affiche les détails de l'activité #55"

#### Créer une activité
> "Crée un appel avec Jean Dupont (personne #123) pour demain à 14h, durée 30 minutes"
>
> "Planifie une réunion 'Démo produit' le 15/04/2026 à 10h, liée au deal #42, avec une note 'Préparer la présentation'"
>
> "Ajoute une tâche 'Envoyer le devis' pour le deal #311, due le 28/03/2026"

#### Modifier une activité
> "Marque l'activité #55 comme terminée"
>
> "Reporte l'activité #55 au 20/04/2026"
>
> "Change la note de l'activité #55"

#### Supprimer une activité
> "Supprime l'activité #55"

#### Types d'activités
> "Quels sont les types d'activités disponibles ?"
>
> "Crée un nouveau type d'activité 'Webinar' avec l'icône 'default'"

---

### 6. Recherche globale

#### Recherche multi-types
> "Cherche 'Acme' dans tous les types (deals, personnes, organisations)"
>
> "Recherche 'Jean' uniquement dans les personnes et les leads"

#### Recherche par champ spécifique
> "Cherche dans le champ 'email' des personnes la valeur 'jean@acme.com'"
>
> "Recherche dans le champ 'title' des deals le terme 'renouvellement'"

---

## Champs personnalisés (Custom Fields)

Les champs personnalisés sont identifiés par une **clé technique** (ex: `cf8d3660109dadde43b15d5fe8d70e796e1040f9`). Vous n'avez pas besoin de connaître ces clés — demandez simplement à Claude en utilisant le nom du champ :

> "Mets à jour le champ 'Linkedin like' du deal #311 à la valeur 1"

Claude trouvera automatiquement la clé technique via l'outil de recherche de champs, puis effectuera la mise à jour.

### Entités supportées pour les custom fields

| Action | Personnes | Organisations | Deals | Leads |
|--------|-----------|---------------|-------|-------|
| Lecture | Oui | Oui | Oui | - |
| Écriture (create/update) | Oui | Oui | Oui | - |

---

## Astuces

- **Pas besoin de connaître les ID** : demandez à Claude de chercher d'abord, il trouvera les ID tout seul.
  > "Trouve le deal 'Licence Acme' et passe-le en statut gagné"

- **Enchaînez les actions** : Claude peut combiner plusieurs opérations.
  > "Crée une organisation 'Tech Corp', puis crée un contact 'Marie Durand' liée à cette organisation, puis crée un deal 'Contrat annuel' à 10000€ lié aux deux"

- **Demandez des résumés** : Claude peut analyser vos données.
  > "Fais-moi un résumé de tous les deals en cours avec leur valeur totale"
  >
  > "Quels deals ont une date de clôture dépassée ?"

- **Visibilité** : quand vous créez ou modifiez un élément, vous pouvez contrôler qui le voit :
  - `1` = Propriétaire uniquement
  - `2` ou `3` = Groupe du propriétaire
  - `7` = Toute l'entreprise

---

## Limites connues

- Les **leads** utilisent des UUID (et non des ID numériques)
- La **recherche** nécessite au minimum 2 caractères
- Les résultats de liste sont paginés (par défaut 50 éléments, max 500)
- Les champs personnalisés en lecture sont limités à 15 par requête pour les personnes
- Le serveur est en **lecture/écriture** : les suppressions sont définitives

---

## Besoin d'aide ?

Si Claude ne trouve pas un outil ou retourne une erreur :
1. Vérifiez que le serveur MCP est bien connecté (icône marteau visible dans Claude Desktop)
2. Si l'icône est rouge, redémarrez Claude Desktop
3. Contactez votre administrateur si le problème persiste
