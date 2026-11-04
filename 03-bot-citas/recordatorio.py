"""Avisa por Telegram las citas proximas. Uso: python recordatorio.py [horas]"""
import os
import sys

import requests

import main


def formatear(cita):
    return (
        f"Cita #{cita['id']}\n"
        f"{cita['fecha_hora']}\n"
        f"{cita['nombre']} - {cita['telefono']}\n"
        f"Servicio: {cita['servicio']}"
    )


def main_():
    horas = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT_ID", "")

    citas = main.citas_proximas(horas)
    if not citas:
        print(f"Sin citas en las proximas {horas} horas")
        return 0

    for cita in citas:
        texto = formatear(cita)
        if token and chat:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat, "text": texto},
                timeout=20,
            )
            estado = "enviado" if r.ok else f"error {r.status_code}"
        else:
            estado = "solo consola"
        print(f"--- {estado}")
        print(texto)

    return 0


if __name__ == "__main__":
    sys.exit(main_())