import random
import time
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
from datetime import datetime

# Durée d'une journée simulée (24h en minutes)
journee_minutes = (24 * 60)+1  
# Accélération (1 seconde réelle = 6 minutes simulées)
minutes_par_seconde = 12  
# Adresse du registre où l'ensoleillement sera stockée
HEURE_REGISTER = 0  # Heure
MINUTE_REGISTER = 1 # Minute
ENSOLEILLEMENT_REGISTER = 2  # Ensoleillement
PROGRAMME_REGISTER = 3  # reglage ensoleillement
MODE_REGISTER = 4  # Mode (0 HIVER, 1 été)
VOLET_REGISTER = 5  # Volet (0 fermé, 1 ouvert)
LEVER_REGISTER = 6  # Heure de lever du soleil (float*100)
COUCHER_REGISTER = 7  # Heure de coucher du soleil (float*100)


def update_time_registers(context, slave_id=0x00):
    """Met à jour les registres Modbus avec l'heure et la minute système."""
    while True:
        now = datetime.now()
        heure = now.hour
        minute = now.minute
        # Ecriture dans les registres Modbus
        context[slave_id].setValues(3, HEURE_REGISTER, [heure])
        context[slave_id].setValues(3, MINUTE_REGISTER, [minute])
        time.sleep(1)

def Simulation_heures(context, journee_minutes, minutes_par_seconde, slave_id=0x00):
    """Simule le passage du temps dans une journée, écrit heure/minute/ensoleillement dans les registres Modbus, et génère ensoleillement_values dépendant de l'heure simulée."""
    # Mode non interactif, juste image finale
    while True:
        # Lever et coucher du soleil aléatoires pour chaque journée (heures et minutes)
        lever_h = random.randint(6, 7)
        lever_m = random.randint(0, 59) if lever_h < 8 else 0
        coucher_h = random.randint(20, 21)
        coucher_m = random.randint(0, 59) if coucher_h < 22 else 0
        lever = lever_h + lever_m / 60
        coucher = coucher_h + coucher_m / 60
        print(f"Lever du soleil : {lever_h:02d}h{lever_m:02d} -> coucher du soleil : {coucher_h:02d}h{coucher_m:02d}")
        # Écriture des heures de lever et coucher dans les registres Modbus (format hhmm, ex: 6.50 -> 650)
        context[slave_id].setValues(3, LEVER_REGISTER, [int(lever*100)])
        context[slave_id].setValues(3, COUCHER_REGISTER, [int(coucher*100)])
        minutes = 0
    # Suppression du stockage et de l'affichage de la courbe
        while minutes < journee_minutes:
            heures = minutes // 60
            mins = minutes % 60
            heure_float = heures + mins/60
            # Calcul de l'ensoleillement en fonction de l'heure simulée et du lever/coucher
            taux_ensoleillement = ensoleillement(heure_float, lever, coucher)
            # Mise à jour des registres Modbus
            context[slave_id].setValues(3, HEURE_REGISTER, [heures])
            context[slave_id].setValues(3, MINUTE_REGISTER, [mins])
            context[slave_id].setValues(3, ENSOLEILLEMENT_REGISTER, [int(taux_ensoleillement)])
            # (Pas de stockage ni d'affichage de courbe)
            # Pause d'une seconde (temps réel)
            time.sleep(1)
            # Avancer dans le temps simulé
            minutes += minutes_par_seconde
    # (Pas d'affichage ni de sauvegarde de courbe)

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [101]*100),
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100)
    )
    context = ModbusServerContext(devices=device, single=True)

    # On n'utilise que l'heure simulée, pas d'heure réelle

    # Lancement du thread de simulation d'heure (heure/minute simulées)
    sim_heures_thread = Thread(target=Simulation_heures, args=(context, journee_minutes, minutes_par_seconde))
    sim_heures_thread.daemon = True
    sim_heures_thread.start()


def ensoleillement(t, lever, coucher):
    # Courbe linéaire en fonction du lever et coucher du soleil
    if t < lever or t > coucher:
        return 0
    elif lever <= t < 12:
        # Monte de 0 à 100% entre lever et milieu
        return (t - lever) / (12 - lever) * 100
    elif 12 <= t <= coucher:
        # Redescend de 100% à 0% entre milieu et coucher
        return (1 - (t - 12) / (coucher - 12)) * 100

def volet():
    while True:
        mode = context[0x00].getValues(3, MODE_REGISTER, count=1)[0]
        heure = context[0x00].getValues(3, HEURE_REGISTER, count=1)[0]
        minute = context[0x00].getValues(3, MINUTE_REGISTER, count=1)[0]
        programme = context[0x00].getValues(3, PROGRAMME_REGISTER, count=1)[0]
        ensoleillement = context[0x00].getValues(3, ENSOLEILLEMENT_REGISTER, count=1)[0]
        heure_float = heure + minute / 60
        if mode == 0:
            # Hiver : volet ouvert de 00h à 8h et de 19h à 00h
            if (0 <= heure_float < 8) or (19 <= heure_float < 24) or (ensoleillement > programme):
                context[0x00].setValues(3, VOLET_REGISTER, [0])
            else:
                context[0x00].setValues(3, VOLET_REGISTER, [1])
        elif mode == 1:
            # Été : volet ouvert de 00h à 6h et de 21h à 00h
            if (0 <= heure_float < 6) or (21 <= heure_float < 24) or (ensoleillement > programme):
                context[0x00].setValues(3, VOLET_REGISTER, [0])
            else:
                context[0x00].setValues(3, VOLET_REGISTER, [1])
                
        time.sleep(1)


# Lancement du thread de contrôle du volet
volet_thread = Thread(target=volet)
volet_thread.daemon = True
volet_thread.start()

# Démarrage du serveur Modbus TCP sur le port 502
print("Serveur Modbus TCP démarré sur le port 502...")
StartTcpServer(context, address=("127.0.0.1", 502))
