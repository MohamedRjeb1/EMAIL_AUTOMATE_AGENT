from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class EmailContext:
    """Structure pour stocker le contexte de l'email"""
    sender: str
    subject: str
    content: str
    extracted_info: Dict[str, Any]
    dataset_info: Dict[str, Any]

class MCPManager:
    def __init__(self):
        self.context = EmailContext(
            sender="",
            subject="",
            content="",
            extracted_info={},
            dataset_info={}
        )
        self.history: List[EmailContext] = []
    
    def update_email_context(self, sender: str, subject: str, content: str):
        """Met à jour le contexte avec un nouvel email"""
        self.context.sender = sender
        self.context.subject = subject
        self.context.content = content
    
    def update_extracted_info(self, info: Dict[str, Any]):
        """Met à jour les informations extraites par Gemini"""
        self.context.extracted_info = info
    
    def update_dataset_info(self, info: Dict[str, Any]):
        """Met à jour les informations du dataset"""
        self.context.dataset_info = info
    
    def get_context_prompt(self) -> str:
        """Génère le prompt complet avec le contexte"""
        return f"""
        Contexte de l'email :
        - Expéditeur : {self.context.sender}
        - Sujet : {self.context.subject}
        - Contenu : {self.context.content}
        
        Informations extraites :
        {json.dumps(self.context.extracted_info, ensure_ascii=False, indent=2)}
        
        Informations du dataset :
        {json.dumps(self.context.dataset_info, ensure_ascii=False, indent=2)}
        """
    
    def save_to_history(self):
        """Sauvegarde le contexte actuel dans l'historique"""
        self.history.append(self.context)
    
    def clear_context(self):
        """Réinitialise le contexte actuel"""
        self.context = EmailContext(
            sender="",
            subject="",
            content="",
            extracted_info={},
            dataset_info={}
        ) 