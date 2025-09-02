# Agent Email avec Ollama Mistral Finetuned

Ce projet utilise un modèle Ollama Mistral local pour traiter automatiquement les emails entrants et générer des réponses appropriées.

## Prérequis

### 1. Installation d'Ollama

Suivez les instructions d'installation sur [ollama.ai](https://ollama.ai) :

**Windows :**
```bash
# Téléchargez et installez Ollama depuis https://ollama.ai
# Puis dans PowerShell :
ollama serve
```

**Linux/macOS :**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### 2. Téléchargement du modèle Mistral

```bash
ollama pull mistral
```

### 3. Installation des dépendances Python

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Variables d'environnement

Créez un fichier `.env` avec les informations suivantes :

```env
# Configuration Email
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_USER=votre_email@gmail.com
EMAIL_PASSWORD=votre_mot_de_passe_app
SOURCE_EMAIL=email_source@example.com

# Configuration SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

### 2. Configuration du modèle

Dans `email_agent.py`, vous pouvez modifier le nom du modèle :

```python
model_name = 'mistral'  # ou le nom exact de votre modèle local
```

## Utilisation

### 1. Vérification d'Ollama

Assurez-vous qu'Ollama fonctionne :

```bash
ollama list
```

Vous devriez voir `mistral` dans la liste.

### 2. Test du modèle

```bash
ollama run mistral "Bonjour, comment allez-vous ?"
```

### 3. Lancement de l'agent

```bash
python email_agent.py
```

## Fonctionnalités

- **Traitement automatique des emails** : L'agent surveille la boîte de réception et traite les nouveaux emails
- **Génération de réponses intelligentes** : Utilise le modèle Mistral local pour générer des réponses contextuelles
- **Extraction d'informations** : Analyse le contenu des emails pour extraire les informations clés
- **Recherche dans Excel** : Recherche dans une base de données Excel pour des informations pertinentes
- **Gestion des erreurs** : Gestion robuste des erreurs de connexion et de génération

## Modèles Ollama disponibles

Vous pouvez utiliser d'autres modèles Ollama en modifiant `model_name` :

- `mistral` (recommandé)
- `llama2`
- `codellama`
- `neural-chat`
- `vicuna`

Pour voir tous les modèles disponibles :
```bash
ollama list
```

## Dépannage

### Erreur de connexion Ollama
```bash
# Vérifiez qu'Ollama est en cours d'exécution
ollama serve

# Dans un autre terminal, testez la connexion
ollama run mistral "test"
```

### Modèle non trouvé
```bash
# Téléchargez le modèle
ollama pull mistral

# Vérifiez qu'il est disponible
ollama list
```

### Erreur de génération
- Vérifiez que le modèle est correctement téléchargé
- Assurez-vous qu'Ollama a suffisamment de ressources (RAM/GPU)
- Vérifiez les logs pour plus de détails

## Avantages d'Ollama local

- **Confidentialité** : Toutes les données restent sur votre machine
- **Pas de coûts API** : Aucun coût d'utilisation
- **Performance** : Réponses rapides sans latence réseau
- **Personnalisation** : Possibilité de fine-tuner le modèle
- **Hors ligne** : Fonctionne sans connexion internet

## Structure du projet

```
MCP_EMAIL_TEST/
├── email_agent.py      # Agent principal avec Ollama
├── mcp_manager.py      # Gestionnaire MCP
├── create_excel.py     # Création du fichier Excel
├── data.xlsx          # Base de données
├── requirements.txt   # Dépendances Python
└── README.md         # Documentation
``` 
