import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import ollama
from imap_tools import MailBox, AND
import time
from mcp_manager import MCPManager

# Charger les variables d'environnement
load_dotenv()

# Configuration Ollama avec le modèle Mistral local
# Assurez-vous que votre modèle Mistral est disponible localement avec: ollama pull mistral
model_name = 'mistral'  # ou le nom exact de votre modèle Mistral local

# Initialiser le gestionnaire MCP
mcp_manager = MCPManager()

def load_excel_data():
    """Charge les données depuis le fichier Excel"""
    try:
        df = pd.read_excel('data.xlsx', engine='openpyxl')
        return df
    except FileNotFoundError:
        print("Le fichier data.xlsx n'existe pas. Veuillez le créer avec vos données.")
        return None

def connect_to_mailbox():
    """Fonction pour établir une connexion IMAP"""
    try:
        mailbox = MailBox(os.getenv('IMAP_SERVER'))
        mailbox.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        return mailbox
    except Exception as e:
        print(f"Erreur de connexion IMAP: {str(e)}")
        return None

def mark_email_as_read(mailbox, email_uid):
    """Marque un email comme lu"""
    try:
        mailbox.fetch(criteria=f'UID {email_uid}', mark_seen=True)
        return True
    except Exception as e:
        print(f"Erreur lors du marquage de l'email comme lu: {str(e)}")
        return False

