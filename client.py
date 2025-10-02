from pymodbus.client import ModbusTcpClient
import time

def main():
    # Connexion au serveur Modbus
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()

    try:
        # Exemple : activer la génération de fumée (coil 1)
        client.write_coil(1, True)
        print("Génération de fumée activée (coil 1 = 1)")

        # Attendre un peu pour laisser le serveur simuler
        time.sleep(2)

        # Lire le niveau de fumée (registre 1)
        result = client.read_holding_registers(1, 1)
        if result.isError():
            print("Erreur de lecture du registre")
        else:
            print(f"Niveau de fumée : {result.registers[0]}%")

        # Exemple : désactiver la génération de fumée (coil 1)
        client.write_coil(1, False)
        print("Génération de fumée désactivée (coil 1 = 0)")

        # Exemple : activer l'extincteur (coil 2)
        client.write_coil(2, True)
        print("Extincteur activé (coil 2 = 1)")

        # Attendre un peu pour voir l'effet
        time.sleep(2)

        # Lire à nouveau le niveau de fumée
        result = client.read_holding_registers(1, 1)
        if result.isError():
            print("Erreur de lecture du registre")
        else:
            print(f"Niveau de fumée après extinction : {result.registers[0]}%")
    finally:
        # Fermer la connexion
        client.close()

if __name__ == "__main__":
    main()