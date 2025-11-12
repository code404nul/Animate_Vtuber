from typing import List, Dict
from collections import deque

class MemoryManager:
    def __init__(self, max_turns: int = 20):
        """
        Gestionnaire de mémoire avec fenêtre glissante
        
        Args:
            max_turns: Nombre maximum de tours de conversation à retenir
                      (1 tour = 1 message user + 1 message assistant)
        """
        self.max_turns = max_turns
        self.conversation_history: deque = deque(maxlen=max_turns * 2)
        # maxlen * 2 car chaque tour = 2 messages (user + assistant)
        self.total_messages = 0
    
    def add_message(self, role: str, content: str):
        """
        Ajoute un message à l'historique
        
        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        self.total_messages += 1
    
    def get_context(self, include_all: bool = False) -> List[Dict[str, str]]:
        """
        Récupère le contexte de conversation
        
        Args:
            include_all: Si False, utilise la fenêtre glissante
            
        Returns:
            Liste des messages dans le contexte
        """
        if include_all:
            return list(self.conversation_history)
        
        # Retourne les derniers messages (fenêtre glissante automatique)
        return list(self.conversation_history)
    
    def clear(self):
        """Efface tout l'historique"""
        self.conversation_history.clear()
        self.total_messages = 0
    
    def get_turn_count(self) -> int:
        """Retourne le nombre de tours de conversation"""
        return len(self.conversation_history) // 2
    
    def get_memory_info(self) -> Dict:
        """Retourne des informations sur l'état de la mémoire"""
        current_turns = self.get_turn_count()
        return {
            'current_turns': current_turns,
            'max_turns': self.max_turns,
            'total_messages': self.total_messages,
            'messages_in_memory': len(self.conversation_history),
            'memory_full': current_turns >= self.max_turns,
            'oldest_message_forgotten': self.total_messages > self.max_turns * 2
        }
    
    def get_summary(self) -> str:
        """Retourne un résumé de l'état de la mémoire"""
        info = self.get_memory_info()
        
        status = "🟢 Mémoire disponible"
        if info['memory_full']:
            status = "🟡 Fenêtre glissante active (oublie les anciens messages)"
        
        return (f"{status}\n"
                f"Tours actuels: {info['current_turns']}/{info['max_turns']}\n"
                f"Messages totaux échangés: {info['total_messages']}")
