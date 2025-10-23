package com.zkteco;

import java.util.*;

public class ZKTecoClient {
    private final String ip;
    private boolean connected = false;

    public ZKTecoClient(String ip) {
        this.ip = ip;
    }

    public boolean testConnection() {
        // 🧠 Simule la connexion (à remplacer par ton SDK réel)
        try {
            // Ici, tu ferais une vraie tentative via le SDK ZK
            // Pour l'instant, on simule avec un délai
            Thread.sleep(1000);
            
            // Vérification supplémentaire avant de retourner true
            if (!isDeviceReachable()) {
                System.out.println("❌ Device non joignable après connexion");
                return false;
            }
            
            connected = true;
            return true;
        } catch (Exception e) {
            System.out.println("❌ Erreur de connexion: " + e.getMessage());
            return false;
        }
    }

    /**
     * Vérifie si le device est toujours joignable
     */
    private boolean isDeviceReachable() {
        try {
            // Test de connectivité rapide
            Process pingProcess = new ProcessBuilder("ping", "-c", "1", "-W", "1", ip).start();
            int exitCode = pingProcess.waitFor();
            return exitCode == 0;
        } catch (Exception e) {
            return false;
        }
    }

    public List<Map<String, Object>> getAttendances() {
        // 🧠 Exemple simulé (à remplacer par ton vrai code ZK SDK)
        List<Map<String, Object>> list = new ArrayList<>();
        if (!connected) {
            System.out.println("❌ Non connecté, impossible de récupérer les pointages");
            return list;
        }

        // Simuler 3 pointages
        list.add(Map.of("user_id", "EMP001", "timestamp", "2025-10-23 08:15:12", "status", "IN"));
        list.add(Map.of("user_id", "EMP002", "timestamp", "2025-10-23 08:47:01", "status", "IN"));
        list.add(Map.of("user_id", "EMP001", "timestamp", "2025-10-23 17:03:48", "status", "OUT"));

        return list;
    }

    public void disconnect() {
        connected = false;
        System.out.println("🔌 Déconnecté du device.");
    }
}