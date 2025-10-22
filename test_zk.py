from zk import ZK

ip = '192.168.43.33'  # l’adresse IP de ton device
port = 4370            # port par défaut ZKTeco

try:
    print(f"Connexion à {ip}:{port} ...")
    zk = ZK(ip=ip, port=port, timeout=5)
    conn = zk.connect()
    print("✅ Connecté avec succès au device ZKTeco !")

    # On teste la récupération d’informations de base
    info = conn.get_device_name()
    print(f"Nom du device : {info}")

    conn.disconnect()
    print("🔌 Déconnecté avec succès !")

except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
