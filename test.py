import math
import os
import time

import pygame
from pygame.locals import *

import live2d.v3 as live2d
from live2d.v3 import StandardParams
from live2d.utils import log
import resources
from live2d.utils.lipsync import WavHandler

live2d.setLogEnable(True)


def main():
    pygame.init()
    pygame.mixer.init()
    live2d.init()

    display = (500, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("pygame window")

    if live2d.LIVE2D_VERSION == 3:
        live2d.glewInit()

    model = live2d.LAppModel()
    model.LoadModelJson("resources/v3/llny/llny.model3.json")
    model.Resize(*display)

    running = True
    dx: float = 0.0
    dy: float = 0.0
    scale: float = 1.0

    model.SetAutoBlinkEnable(False)
    model.SetAutoBreathEnable(False)

    wavHandler = WavHandler()
    lipSyncN = 3

    # CORRECTION 1: Retirer audioPlayed ou le mettre à False pour tester
    audioPlayed = False

    def on_start_motion_callback(group: str, no: int):
        log.Info("start motion: [%s_%d]" % (group, no))
        # CORRECTION 2: Chemin absolu ou relatif correct
        audioPath = "output.wav"  # Assurez-vous que ce fichier existe !
        
        print(f"\n=== CALLBACK MOTION START ===")
        print(f"Groupe: {group}, No: {no}")
        print(f"Chemin audio: {os.path.abspath(audioPath)}")
        print(f"Fichier existe: {os.path.exists(audioPath)}")
        
        if os.path.exists(audioPath):
            try:
                pygame.mixer.music.load(audioPath)
                pygame.mixer.music.play()
                print("✓ Audio chargé et lancé")
                wavHandler.Start(audioPath)
                print("✓ WavHandler démarré")
            except Exception as e:
                print(f"✗ Erreur callback: {e}")
        else:
            print(f"✗ Fichier audio introuvable!")
            wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
            print(f"Fichiers WAV disponibles: {wav_files}")

    def on_finish_motilback():
        log.Info("motion finished")

    for i in range(model.GetParameterCount()):
        param = model.GetParameter(i)
        log.Debug(
            param.id, param.type, param.value, param.max, param.min, param.default
        )

    partIds = model.GetPartIds()
    currentTopClickedPartId = None

    def getHitFeedback(x, y):
        t = time.time()
        hitPartIds = model.HitPart(x, y, False)
        if currentTopClickedPartId is not None:
            pidx = partIds.index(currentTopClickedPartId)
            model.SetPartOpacity(pidx, 1)
            model.SetPartMultiplyColor(pidx, 1.0, 1.0, 1., 1)
        if len(hitPartIds) > 0:
            ret = hitPartIds[0]
            return ret

    fc = None
    sc = None
    model.StartRandomMotion("TapBody", 300, sc, fc)

    radius_per_frame = math.pi * 10 / 1000 * 0.5
    deg_max = 5
    progress = 0
    deg = math.sin(progress) * deg_max 

    print("canvas size:", model.GetCanvasSize())
    print("canvas size in pixels:", model.GetCanvasSizePixel())
    print("pixels per unit:", model.GetPixelsPerUnit())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                model.SetExpression("plaisir")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx -= 0.1
                elif event.key == pygame.K_RIGHT:
                    dx += 0.1
                elif event.key == pygame.K_UP:
                    dy += 0.1
                elif event.key == pygame.K_DOWN:
                    dy -= 0.1
                elif event.key == pygame.K_i:
                    scale += 0.1
                elif event.key == pygame.K_u:
                    scale -= 0.1
                elif event.key == pygame.K_r:
                    model.StopAllMotions()
                    model.ResetPose()
                elif event.key == pygame.K_e:
                    model.ResetExpression()
                # CORRECTION 4: Ajouter une touche pour tester le son directement
                elif event.key == pygame.K_SPACE:
                    audioPath = "output.wav"
                    print(f"\n=== TEST AUDIO MANUEL ===")
                    print(f"Chemin: {os.path.abspath(audioPath)}")
                    print(f"Existe: {os.path.exists(audioPath)}")
                    if os.path.exists(audioPath):
                        try:
                            pygame.mixer.music.load(audioPath)
                            pygame.mixer.music.play()
                            print("✓ Audio chargé et lancé")
                            wavHandler.Start(audioPath)
                            print("✓ WavHandler démarré")
                        except Exception as e:
                            print(f"✗ Erreur: {e}")
                    else:
                        print(f"✗ Fichier introuvable!")
                        # Lister les fichiers WAV disponibles
                        wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
                        print(f"Fichiers WAV trouvés: {wav_files}")

            if event.type == pygame.MOUSEMOTION:
                model.Drag(*pygame.mouse.get_pos())
                currentTopClickedPartId = getHitFeedback(*pygame.mouse.get_pos())

        if not running:
            break

        progress += radius_per_frame
        deg = math.sin(progress) * deg_max
        model.Rotate(deg)

        model.Update()

        if currentTopClickedPartId is not None:
            pidx = partIds.index(currentTopClickedPartId)
            model.SetPartOpacity(pidx, 0.5)
            model.SetPartMultiplyColor(pidx, .0, .0, 1., .9)

        # CORRECTION 5: Toujours mettre à jour le lip sync avec DEBUG
        if wavHandler.Update():
            rms_value = wavHandler.GetRms()
            mouth_value = rms_value * lipSyncN
            model.SetParameterValue(StandardParams.ParamMouthOpenY, mouth_value)
            # DEBUG ACTIVÉ
            print(f"🎤 RMS: {rms_value:.4f} | Bouche: {mouth_value:.4f}")
        else:
            # Afficher quand wavHandler n'est pas actif
            if pygame.mixer.music.get_busy():
                print("⚠️  Audio joue mais wavHandler.Update() retourne False")

        # CORRECTION 6: Code de test supprimé (était inutile et bloquant)

        model.SetOffset(dx, dy)
        model.SetScale(scale)
        live2d.clearBuffer(1.0, 0.0, 0.0, 0.0)
        model.Draw()
        pygame.display.flip()
        pygame.time.wait(10)

    live2d.dispose()
    pygame.quit()
    quit()


if __name__ == "__main__":
    currentTopClickedPartId = None
    main()