def generate_response(email_content):
    """Génère une réponse en utilisant le modèle Ollama Mistral local"""
    try:
        # Vérifier si le contenu de l'email est vide
        if not email_content or not email_content.strip():
            return "Je ne peux pas traiter un email vide. Veuillez me fournir plus d'informations."

        # Préparation du prompt
        prompt = f"""
        En tant qu'assistant professionnel, veuillez répondre à cet email de manière professionnelle et concise.
        Voici le contenu de l'email à traiter :

        {email_content}

        Veuillez fournir une réponse appropriée.
        """

        # Génération de la réponse avec Ollama
        try:
            response = ollama.chat(model=model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
        except Exception as e:
            print(f"Erreur lors de la génération avec Ollama: {str(e)}")
            print("Vérifiez que:")
            print("1. Ollama est installé et en cours d'exécution")
            print("2. Le modèle Mistral est disponible (ollama pull mistral)")
            print("3. Le nom du modèle est correct")
            return "Je suis désolé, il y a un problème technique avec le service de réponse automatique. Veuillez réessayer plus tard."
        
        # Vérifier si la réponse est valide
        if not response or not response.get('message', {}).get('content'):
            return "Je suis désolé, je n'ai pas pu générer une réponse appropriée. Veuillez réessayer plus tard."

        return response['message']['content'].strip()

    except Exception as e:
        print(f"Erreur lors de la génération de la réponse : {str(e)}")
        return "Je suis désolé, une erreur s'est produite lors du traitement de votre email. Veuillez réessayer plus tard."

def check_new_emails():
    """Vérifie les nouveaux emails et les traite"""
    try:
        print("Tentative de connexion au serveur IMAP...")
        print(f"Serveur IMAP: {os.getenv('IMAP_SERVER')}")
        print(f"Port IMAP: {os.getenv('IMAP_PORT')}")
        print(f"Utilisateur: {os.getenv('EMAIL_USER')}")
        print(f"Source Email: {os.getenv('SOURCE_EMAIL')}")
        
        # Vérifier si les variables d'environnement sont définies
        if not all([os.getenv('IMAP_SERVER'), os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'), os.getenv('SOURCE_EMAIL')]):
            print("Erreur: Variables d'environnement manquantes")
            print("Vérifiez que votre fichier .env contient:")
            print("- IMAP_SERVER")
            print("- EMAIL_USER")
            print("- EMAIL_PASSWORD")
            print("- SOURCE_EMAIL")
            return False

        # Première connexion
        mailbox = connect_to_mailbox()
        if not mailbox:
            print("Échec de la connexion initiale au serveur IMAP")
            return False

        print("Connexion au serveur IMAP établie")
        print("Login réussi")

        # Marquer tous les emails existants comme lus
        print("Marquage des emails existants comme lus...")
        try:
            for email in mailbox.fetch(criteria='UNSEEN'):
                mark_email_as_read(mailbox, email.uid)
        except Exception as e:
            print(f"Erreur lors du marquage des emails existants: {str(e)}")
            mailbox = connect_to_mailbox()
            if not mailbox:
                print("Échec de la reconnexion au serveur IMAP")
                return False

        print("En attente de nouveaux emails...")
        last_check_time = time.time()
        processed_emails = set()  # Pour garder une trace des emails déjà traités
        
        while True:
            try:
                current_time = time.time()
                # Vérifier toutes les 30 secondes si la connexion est toujours active
                if current_time - last_check_time >= 30:
                    print("Vérification de la connexion...")
                    mailbox = connect_to_mailbox()
                    if not mailbox:
                        print("Échec de la reconnexion au serveur IMAP")
                        return False
                    last_check_time = current_time

                # Vérifier les nouveaux emails non lus
                print("Vérification des nouveaux emails...")
                new_emails = list(mailbox.fetch(criteria='UNSEEN', mark_seen=False))
                
                if new_emails:
                    print(f"{len(new_emails)} nouveau(x) email(s) trouvé(s)")
                    
                    for email in new_emails:
                        try:
                            # Vérifier si l'email a déjà été traité
                            email_id = f"{email.uid}_{email.date}"
                            if email_id in processed_emails:
                                print(f"Email déjà traité: {email_id}")
                                continue

                            print(f"Email trouvé de: {email.from_}")
                            # Vérifier si l'email provient de l'adresse source
                            if email.from_ != os.getenv('SOURCE_EMAIL'):
                                print(f"Email ignoré de {email.from_} (n'est pas l'adresse source)")
                                continue

                            print(f"Nouvel email reçu de {email.from_}...")
                            print(f"Sujet: {email.subject}")
                            
                            # Vérifier si l'email a un contenu
                            if not email.text:
                                print(f"L'email de {email.from_} est vide, ignoré.")
                                continue

                            # Générer la réponse
                            print("Génération de la réponse...")
                            response_content = generate_response(email.text)
                            
                            if not response_content:
                                print(f"Impossible de générer une réponse pour l'email de {email.from_}")
                                continue

                            # Envoyer l'email
                            print("Envoi de la réponse...")
                            if send_email(email.from_, response_content):
                                # Marquer l'email comme lu
                                if mark_email_as_read(mailbox, email.uid):
                                    print(f"Email marqué comme lu: {email.uid}")
                                    # Ajouter l'email à la liste des emails traités
                                    processed_emails.add(email_id)
                                else:
                                    print(f"Échec du marquage de l'email comme lu: {email.uid}")
                            else:
                                print(f"Échec de l'envoi de la réponse à {email.from_}")
                                
                        except Exception as e:
                            print(f"Erreur lors du traitement de l'email de {email.from_}: {str(e)}")
                            mailbox = connect_to_mailbox()
                            if not mailbox:
                                print("Échec de la reconnexion au serveur IMAP")
                                return False
                            continue
                else:
                    print("Aucun nouvel email trouvé")

                # Attendre 5 secondes avant la prochaine vérification
                time.sleep(5)

            except Exception as e:
                print(f"Erreur lors de la vérification des emails : {str(e)}")
                mailbox = connect_to_mailbox()
                if not mailbox:
                    print("Échec de la reconnexion au serveur IMAP")
                    return False
                time.sleep(5)

    except Exception as e:
        print(f"Erreur détaillée lors de la vérification des emails : {str(e)}")
        print(f"Type d'erreur : {type(e).__name__}")
        return False
    finally:
        try:
            if mailbox:
                mailbox.logout()
                print("Déconnexion finale du serveur IMAP")
        except:
            pass
    
    return True

def extract_information_with_ollama(email_content):
    """Utilise Ollama Mistral pour extraire les informations importantes de l'email"""
    prompt = f"""
    Analyse cet email et extrait les informations clés pour la recherche dans la base de données :
    {email_content}
    
    Retourne un dictionnaire JSON avec les informations suivantes :
    - question_principale : la question principale posée
    - mots_cles : liste des mots-clés importants
    - contexte : contexte supplémentaire si pertinent
    """
    
    try:
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Erreur lors de l'extraction d'informations avec Ollama: {str(e)}")
        return "{}"

def search_in_excel(data, extracted_info):
    """Recherche les informations dans le fichier Excel"""
    # Convertir les informations extraites en minuscules pour la recherche
    search_terms = extracted_info.lower()
    
    # Rechercher dans toutes les colonnes
    matching_rows = data[data.astype(str).apply(lambda x: x.str.lower().str.contains(search_terms, na=False)).any(axis=1)]
    
    return matching_rows

def generate_response_with_ollama(original_email, excel_data):
    """Génère une réponse avec Ollama Mistral en utilisant le MCP"""
    # Mettre à jour le contexte MCP
    mcp_manager.update_email_context(
        sender=original_email.from_,
        subject=original_email.subject,
        content=original_email.text
    )
    
    # Extraire les informations avec Ollama
    extracted_info = extract_information_with_ollama(original_email.text)
    try:
        mcp_manager.update_extracted_info(eval(extracted_info))  # Convertir la chaîne JSON en dict
    except:
        print("Erreur lors de l'évaluation des informations extraites")
        mcp_manager.update_extracted_info({})
    
    # Rechercher dans Excel
    matching_data = search_in_excel(excel_data, extracted_info)
    mcp_manager.update_dataset_info(matching_data.to_dict('records'))
    
    # Générer la réponse
    response_content = generate_response(original_email.text)
    
    # Sauvegarder le contexte dans l'historique
    mcp_manager.save_to_history()
    
    return response_content

def send_email(to_email, content):
    """Envoie un email avec le contenu formaté"""
    try:
        if content is None:
            print(f"Impossible d'envoyer l'email à {to_email}: contenu vide")
            return False

        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = to_email
        msg['Subject'] = "Vos informations de contact"

        msg.attach(MIMEText(content, 'plain'))

        with smtplib.SMTP_SSL(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            server.send_message(msg)
            print(f"Email envoyé avec succès à {to_email}")
            return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
        return False

def format_email_content(row):
    """Formate le contenu de l'email avec les données de la ligne"""
    try:
        # Vérifier si toutes les colonnes nécessaires existent
        required_columns = ['nom', 'prenom', 'telephone', 'adresse', 'code_postal', 'ville', 'pays']
        for col in required_columns:
            if col not in row or pd.isna(row[col]):
                print(f"Attention: La colonne '{col}' est manquante ou vide dans les données")
                row[col] = ""  # Remplacer les valeurs None par une chaîne vide

        # Formater le contenu de l'email
        content = f"""
        Bonjour {row['prenom']} {row['nom']},

        Voici vos informations de contact :
        Téléphone : {row['telephone']}
        Adresse : {row['adresse']}
        Code postal : {row['code_postal']}
        Ville : {row['ville']}
        Pays : {row['pays']}

        Cordialement,
        Votre application
        """
        return content.strip()
    except Exception as e:
        print(f"Erreur lors du formatage de l'email : {str(e)}")
        return None

def main():
    # Charger les données Excel
    excel_data = load_excel_data()
    if excel_data is None:
        return
    
    while True:
        try:
            # Vérifier les nouveaux emails
            if check_new_emails():
                # Réinitialiser le contexte MCP
                mcp_manager.clear_context()
            
            # Attendre 5 minutes avant la prochaine vérification
            time.sleep(300)
            
        except Exception as e:
            print(f"Une erreur est survenue: {str(e)}")
            time.sleep(60)  # Attendre 1 minute en cas d'erreur

if __name__ == "__main__":
    main() 