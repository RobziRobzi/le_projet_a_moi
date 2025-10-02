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
    while True:
        minutes = 0
        heures_simulees = []
        ensoleillement_values = []
        while minutes < journee_minutes:
            heures = minutes // 60
            mins = minutes % 60
            print(f"Il est {heures:02d}:{mins:02d}")
            # Calcul de l'ensoleillement en fonction de l'heure simulée
            taux_ensoleillement = ensoleillement(heures)
            # Mise à jour des registres Modbus
            context[slave_id].setValues(3, HEURE_REGISTER, [heures])
            context[slave_id].setValues(3, MINUTE_REGISTER, [mins])
            context[slave_id].setValues(3, ENSOLEILLEMENT_REGISTER, [int(taux_ensoleillement)])
            # Stockage pour le graphique
            heures_simulees.append(heures + mins/60)
            ensoleillement_values.append(taux_ensoleillement)
            # Pause d'une seconde (temps réel)
            time.sleep(1)
            # Avancer dans le temps simulé
            minutes += minutes_par_seconde
        # Affichage du graphique à la fin de la simulation d'une journée
        plt.plot(heures_simulees, ensoleillement_values, label="Taux d'ensoleillement simulé (%)")
        plt.xlabel("Heure simulée")
        plt.ylabel("Ensoleillement (%)")
        plt.title("Simulation du taux d'ensoleillement (parabole, heure simulée)")
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [50]*100),
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


def ensoleillement(t):
    # Courbe linéaire en forme de parabole idéale
    if t < 7 or t > 20:
        return 0
    elif 6 <= t < 12:
        # Monte de 0 à 100% entre 6h et 12h
        return (t - 6) / (12 - 6) * 100
    elif 12 <= t <= 22:
        # Redescend de 100% à 0% entre 12h et 22h
        return (1 - (t - 12) / (22 - 12)) * 100


# Démarrage du serveur Modbus TCP sur le port 502
print("Serveur Modbus TCP démarré sur le port 502...")
StartTcpServer(context, address=("127.0.0.1", 502))
