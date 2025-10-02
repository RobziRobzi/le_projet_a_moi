# Ajout de l'import manquant
from threading import Thread

from pymodbus.client import ModbusTcpClient

# Initialisation des données Modbus
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

store = ModbusDeviceContext(
    di=ModbusSequentialDataBlock(0, [0]*10),
    co=ModbusSequentialDataBlock(0, [0]*10),
    hr=ModbusSequentialDataBlock(0, [0]*10),
    ir=ModbusSequentialDataBlock(0, [0]*10)
)
context = ModbusServerContext(devices=store, single=True)
import random
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread


# Adresses Modbus
LOCK_COIL_ADDR = 0         # Coil 0: état du verrou (0 = ouvert, 1 = fermé)
SMOKE_SIMULATION_COIL = 1    # Coil 1: activation génération de fumée (0 = off, 1 = on)
FIRE_EXTINCTOR_COIL = 2    # Coil 2: activation extincteur a feu (0 = off, 1 = on)
SMOKE_LEVEL_REG = 1        # Holding Register 1: saturation de l'air (0-100)

def monitor_and_print_status(context):
    smoke_level = random.randint(0, 10)
    last_print = time.time()
    while True:
        # Lecture des états
        lock_state = context[0].getValues(1, LOCK_COIL_ADDR, count=1)[0]
        alarm_state = 1 if lock_state == 1 else 0
        smoke_gen_on = context[0].getValues(1, SMOKE_SIMULATION_COIL, count=1)[0]
        fire_extinction = context[0].getValues(1, FIRE_EXTINCTOR_COIL, count=1)[0]
        


        # Génération de fumée aléatoire uniquement si coil 1 activé et extincteur désactivé
        if smoke_gen_on and fire_extinction == 0:
            variation = random.randint(-2, 4)
            smoke_level = max(0, min(100, smoke_level + variation))
        # Diminution rapide si extincteur actif
        elif fire_extinction == 1:
            if smoke_level > 0:
                smoke_level = max(0, smoke_level - random.randint(3, 8))
        # Diminution normale sinon
        else:
            if smoke_level > 0:
                smoke_level = max(0, smoke_level - random.randint(2, 5))

        # Activation/désactivation automatique de l'extincteur
        if smoke_level >= 70 and fire_extinction == 0:
            # Active le coil 2 (extincteur)
            client = ModbusTcpClient('127.0.0.1', port=502)
            client.connect()
            client.write_coil(FIRE_EXTINCTOR_COIL, True)
            client.close()
        elif smoke_level < 5 and fire_extinction == 1:
            # Désactive le coil 2 (extincteur)
            context[0].setValues(1, SMOKE_SIMULATION_COIL, [0])
            client = ModbusTcpClient('127.0.0.1', port=502)
            client.connect()
            client.write_coil(FIRE_EXTINCTOR_COIL, False)
            client.close()
            


        context[0].setValues(3, SMOKE_LEVEL_REG, [smoke_level])

        # Le détecteur réagit uniquement si le taux est trop élevé
        detector_on = 1 if smoke_level > 35 else 0

        # Affichage synchronisé toutes les 5 secondes
        if time.time() - last_print >= 3:
            print("\n================= État du système =================")
            print(f"Alarme de sécurité: {'ACTIVÉE' if alarm_state else 'désactivée'}")
            if detector_on:
                print(f"DÉTECTEUR DE FUMÉE : ACTIVÉ /!\ATTENTION/!\ ")
            else:
                print(f"Détecteur de fumée : désactivé")
            print(f"Saturation de l'air par la fumée : {smoke_level}%")
            if fire_extinction:
                print("EXTINCTEUR : ACTIVÉ  /!\ALERTE/!\ ")
            print("===================================================\n")
            last_print = time.time()

        time.sleep(1)




# Lancement du monitoring synchronisé dans un thread séparé
monitor_thread = Thread(target=monitor_and_print_status, args=(context,), daemon=True)
monitor_thread.start()

print("Serveur Modbus TCP démarré sur le port 502...")
StartTcpServer(context, address=("127.0.0.1", 502))
