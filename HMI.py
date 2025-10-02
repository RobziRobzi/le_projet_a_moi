from pymodbus.client import ModbusTcpClient
import time

# Connexion au serveur Modbus
client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

# Demander le mode et le taux d'ensoleillement au démarrage

valeur_mode = int(input("Choisissez le mode : Hiver (0) ou été (1) : "))
client.write_register(address=4, value=valeur_mode)
valeur_ensoleillement = int(input("Entrez le taux d'ensoleillement à régler (0-100) : "))
client.write_register(address=3, value=valeur_ensoleillement)

# Affichage des infos juste après saisie
time.sleep(1)
lever_result = client.read_holding_registers(address=6, count=1)
coucher_result = client.read_holding_registers(address=7, count=1)
mode_result = client.read_holding_registers(address=4, count=1)
enso_result = client.read_holding_registers(address=3, count=1)
if not lever_result.isError() and not coucher_result.isError() and not mode_result.isError() and not enso_result.isError():
    lever = lever_result.registers[0] / 100.0
    coucher = coucher_result.registers[0] / 100.0
    mode = mode_result.registers[0]
    ensoleillement = enso_result.registers[0]
    mode_str = "Hiver" if mode == 0 else "Été" if mode == 1 else f"Autre ({mode})"
    print("-"*50)
    print(f"Lever du soleil : {lever:.2f}h")
    print(f"Coucher du soleil : {coucher:.2f}h")
    print(f"Mode : {mode_str}")
    print(f"Taux d'ensoleillement programmé : {ensoleillement}%")
    print("-"*50)


while True:
    heure_result = client.read_holding_registers(address=0, count=1)
    minute_result = client.read_holding_registers(address=1, count=1)
    lever_result = client.read_holding_registers(address=6, count=1)
    coucher_result = client.read_holding_registers(address=7, count=1)
    mode_result = client.read_holding_registers(address=4, count=1)
    enso_result = client.read_holding_registers(address=3, count=1)
    enso_reel_result = client.read_holding_registers(address=2, count=1)
    volet_result = client.read_holding_registers(address=5, count=1)
    if not heure_result.isError() and not minute_result.isError() and not lever_result.isError() and not coucher_result.isError() and not mode_result.isError() and not enso_result.isError() and not volet_result.isError() and not enso_reel_result.isError():
        heure = heure_result.registers[0]
        minute = minute_result.registers[0]
        # Actualisation à chaque passage d'heure du REGISTER 0
        if 'last_heure' not in locals():
            last_heure = heure
        if heure != last_heure:
            lever_val = lever_result.registers[0]
            coucher_val = coucher_result.registers[0]
            lever_h = int(lever_val // 100)
            lever_m = int(lever_val % 100)
            coucher_h = int(coucher_val // 100)
            coucher_m = int(coucher_val % 100)
            lever = lever_h + lever_m / 60
            coucher = coucher_h + coucher_m / 60
            mode = mode_result.registers[0]
            ensoleillement = enso_result.registers[0]
            ensoleillement_reel = enso_reel_result.registers[0]
            volet = volet_result.registers[0]
            mode_str = "Hiver" if mode == 0 else "Été" if mode == 1 else None
            volet_str = "Ouvert" if volet == 1 else "Fermé"
            print("-"*50)
            print(f"Lever du soleil : {lever_h:02d}h{lever_m:02d} ")
            print(f"Coucher du soleil : {coucher_h:02d}h{coucher_m:02d} ")
            print(f"Mode : {mode_str}")
            print(f"Taux d'ensoleillement programmé : {ensoleillement}%")
            print(f"Taux d'ensoleillement réel : {ensoleillement_reel}%")
            print(f"Heure simulée : {heure:02d}h{minute:02d}")
            print(f"Volet : {volet_str}")
            print("-"*50)
            last_heure = heure
        if heure == 24:
            lever_val = lever_result.registers[0]
            coucher_val = coucher_result.registers[0]
            lever_h = int(lever_val // 100)
            lever_m = int(lever_val % 100)
            coucher_h = int(coucher_val // 100)
            coucher_m = int(coucher_val % 100)
            lever = lever_h + lever_m / 60
            coucher = coucher_h + coucher_m / 60
            mode = mode_result.registers[0]
            ensoleillement = enso_result.registers[0]
            ensoleillement_reel = enso_reel_result.registers[0]
            volet = volet_result.registers[0]
            mode_str = "Hiver" if mode == 0 else "Été" if mode == 1 else None 
            volet_str = "Ouvert" if volet == 1 else "Fermé"
            print("-"*50)
            print(f"Lever du soleil : {lever_h:02d}h{lever_m:02d} ")
            print(f"Coucher du soleil : {coucher_h:02d}h{coucher_m:02d} ")
            print(f"Mode : {mode_str}")
            print(f"Taux d'ensoleillement programmé : {ensoleillement}%")
            print(f"Taux d'ensoleillement réel : {ensoleillement_reel}%")
            print(f"Heure simulée : {heure:02d}h{minute:02d}")
            print(f"Volet : {volet_str}")
            print("-"*50)
            valeur_changement = int(input("Changer le mode ? (oui=1 et non=0): "))
            if valeur_changement == 1:
                valeur_mode = int(input("Changer le mode ? Hiver (0) ou été (1) : "))
                client.write_register(address=4, value=valeur_mode)
                valeur_ensoleillement = int(input("Changer le taux d'ensoleillement (0-100) : "))
                client.write_register(address=3, value=valeur_ensoleillement)
                print("Valeurs mises à jour.")
                # Affichage des infos après mise à jour
                time.sleep(1)
                lever_result = client.read_holding_registers(address=6, count=1)
                coucher_result = client.read_holding_registers(address=7, count=1)
                mode_result = client.read_holding_registers(address=4, count=1)
                enso_result = client.read_holding_registers(address=3, count=1)
                volet_result = client.read_holding_registers(address=5, count=1)
                if not lever_result.isError() and not coucher_result.isError() and not mode_result.isError() and not enso_result.isError() and not volet_result.isError():
                    lever = lever_result.registers[0] / 100.0
                    coucher = coucher_result.registers[0] / 100.0
                    mode = mode_result.registers[0]
                    ensoleillement = enso_result.registers[0]
                    volet = volet_result.registers[0]
                    mode_str = "Hiver" if mode == 0 else "Été" if mode == 1 else None
                    volet_str = "Ouvert" if volet == 1 else "Fermé"
                    print("-"*50)
                    print(f"Lever du soleil : {lever:.2f}h")
                    print(f"Coucher du soleil : {coucher:.2f}h")
                    print(f"Mode : {mode_str}")
                    print(f"Taux d'ensoleillement programmé : {ensoleillement}%")
                    print(f"Volet : {volet_str}")
                    print("-"*50)
                time.sleep(2)
    time.sleep(1)