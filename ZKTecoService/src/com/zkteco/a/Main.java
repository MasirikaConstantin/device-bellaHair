package com.zkteco;

import java.util.logging.*;

public class Main {
    private static final Logger logger = Logger.getLogger(Main.class.getName());
    
    private static void setupLogging() {
        try {
            FileHandler fileHandler = new FileHandler("zkteco_service.log", 1024*1024, 3, true);
            fileHandler.setFormatter(new SimpleFormatter() {
                private static final String format = "[%1$tF %1$tT] [%2$-7s] %3$s %n";
                
                @Override
                public synchronized String format(LogRecord lr) {
                    return String.format(format,
                        new java.util.Date(lr.getMillis()),
                        lr.getLevel().getLocalizedName(),
                        lr.getMessage()
                    );
                }
            });
            
            Logger rootLogger = Logger.getLogger("");
            for (Handler handler : rootLogger.getHandlers()) {
                rootLogger.removeHandler(handler);
            }
            rootLogger.addHandler(fileHandler);
            rootLogger.setLevel(Level.INFO);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public static void main(String[] args) {
        setupLogging();
        
        if (args.length > 0) {
            String command = args[0].toLowerCase();
            
            switch (command) {
                case "start":
                    startServiceMode();
                    break;
                case "test":
                    testConnection();
                    break;
                case "simple":
                    testSimple();
                    break;
                default:
                    showHelp();
                    break;
            }
        } else {
            // Mode GUI par défaut
            startGUI();
        }
    }
    
    private static void startServiceMode() {
        logger.info("Demarrage du service ZKTeco en mode service...");
        
        ZKTecoService service = new ZKTecoService();
        service.start();
        
        // Garder le programme actif
        try {
            java.util.Scanner scanner = new java.util.Scanner(System.in);
            while (true) {
                System.out.print("Tapez 'stop' pour arreter le service: ");
                String userInput = scanner.nextLine();
                if (userInput.toLowerCase().equals("stop")) {
                    break;
                }
            }
            scanner.close();
        } catch (Exception e) {
            System.out.println("\nArret demande...");
        } finally {
            service.stop();
        }
    }
    
    private static void testConnection() {
        logger.info("Test de connexion...");
        
        ZKTecoService service = new ZKTecoService();
        java.util.Map<String, Object> results = service.testConnection();
        
        System.out.println("\nResultats du test:");
        System.out.println("ZKTeco Device: " + (Boolean.TRUE.equals(results.get("zkteco")) ? "OK" : "ERREUR"));
        System.out.println("API: " + (Boolean.TRUE.equals(results.get("api")) ? "OK" : "ERREUR"));
        
        if (Boolean.TRUE.equals(results.get("zkteco")) && results.get("device_info") != null) {
            System.out.println("\nInformations du device:");
            java.util.Map<String, Object> deviceInfo = (java.util.Map<String, Object>) results.get("device_info");
            for (java.util.Map.Entry<String, Object> entry : deviceInfo.entrySet()) {
                System.out.println("  " + entry.getKey() + ": " + entry.getValue());
            }
        }
    }
    
    private static void testSimple() {
        // Implementation simple de test
        System.out.println("Test simple de connexion...");
        ZKTecoClient client = new ZKTecoClient("192.168.43.33", 4370);
        boolean connected = client.testConnection();
        System.out.println("Connexion ZKTeco: " + (connected ? "OK" : "ERREUR"));
    }
    
    private static void showHelp() {
        System.out.println("Commandes disponibles:");
        System.out.println("  start  - Demarrer le service en mode console");
        System.out.println("  gui    - Interface graphique (recommandé)");
        System.out.println("  test   - Tester la connexion");
        System.out.println("  simple - Test simple de connexion");
    }
   private static void startGUI() {
    java.awt.EventQueue.invokeLater(() -> {
        try {
            javax.swing.UIManager.setLookAndFeel(
javax.swing.UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        new ZKTecoGUI().setVisible(true);
    });
}
}