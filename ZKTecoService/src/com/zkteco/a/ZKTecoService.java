package com.zkteco;

import java.util.*;
import java.util.concurrent.*;
import java.util.logging.*;
import java.text.SimpleDateFormat;

public class ZKTecoService {
    private static final Logger logger = Logger.getLogger(ZKTecoService.class.getName());
    private ConfigManager configManager;
    private ScheduledExecutorService scheduler;
    private boolean isRunning = false;
    private Date lastCheck;
    private Date lastSuccessfulSync;
    private int errorCount = 0;
    private final int MAX_ERRORS = 5;
    
    public ZKTecoService() {
        this.configManager = new ConfigManager();
        setupLogger();
    }
    
    private void setupLogger() {
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
    
    public void start() {
        if (isRunning) {
            logger.warning("⚠️ Service déjà en cours d'exécution");
            return;
        }
        
        isRunning = true;
        scheduler = Executors.newScheduledThreadPool(1);
        
        int interval = configManager.getInt("polling_interval", 300);
        logger.info("🚀 Service ZKTeco démarré - Intervalle: " + interval + "s");
        
        scheduler.scheduleAtFixedRate(this::checkAttendance, 0, interval, TimeUnit.SECONDS);
    }
    
    public void stop() {
        if (!isRunning) return;
        
        isRunning = false;
        if (scheduler != null) {
            scheduler.shutdown();
            try {
                if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                    scheduler.shutdownNow();
                }
            } catch (InterruptedException e) {
                scheduler.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        logger.info("🛑 Service ZKTeco arrêté");
    }
    
    private void checkAttendance() {
        logger.info("🔍 Vérification des pointages...");
        
        try {
            // Calculer la date de départ (dernière synchro ou 24h)
            Date sinceDate = lastSuccessfulSync;
            if (sinceDate == null) {
                Calendar cal = Calendar.getInstance();
                cal.add(Calendar.HOUR, -24);
                sinceDate = cal.getTime();
            }
            
            ZKTecoClient zkClient = new ZKTecoClient(
                configManager.getString("zkteco_ip", "192.168.43.33"),
                configManager.getInt("zkteco_port", 4370)
            );
            
            List<Map<String, Object>> attendances = zkClient.getAttendanceSince(sinceDate);
            
            if (attendances != null && !attendances.isEmpty()) {
                logger.info("📥 " + attendances.size() + " nouveaux pointages à envoyer");
                
                ApiClient apiClient = new ApiClient(configManager.getString("api_url", "http://localhost:8000/api/pointages"));
                boolean success = apiClient.sendAttendance(attendances);
                
                if (success) {
                    lastSuccessfulSync = new Date();
                    lastCheck = new Date();
                    errorCount = 0;
                    logger.info("✅ Pointages envoyés avec succès");
                } else {
                    errorCount++;
                    logger.severe("❌ Échec de l'envoi des pointages");
                }
            } else {
                lastCheck = new Date();
                logger.info("📭 Aucun nouveau pointage");
            }
            
        } catch (Exception e) {
            errorCount++;
            logger.severe("💥 Erreur lors de la vérification: " + e.getMessage());
            
            if (errorCount >= MAX_ERRORS) {
                logger.severe("🔴 Trop d'erreurs, arrêt du service");
                stop();
            }
        }
    }
    
    public Map<String, Object> testConnection() {
        return testConnection(null);
    }
    
    public Map<String, Object> testConnection(String ip) {
        String testIp = (ip != null) ? ip : configManager.getString("zkteco_ip", "192.168.43.33");
        
        Map<String, Object> results = new HashMap<>();
        results.put("zkteco", false);
        results.put("api", false);
        results.put("device_info", new HashMap<String, Object>());
        results.put("zkteco_error", null);
        results.put("api_error", null);
        
        try {
            // Test ZKTeco
            ZKTecoClient zkClient = new ZKTecoClient(testIp, configManager.getInt("zkteco_port", 4370));
            boolean zkConnected = zkClient.testConnection();
            results.put("zkteco", zkConnected);
            
            if (zkConnected) {
                Map<String, Object> deviceInfo = new HashMap<>();
                deviceInfo.put("ip_address", testIp);
                deviceInfo.put("port", configManager.getInt("zkteco_port", 4370));
                deviceInfo.put("status", "Connecté avec succès");
                deviceInfo.put("test_time", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
                results.put("device_info", deviceInfo);
            }
            
        } catch (Exception e) {
            results.put("zkteco_error", e.getMessage());
            logger.severe("❌ Erreur test ZKTeco: " + e.getMessage());
        }
        
        // Test API
        try {
            ApiClient apiClient = new ApiClient(configManager.getString("api_url", "http://localhost:8000/api/pointages"));
            boolean apiConnected = apiClient.testConnection();
            results.put("api", apiConnected);
        } catch (Exception e) {
            results.put("api_error", e.getMessage());
            logger.severe("❌ Erreur test API: " + e.getMessage());
        }
        
        return results;
    }
    
    public boolean updateConfig(Map<String, Object> newConfig) {
        try {
            for (Map.Entry<String, Object> entry : newConfig.entrySet()) {
                configManager.setProperty(entry.getKey(), entry.getValue().toString());
            }
            logger.info("✅ Configuration mise à jour");
            return true;
        } catch (Exception e) {
            logger.severe("❌ Erreur mise à jour configuration: " + e.getMessage());
            return false;
        }
    }
    
    public Map<String, Object> getStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("running", isRunning);
        status.put("last_check", lastCheck != null ? lastCheck.toString() : null);
        status.put("last_successful_sync", lastSuccessfulSync != null ? lastSuccessfulSync.toString() : null);
        status.put("error_count", errorCount);
        
        Map<String, Object> config = new HashMap<>();
        config.put("zkteco_ip", configManager.getString("zkteco_ip", "192.168.43.33"));
        config.put("zkteco_port", configManager.getInt("zkteco_port", 4370));
        config.put("api_url", configManager.getString("api_url", "http://localhost:8000/api/pointages"));
        config.put("polling_interval", configManager.getInt("polling_interval", 180));
        
        status.put("config", config);
        return status;
    }
    
    public boolean forceSync() {
        logger.info("🔀 Synchronisation forcée demandée");
        checkAttendance();
        return errorCount == 0;
    }
    
    public boolean isRunning() {
        return isRunning;
    }
}