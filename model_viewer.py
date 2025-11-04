"""Live2D model viewer with interactive controls - Optimized for fast external expressions."""

import math
import time
import threading
import queue
from dataclasses import dataclass
from typing import Optional, ClassVar
import os

import pygame
from pygame.locals import DOUBLEBUF, OPENGL

import live2d.v3 as live2d
from live2d.v3 import StandardParams
from live2d.utils.lipsync import WavHandler

from utils.manage_model import ModelManager
from utils.get_emotion import corresp_emotion
from utils import lenght_to_duration

from speech.TTS import init_model_TTS, synthesize_audio

@dataclass
class ViewConfig:
    """Configuration for the Live2D viewer."""
    width: int = 500
    height: int = 600
    title: str = "Live2D Viewer"
    frame_delay: int = 10
    background_color: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)


@dataclass
class TransformState:
    """State for model transformations."""
    dx: float = 0.0
    dy: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    rotation_speed: float = math.pi * 10 / 1000 * 0.5
    rotation_amplitude: float = 1.0


class EmotionProcessor:
    """Thread-safe emotion processing handler with optimized processing."""
    
    def __init__(self):
        self.input_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue(maxsize=10)
        self.worker_thread = None
        self.running = False
        self.processing_lock = threading.Lock()
        
    def start(self):
        """Start the emotion processing thread."""
        self.running = True
        self.worker_thread = threading.Thread(
            target=self._process_worker,
            daemon=True,
            name="EmotionProcessorThread"
        )
        self.worker_thread.start()
        print("[EmotionProcessor] Thread démarré")
    
    def stop(self):
        """Stop the emotion processing thread."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                self.input_queue.put(None, timeout=0.1)
            except queue.Full:
                pass
            self.worker_thread.join(timeout=2.0)
        print("[EmotionProcessor] Thread arrêté")
    
    def _process_worker(self):
        """Worker thread qui traite les émotions de manière asynchrone."""
        print("[EmotionProcessor] Worker thread en cours d'exécution")
        
        while self.running:
            try:
                # Timeout réduit pour réactivité accrue
                text = self.input_queue.get(timeout=0.1)
                
                if text is None:
                    break
                
                print(f"[EmotionProcessor] Traitement de: '{text}'")
                
                with self.processing_lock:
                    try:
                        emotion_id = corresp_emotion(text)
                        self.result_queue.put({
                            'text': text,
                            'emotion_id': emotion_id,
                            'success': True,
                            'timestamp': time.time()
                        })
                        print(f"[EmotionProcessor] Résultat: {emotion_id}")
                    except Exception as e:
                        print(f"[EmotionProcessor] Erreur lors du traitement: {e}")
                        self.result_queue.put({
                            'text': text,
                            'emotion_id': None,
                            'success': False,
                            'error': str(e),
                            'timestamp': time.time()
                        })
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[EmotionProcessor] Erreur dans le worker: {e}")
    
    def submit_text(self, text: str) -> bool:
        """Soumettre un texte pour traitement."""
        try:
            self.input_queue.put_nowait(text)
            return True
        except queue.Full:
            print("[EmotionProcessor] Queue pleine, texte ignoré")
            return False
    
    def get_result(self) -> Optional[dict]:
        """Récupérer un résultat si disponible."""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None


class Live2DViewer:
    """Interactive Live2D model viewer with threading support and singleton pattern."""
    
    # Singleton pattern avec thread safety
    _instance: ClassVar[Optional['Live2DViewer']] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()
    _initialized: ClassVar[threading.Event] = threading.Event()
    
    # Queue d'entrée externe accessible depuis n'importe où
    _external_queue: ClassVar[queue.Queue] = queue.Queue(maxsize=50)

    def __init__(self, model_manager: ModelManager, config: ViewConfig = ViewConfig()):
        self.config = config
        self.model_manager = model_manager
        self.model: Optional[live2d.LAppModel] = None
        self.transform = TransformState()
        self.running = False
        self.current_expression_idx = 0
        self.expressions = []
        self.part_ids = []
        self.highlighted_part_id: Optional[str] = None
        
        # Threading components
        self.emotion_processor = EmotionProcessor()
        
        # Cooldown optimisé pour les expressions externes
        self.last_expression_time = 0
        self.last_expression_duration = 0
        self.expression_cooldown = 2
        self.external_expression_cooldown = 1
        self.pending_expression = None
        
        # Audio & LipSync
        self.wavHandler = None
        self.lipSyncN = 3
        self.audioPlayed = False

        self.tss = init_model_TTS()

        self.expression_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> Optional['Live2DViewer']:
        """Récupérer l'instance singleton (si elle existe)."""
        return cls._instance
    
    @classmethod
    def wait_for_instance(cls, timeout: float = 10.0) -> Optional['Live2DViewer']:
        """Attendre que l'instance soit initialisée."""
        if cls._initialized.wait(timeout):
            return cls._instance
        return None
    
    @classmethod
    def send_text(cls, text: str, priority: bool = True) -> bool:
        """
        Méthode statique pour envoyer du texte depuis n'importe où.
        Thread-safe et non-bloquante.
        
        Args:
            text: Le texte à traiter
            priority: Si True, utilise un cooldown réduit
        """

        try:
            cls._external_queue.put_nowait({'text': text, 'priority': priority})
            print(f"[External] Texte ajouté à la queue: '{text}' (priority={priority})")
            return True
        except queue.Full:
            print(f"[External] Queue externe pleine, texte ignoré: '{text}'")
            return False
    
    @classmethod
    def send_emotion_direct(cls, emotion_id: str) -> bool:
        """
        Envoyer directement un emotion_id sans passer par corresp_emotion.
        Le plus rapide pour les appels externes.
        """
        try:
            cls._external_queue.put_nowait({
                'emotion_id': emotion_id,
                'direct': True,
                'priority': True
            })
            print(f"[External] Emotion directe ajoutée: '{emotion_id}'")
            return True
        except queue.Full:
            print(f"[External] Queue externe pleine, emotion ignorée: '{emotion_id}'")
            return False

    def on_start_motion_callback(self, group: str, no: int):
        """Callback appelé au démarrage d'une motion - GÈRE LE LIPSYNC"""
        print(f"\n=== 🎬 MOTION START CALLBACK ===")
        print(f"Groupe: {group}, No: {no}")
        
        self.audioPath = "output.wav"
        print(f"Chemin audio: {os.path.abspath(self.audioPath)}")
        print(f"Fichier existe: {os.path.exists(self.audioPath)}")
        
        if os.path.exists(self.audioPath):
            try:
                pygame.mixer.music.load(self.audioPath)
                pygame.mixer.music.play()
                print("✓ Audio chargé et lancé")
                
                self.wavHandler.Start(self.audioPath)
                print("✓ WavHandler démarré pour lip sync")
            except Exception as e:
                print(f"✗ Erreur callback: {e}")
        else:
            print(f"✗ Fichier audio introuvable!")
            wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
            print(f"Fichiers WAV disponibles: {wav_files}")
    
    def on_finish_motion_callback(self):
        """Callback appelé à la fin d'une motion"""
        print("🏁 Motion terminée")

    def initialize(self) -> None:
        """Initialize pygame, Live2D, and load the model."""
        with self._lock:
            if Live2DViewer._instance is not None:
                raise RuntimeError("Une instance de Live2DViewer existe déjà!")
            Live2DViewer._instance = self
        
        pygame.init()
        pygame.mixer.init()
        live2d.init()
        live2d.setLogEnable(True)

        pygame.display.set_mode(
            (self.config.width, self.config.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(self.config.title)

        if live2d.LIVE2D_VERSION == 3:
            live2d.glewInit()

        self._load_model()
        
        # Initialiser le WavHandler
        self.wavHandler = WavHandler()
        
        # Démarrer les threads après l'initialisation du modèle
        self.emotion_processor.start()
        # Signaler que l'instance est prête
        Live2DViewer._initialized.set()
        
        print("=== Live2D Viewer (Mode Rapide) ===")
        print("Contrôles:")
        print("- Flèches: Déplacer le modèle")
        print("- I/U: Zoomer/Dézoomer")
        print("- R: Réinitialiser")
        print("- E: Changer d'expression")
        print("- SPACE: Tester l'audio + lip sync")
        print("- Tapez du texte dans la console pour changer l'expression")
        print("\nAPI externe (rapide):")
        print("  Live2DViewer.send_text('texte')  # Passe par corresp_emotion")
        print("  Live2DViewer.send_emotion_direct('f01')  # Direct, le plus rapide!")
        print(f"\nExpressions disponibles: {self.expressions}")
        print("- Ctrl+C ou fermez la fenêtre pour quitter")
        print("====================================")

    def update_wav_handler(self):
        """Met à jour le lip sync basé sur l'audio"""
        if self.wavHandler.Update():
            rms_value = self.wavHandler.GetRms()
            mouth_value = rms_value * self.lipSyncN
            self.model.SetParameterValue(StandardParams.ParamMouthOpenY, mouth_value)
            # DEBUG: décommenter pour voir les valeurs
            # print(f"🎤 RMS: {rms_value:.4f} | Bouche: {mouth_value:.4f}")
        else:
            # Remettre la bouche à zéro quand pas d'audio
            if not pygame.mixer.music.get_busy():
                self.model.SetParameterValue(StandardParams.ParamMouthOpenY, 0.0)

    def text_to_file_path(self, text):
        FORBIDDEN_CHARS = [" ", ".", "/"]

        for char in FORBIDDEN_CHARS:
            text.replace(char, "")
        return text+".wav"

    def make_sound(self, text):
        """Test manuel de l'audio + lip sync"""

        self.audioPath = self.text_to_file_path(text)

        audio, duration = synthesize_audio(self.tss, text, self.audioPath)

        print(f"\n=== 🔊 TEST AUDIO MANUEL ===")
        print(f"Chemin: {os.path.abspath(self.audioPath)}")
        print(f"Existe: {os.path.exists(self.audioPath)}")
        return (audio, duration)

    def play_sound(self):
        if os.path.exists(self.audioPath):
            try:
                pygame.mixer.music.load(self.audioPath)
                pygame.mixer.music.play()
                print("✓ Audio chargé et lancé")
                
                self.wavHandler.Start(self.audioPath)
                print("✓ WavHandler démarré pour lip sync")
            except Exception as e:
                print(f"✗ Erreur: {e}")
        else:
            print(f"✗ Fichier introuvable!")
            wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
            print(f"Fichiers WAV trouvés: {wav_files}")

    def _load_model(self) -> None:
        """Load and configure the Live2D model."""
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(str(self.model_manager.path))
        
        self.expressions = self.model.GetExpressionIds()
        print(f"Expressions disponibles: {self.expressions}")
        
        if self.expressions:
            self.model.AddExpression(self.expressions[0])
            print(f"Expression initiale: {self.expressions[0]}")

        self.model.Resize(self.config.width, self.config.height)
        self.model.SetAutoBlinkEnable(True)
        self.model.SetAutoBreathEnable(False)  # Désactivé pour éviter conflits
        
        self.part_ids = self.model.GetPartIds()
        
        self._log_model_info()
        
        # 🔥 CORRECTION PRINCIPALE : Enregistrer les callbacks !
        print("\n🔧 Enregistrement des callbacks de motion...")
        self.model.StartRandomMotion(
            "TapBody", 
            300, 
            self.on_start_motion_callback,  # ← START callback
            self.on_finish_motion_callback   # ← FINISH callback
        )
        print("✓ Callbacks enregistrés\n")

    def _log_model_info(self) -> None:
        """Log model parameters and information."""
        print(f"Canvas size: {self.model.GetCanvasSize()}")
        print(f"Canvas size (pixels): {self.model.GetCanvasSizePixel()}")
        print(f"Pixels per unit: {self.model.GetPixelsPerUnit()}")
        print(f"Part count: {len(self.part_ids)}")
        print(f"Parameter count: {self.model.GetParameterCount()}")

    def _check_threading_inputs(self) -> None:
        """Check for inputs from all sources (optimized)."""
        # Vérifier la queue externe (prioritaire)
        processed_count = 0
        max_per_frame = 3
        
        while processed_count < max_per_frame:
            try:
                data = self._external_queue.get_nowait()
                processed_count += 1
                
                if isinstance(data, dict) and data.get('direct'):
                    emotion_id = data.get('emotion_id')
                    if emotion_id:
                        print(f"[Main] Emotion directe reçue: '{emotion_id}'")
                        self._apply_expression_fast(emotion_id, priority=True)
                    continue
                
                if isinstance(data, dict):
                    text = data.get('text')
                    priority = data.get('priority', False)
                    if text:
                        print(f"[Main] Texte externe reçu: '{text}' (priority={priority})")
                        self.emotion_processor.submit_text(text)
                else:
                    print(f"[Main] Texte externe reçu: '{data}'")
                    self.emotion_processor.submit_text(data)
                    
            except queue.Empty:
                break
        
        # Vérifier les résultats du processeur d'émotions
        result = self.emotion_processor.get_result()
        if result:
            self._handle_emotion_result(result)

    def _handle_emotion_result(self, result: dict) -> None:
        """Handle emotion processing result (optimized)."""
        if not result['success']:
            print(f"[Main] Échec du traitement pour '{result['text']}': {result.get('error', 'Unknown')}")
            return

        text = result['text']
        emotion_id = result['emotion_id']

        print(f"[Main] Résultat reçu pour '{text}': {emotion_id}")

        # Lecture du TTS — aucune restriction
        try:
            self.audio_tts, self.duration_last_tts = self.make_sound(text)
        except Exception as e:
            print(f"[Main] Erreur lors du play_sound: {e}")

        # Application d’une expression avec son propre cooldown interne
        if emotion_id and emotion_id in self.expressions:
            self._apply_expression_fast(emotion_id, priority=False)
        else:
            print(f"[Main] Expression '{emotion_id}' non disponible")
            if emotion_id:
                print(f"       Expressions disponibles: {self.expressions}")

    def _apply_expression_fast(self, expression_id: str, priority: bool = False) -> bool:
        """
        Appliquer une expression avec durée visible et cooldown optimisé.
        """
        current_time = time.time()
        cooldown = self.external_expression_cooldown if priority else self.expression_cooldown
        expression_duration = 1.5  # durée pendant laquelle l'expression reste affichée (secondes)

        # Empêcher un spam d'expressions trop rapprochées
        if current_time - self.last_expression_time < cooldown:
            remaining = cooldown - (current_time - self.last_expression_time)
            print(f"[Main] Cooldown actif: attendez {remaining:.2f}s avant de rejouer une expression")
        else:
            try:
                self.model.ResetExpressions()
                self.model.AddExpression(expression_id)

                self.play_sound()
                
                self.last_expression_time = current_time
                print(f"[Main] Expression appliquée: {expression_id}")

                # Maintenir l'expression pendant un certain temps, puis reset
                threading.Timer(expression_duration, self.model.ResetExpressions).start()

            except Exception as e:
                print(f"[Main] Erreur lors de l'application de l'expression: {e}")


    def _apply_expression(self, expression_id: str) -> None:
        """Apply an expression to the model (legacy method)."""
        self._apply_expression_fast(expression_id, priority=False)

    def _handle_keyboard(self, key: int) -> None:
        """Handle keyboard input."""
        transform_map = {
            pygame.K_LEFT: ('dx', -0.1),
            pygame.K_RIGHT: ('dx', 0.1),
            pygame.K_o: ('dy', 0.1),
            pygame.K_l: ('dy', -0.1),
            pygame.K_i: ('scale', 0.1),
            pygame.K_u: ('scale', -0.1),
        }

        if key in transform_map:
            attr, delta = transform_map[key]
            setattr(self.transform, attr, getattr(self.transform, attr) + delta)
            print(f"Transform: {attr} = {getattr(self.transform, attr):.2f}")
        
        elif key == pygame.K_SPACE:
            self.play_sound("C'est un petit test comme ca")
        
        elif key == pygame.K_r:
            self._reset_model()
            print("Modèle réinitialisé")
        
        elif key == pygame.K_e:
            self._cycle_expression()

    def _reset_model(self) -> None:
        """Reset model to default state."""
        self.model.StopAllMotions()
        self.model.ResetPose()
        self.model.ResetExpression()

    def _cycle_expression(self) -> None:
        """Cycle to the next expression."""
        if not self.expressions:
            return
        
        self.current_expression_idx = (self.current_expression_idx + 1) % len(self.expressions)
        self._apply_expression(self.expressions[self.current_expression_idx])
        print(f"Expression cyclée: {self.expressions[self.current_expression_idx]}")

    def _handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """Handle mouse motion for dragging and part highlighting."""
        self.model.Drag(*pos)
        self._update_highlighted_part(pos)

    def _update_highlighted_part(self, pos: tuple[int, int]) -> None:
        """Update the highlighted part based on mouse position."""
        if self.highlighted_part_id:
            pidx = self.part_ids.index(self.highlighted_part_id)
            self.model.SetPartOpacity(pidx, 1.0)
            self.model.SetPartMultiplyColor(pidx, 1.0, 1.0, 1.0, 1.0)
        
        hit_parts = self.model.HitPart(*pos, False)
        self.highlighted_part_id = hit_parts[0] if hit_parts else None

    def _apply_transformations(self) -> None:
        """Apply all transformations to the model."""
        self.transform.rotation += self.transform.rotation_speed
        rotation_deg = math.sin(self.transform.rotation) * self.transform.rotation_amplitude
        
        self.model.Rotate(rotation_deg)
        self.model.SetOffset(self.transform.dx, self.transform.dy)
        self.model.SetScale(self.transform.scale)

    def _render_highlighted_part(self) -> None:
        """Render the highlighted part with visual feedback."""
        if not self.highlighted_part_id:
            return
        
        pidx = self.part_ids.index(self.highlighted_part_id)
        self.model.SetPartOpacity(pidx, 0.5)
        self.model.SetPartMultiplyColor(pidx, 0.0, 0.0, 1.0, 0.9)

    def _process_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event.key)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(pygame.mouse.get_pos())

    def run(self) -> None:
        """Main rendering loop."""
        self.running = True
        
        print("\n[Main] Boucle principale démarrée")
        print("[Main] Prêt à recevoir des inputs...")
        
        frame_count = 0
        
        while self.running:
            frame_count += 1
            
            # Vérifier les inputs des threads
            self._check_threading_inputs()
            
            # Traiter les événements pygame
            self._process_events()
            
            if not self.running:
                break
            
            # Appliquer les transformations
            self._apply_transformations()
            
            self.update_wav_handler()
            
            # Mise à jour du modèle
            self.model.Update()
            self._render_highlighted_part()
            
            # Rendu
            live2d.clearBuffer(*self.config.background_color)
            self.model.Draw()
            
            pygame.display.flip()
            pygame.time.wait(self.config.frame_delay)
        
        print(f"[Main] Boucle principale terminée ({frame_count} frames)")

    def cleanup(self) -> None:
        """Cleanup resources and stop threads."""
        print("[Main] Nettoyage en cours...")
        
        self.emotion_processor.stop()
        with self._lock:
            Live2DViewer._instance = None
            Live2DViewer._initialized.clear()
        
        time.sleep(0.2)
        
        try:
            live2d.dispose()
        except Exception as e:
            print(f"[Main] Erreur lors du dispose de Live2D: {e}")
        
        try:
            pygame.quit()
        except Exception as e:
            print(f"[Main] Erreur lors du quit de pygame: {e}")
        
        print("[Main] Nettoyage terminé")


def main():
    """Entry point for the Live2D viewer."""
    model_manager = ModelManager("llny")
    viewer = Live2DViewer(model_manager)

    try:
        viewer.initialize()
        viewer.run()
    except KeyboardInterrupt:
        print("\n[Main] Arrêt demandé par l'utilisateur (Ctrl+C)...")
    except Exception as e:
        print(f"[Main] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        viewer.cleanup()


if __name__ == "__main__":
    main()