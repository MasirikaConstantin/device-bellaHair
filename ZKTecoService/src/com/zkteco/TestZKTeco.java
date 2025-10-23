package com.zkteco;

import java.text.SimpleDateFormat;
import java.util.*;

public class TestZKTeco {

    public static void main(String[] args) {
        // 🔧 Config de base (à adapter)
        String deviceIp = "192.168.1.201";  // <-- IP de ton terminal ZKTeco

        System.out.println("Test de ping du device ZKTeco " + deviceIp + " ...");

        // Test de ping avant toute tentative de connexion
        if (!pingDevice(deviceIp)) {
            System.out.println("❌ Device non pingable ! Vérifiez l'IP et la connectivité réseau.");
            return;
        }

        System.out.println("✅ Device pingable !");
        System.out.println("Connexion au device ZKTeco " + deviceIp + " ...");

        ZKTecoClient client = new ZKTecoClient(deviceIp);

        if (!client.testConnection()) {
            System.out.println("❌ Impossible de se connecter au device !");
            return;
        }

        System.out.println("✅ Connexion réussie !");
        System.out.println("Récupération des pointages du jour en cours...");

        // 🕒 Obtenir les attendances
        List<Map<String, Object>> attendances = client.getAttendances();

        // 🧮 Filtrer celles du jour
        String today = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
        List<Map<String, Object>> todayAttendances = new ArrayList<>();

        for (Map<String, Object> att : attendances) {
            Object timeObj = att.get("timestamp");
            if (timeObj != null && timeObj.toString().startsWith(today)) {
                todayAttendances.add(att);
            }
        }

        // 📋 Affichage des résultats
        if (todayAttendances.isEmpty()) {
            System.out.println("Aucun pointage trouvé pour aujourd'hui (" + today + ")");
        } else {
            System.out.println("Pointages du " + today + " :");
            for (Map<String, Object> entry : todayAttendances) {
                System.out.printf("- ID: %s | Date: %s | Type: %s%n",
                        entry.get("user_id"),
                        entry.get("timestamp"),
                        entry.get("status"));
            }
        }

        client.disconnect();
        System.out.println("\n✅ Test terminé.");
    }

    /**
     * Vérifie si le device est pingable
     */
    private static boolean pingDevice(String ip) {
        try {
            Process pingProcess = new ProcessBuilder("ping", "-c", "3", "-W", "2", ip).start();
            int exitCode = pingProcess.waitFor();
            return exitCode == 0;
        } catch (Exception e) {
            System.out.println("❌ Erreur lors du ping: " + e.getMessage());
            return false;
        }
    }
}