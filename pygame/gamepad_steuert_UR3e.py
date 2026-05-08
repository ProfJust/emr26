"""ich erstelle Ihnen ein lauffähiges Grundgerüst mit Sicherheitslogik: Deadman-Taste, Geschwindigkeitsbegrenzung, Achszuordnung und sauberem jogStop() beim Loslassen/Beenden.

Unten ist ein einfaches Python-Grundprogramm für UR3e + Gamepad + ur_rtde + pygame. jogStart() kann wiederholt neue Geschwindigkeitsvektoren übernehmen; Translation ist laut API in mm/s, Rotation in rad/s. jogStop() stoppt das Jogging.
"""
import time
import pygame
import rtde_control

ROBOT_IP = "192.168.0.10"   # <-- IP Ihres UR3e anpassen

# Sicherheitsbegrenzungen
MAX_TRANS_SPEED = 50.0      # mm/s
MAX_ROT_SPEED = 0.25        # rad/s
ACC = 0.5                   # Jog-Beschleunigung
DEADZONE = 0.12

# Feature: Basis-Koordinatensystem
FEATURE_BASE = rtde_control.RTDEControlInterface.FEATURE_BASE

# Gamepad-Zuordnung
AXIS_LX = 0      # links/rechts -> Y
AXIS_LY = 1      # vor/zurück -> X
AXIS_RX = 3      # rechter Stick X -> Rz
AXIS_RY = 4      # rechter Stick Y -> Z
DEADMAN_BUTTON = 4   # z.B. LB/L1 gedrückt halten


def apply_deadzone(value, deadzone=DEADZONE):
    if abs(value) < deadzone:
        return 0.0
    return value


def main():
    print("\a THIS SOFTWARE IS UNDER HEAVY CONSTRUCTION ")
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        raise RuntimeError("Kein Gamepad gefunden.")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Gamepad erkannt: {joystick.get_name()}")
    print("Deadman-Taste gedrückt halten zum Verfahren.")
    print("Strg+C beendet das Programm.")

    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)

    jogging_active = False

    try:
        while True:
            pygame.event.pump()

            deadman = joystick.get_button(DEADMAN_BUTTON)

            if deadman:
                lx = apply_deadzone(joystick.get_axis(AXIS_LX))
                ly = apply_deadzone(joystick.get_axis(AXIS_LY))
                rx = apply_deadzone(joystick.get_axis(AXIS_RX))
                ry = apply_deadzone(joystick.get_axis(AXIS_RY))

                # jogStart erwartet: [vx, vy, vz, rx, ry, rz]
                # Translation: mm/s, Rotation: rad/s
                speed_vector = [
                    -ly * MAX_TRANS_SPEED,   # X vor/zurück
                     lx * MAX_TRANS_SPEED,    # Y links/rechts
                    -ry * MAX_TRANS_SPEED,   # Z hoch/runter
                    0.0,                     # Rotation um X
                    0.0,                     # Rotation um Y
                    rx * MAX_ROT_SPEED       # Rotation um Z
                ]

                rtde_c.jogStart(speed_vector, FEATURE_BASE, ACC)
                jogging_active = True

            else:
                if jogging_active:
                    rtde_c.jogStop()
                    jogging_active = False

            time.sleep(0.02)  # ca. 50 Hz

    except KeyboardInterrupt:
        print("Programm wird beendet.")

    finally:
        try:
            rtde_c.jogStop()
        except Exception:
            pass

        rtde_c.disconnect()
        pygame.quit()


if __name__ == "__main__":
    main()