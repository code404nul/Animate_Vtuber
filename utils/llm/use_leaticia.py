import ollama
from utils.llm.memory_manager import MemoryManager

class OllamaChat:
    def __init__(self, model_name: str, max_turns: int = 20):
        """
        Initialise le chat avec un modèle Ollama
        
        Args:
            model_name: Nom du modèle dans Ollama
            max_turns: Nombre maximum de tours à retenir en mémoire
        """
        self.model_name = model_name
        self.memory = MemoryManager(max_turns=max_turns)
    
    def generate_response(self, user_message: str, stream: bool = True) -> str:
        """
        Génère une réponse avec le modèle
        
        Args:
            user_message: Message de l'utilisateur
            stream: Si True, affiche la réponse en streaming
            
        Returns:
            Réponse générée par le modèle
        """
        # Ajoute le message utilisateur
        self.memory.add_message('user', user_message)
        
        # Récupère le contexte (fenêtre glissante automatique)
        messages = self.memory.get_context()
        
        try:
            response_content = ""
            
            if stream:
                print(f"\n🤖 Assistant: ", end="", flush=True)
                
                stream_response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )
                
                for chunk in stream_response:
                    content = chunk['message']['content']
                    print(content, end="", flush=True)
                    response_content += content
                
                print()
            else:
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    stream=False
                )
                response_content = response['message']['content']
                print(f"\n🤖 Assistant: {response_content}")
            
            # Ajoute la réponse au contexte
            self.memory.add_message('assistant', response_content)
            
            return response_content
            
        except ollama.ResponseError as e:
            print(f"\n❌ Erreur Ollama: {e}")
            return ""
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            return ""
    
    def clear_memory(self):
        """Efface la mémoire"""
        self.memory.clear()
        print("✨ Mémoire effacée")
    
    def show_memory_info(self):
        """Affiche les informations sur la mémoire"""
        print(f"\n📊 État de la mémoire:")
        print(self.memory.get_summary())
    
    def show_context(self):
        """Affiche l'historique en mémoire"""
        context = self.memory.get_context()
        print("\n📜 Contexte actuel en mémoire:")
        for i, msg in enumerate(context, 1):
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
            print(f"{i}. {role_emoji} {msg['role']}: {preview}")
