import random
import time
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
from datetime import datetime

# Initialisation des données (coils, holding registers, etc.)
store = ModbusDeviceContext(
    di=ModbusSequentialDataBlock(0, [0]*100),    # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0]*100),    # Coils
    hr=ModbusSequentialDataBlock(0, [13]*100),   # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0]*100)     # Input Registers
)

# Durée d'une journée simulée (24h en minutes)
journee_minutes = (24 * 60)+1  
# Accélération (1 seconde réelle = 6 minutes simulées)
minutes_par_seconde = 12  
# Contexte du serveur (1 slave par défaut, unit_id=1)
context = ModbusServerContext(devices = store, single=True)
# Adresse du registre où l'ensoleillement sera stockée
HEURE_REGISTER = 0  # Heure
MINUTE_REGISTER = 1 # Minute
ENSOLEILLEMENT_REGISTER = 2  # Ensoleillement


def update_time_registers(context, slave_id=0x00):
    """Met à jour les registres Modbus avec l'heure et la minutesystème."""
    while True:
        now = datetime.now()
        heure = now.hour
        minute = now.minute
        # Ecriture dans les registres Modbus
        context[slave_id].setValues(3, HEURE_REGISTER, [heure])
        context[slave_id].setValues(3, MINUTE_REGISTER, [minute])
        time.sleep(1)

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 10 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [50]*10)  # 20.0°C initial
    )
    context = ModbusServerContext(devices=device, single=True)



    # Lancement du thread de mise à jour de l'heure
    time_thread = Thread(target=update_time_registers, args=(context,))
    time_thread.daemon = True
    time_thread.start()

    # Lancement du thread de simulation d'heure (heure/minute simulées)
    sim_heures_thread = Thread(target=Simulation_heures, args=(context, journee_minutes, minutes_par_seconde))
    sim_heures_thread.daemon = True
    sim_heures_thread.start()


def Simulation_heures(context, journee_minutes, minutes_par_seconde, slave_id=0x00):
    """Simule le passage du temps dans une journée et écrit dans les registres Modbus."""
    minutes = 0
    while minutes < journee_minutes:
        heures = minutes // 60
        mins = minutes % 60
        print(f"Il est {heures:02d}:{mins:02d}")
        # Mise à jour des registres Modbus
        context[slave_id].setValues(3, HEURE_REGISTER, [heures])
        context[slave_id].setValues(3, MINUTE_REGISTER, [mins])
        # Pause d'une seconde (temps réel)
        time.sleep(1)
        # Avancer dans le temps simulé
        minutes += minutes_par_seconde

def ensoleillement(t):
    if t < 6 or t > 22:
        return 0
    return max(0, -2.78 * (t - 12)**2 + 100)

# Générer la journée (0 à 24h)
heures = np.linspace(0, 24, 200)
ensoleillement_values = [ensoleillement(h) for h in heures]

# Affichage
plt.plot(heures, ensoleillement_values, label="Taux d'ensoleillement (%)")
plt.xlabel("Heure de la journée")
plt.ylabel("Ensoleillement (%)")
plt.title("Simulation du taux d'ensoleillement (parabole)")
plt.legend()
plt.grid()
plt.show()

# Démarrage du serveur Modbus TCP sur le port 502
print("Serveur Modbus TCP démarré sur le port 502...")
StartTcpServer(context, address=("127.0.0.1", 502))
