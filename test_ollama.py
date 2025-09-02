
"""
Script de test pour vérifier la configuration Ollama
"""

import ollama
import sys

def test_ollama_connection():
    """Teste la connexion à Ollama"""
    try:
        # Test de connexion basique
        print("🔍 Test de connexion à Ollama...")
        models = ollama.list()
        print(f"✅ Connexion réussie! Modèles disponibles: {len(models['models'])}")
        
        for model in models['models']:
            print(f"  - {model['name']} ({model['size']})")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à Ollama: {str(e)}")
        print("💡 Assurez-vous qu'Ollama est installé et en cours d'exécution:")
        print("   ollama serve")
        return False

def test_mistral_model():
    """Teste le modèle Mistral"""
    try:
        print("\n🤖 Test du modèle Mistral...")
        
        # Test simple
        response = ollama.chat(model='mistral', messages=[
            {
                'role': 'user',
                'content': 'Dis-moi bonjour en français'
            }
        ])
        
        print("✅ Modèle Mistral fonctionne!")
        print(f"📝 Réponse: {response['message']['content'][:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec le modèle Mistral: {str(e)}")
        print("💡 Assurez-vous que le modèle est téléchargé:")
        print("   ollama pull mistral")
        return False

def test_email_generation():
    """Teste la génération de réponse d'email"""
    try:
        print("\n📧 Test de génération de réponse d'email...")
        
        test_email = """
        Bonjour,
        
        J'aimerais avoir des informations sur vos services.
        Pouvez-vous me contacter au plus vite ?
        
        Cordialement,
        Jean Dupont
        """
        
        prompt = f"""
        En tant qu'assistant professionnel, veuillez répondre à cet email de manière professionnelle et concise.
        Voici le contenu de l'email à traiter :

        {test_email}

        Veuillez fournir une réponse appropriée.
        """
        
        response = ollama.chat(model='mistral', messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        print("✅ Génération de réponse d'email réussie!")
        print(f"📝 Réponse générée: {response['message']['content'][:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la génération de réponse: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de configuration Ollama pour l'agent email\n")
    
    # Tests
    tests = [
        test_ollama_connection,
        test_mistral_model,
        test_email_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Résumé
    print("=" * 50)
    print(f"📊 Résumé: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Votre configuration Ollama est prête.")
        print("💡 Vous pouvez maintenant lancer l'agent email:")
        print("   python email_agent.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        print("💡 Consultez le README.md pour plus d'informations.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 