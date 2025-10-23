package com.zkteco;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.logging.*;
import javax.net.ssl.HttpsURLConnection;
public class ApiClient {
    private static final Logger logger = Logger.getLogger(ApiClient.class.getName());
    private String apiUrl;
    
    public ApiClient(String apiUrl) {
        this.apiUrl = apiUrl;
    }
    
    public boolean sendAttendance(List<Map<String, Object>> attendanceData) {
        return sendAttendance(attendanceData, 3);
    }
    
    public boolean sendAttendance(List<Map<String, Object>> attendanceData, int maxRetries) {
        if (attendanceData == null || attendanceData.isEmpty()) {
            logger.info("📭 Aucune donnée à envoyer");
            return true;
        }
        
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                logger.info("📤 Tentative " + (attempt + 1) + "/" + maxRetries + 
                           " - Envoi de " + attendanceData.size() + " pointages");
                
                URL url = new URL(apiUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setRequestProperty("User-Agent", "ZKTeco-Service/2.0");
                connection.setConnectTimeout(30000);
                connection.setReadTimeout(30000);
                connection.setDoOutput(true);
                
                // Désactiver la vérification SSL
                if (connection instanceof HttpsURLConnection) {
                    ((HttpsURLConnection) connection).setSSLSocketFactory(
                        getTrustAllSocketFactory());
                }
                
                // Convertir les données en JSON
                String jsonData = convertToJson(attendanceData);
                
                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = jsonData.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }
                
                int responseCode = connection.getResponseCode();
                
                if (responseCode == 200 || responseCode == 201) {
                    String response = readResponse(connection);
                    logger.info("✅ Réponse API: " + response);
                    return true;
                } else {
                    logger.warning("⚠️ Réponse API " + responseCode + ": " + readError(connection));
                    
                    if (attempt < maxRetries - 1) {
                        int waitTime = (attempt + 1) * 10;
                        logger.info("⏳ Nouvelle tentative dans " + waitTime + "s...");
                        Thread.sleep(waitTime * 1000);
                    }
                }
                
            } catch (SocketTimeoutException e) {
                logger.severe("⏰ Timeout API: " + e.getMessage());
            } catch (ConnectException e) {
                logger.severe("🔌 Erreur connexion API: " + e.getMessage());
            } catch (Exception e) {
                logger.severe("💥 Erreur inattendue: " + e.getMessage());
            }
            
            if (attempt < maxRetries - 1) {
                try {
                    Thread.sleep((attempt + 1) * 10000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
        
        logger.severe("🔴 Échec après " + maxRetries + " tentatives");
        return false;
    }
    
    public boolean testConnection() {
        try {
            logger.info("🧪 Test de connexion API: " + apiUrl);
            
            // Méthode 1: OPTIONS
            try {
                URL url = new URL(apiUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("OPTIONS");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                if (connection instanceof HttpsURLConnection) {
                    ((HttpsURLConnection) connection).setSSLSocketFactory(
                        getTrustAllSocketFactory());
                }
                
                int responseCode = connection.getResponseCode();
                if (responseCode == 200 || responseCode == 204 || responseCode == 405) {
                    logger.info("✅ Test OPTIONS réussi");
                    return true;
                }
            } catch (Exception e) {
                // Continuer avec d'autres méthodes
            }
            
            // Méthode 2: HEAD
            try {
                URL url = new URL(apiUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("HEAD");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                if (connection instanceof HttpsURLConnection) {
                    ((HttpsURLConnection) connection).setSSLSocketFactory(
                        getTrustAllSocketFactory());
                }
                
                int responseCode = connection.getResponseCode();
                if (responseCode != 404) {
                    logger.info("✅ Test HEAD réussi");
                    return true;
                }
            } catch (Exception e) {
                // Continuer avec d'autres méthodes
            }
            
            // Méthode 3: POST avec données vides
            try {
                URL url = new URL(apiUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                connection.setDoOutput(true);
                
                if (connection instanceof HttpsURLConnection) {
                    ((HttpsURLConnection) connection).setSSLSocketFactory(
                        getTrustAllSocketFactory());
                }
                
                // Envoyer tableau vide
                String emptyJson = "[]";
                try (OutputStream os = connection.getOutputStream()) {
                    byte[] input = emptyJson.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }
                
                int responseCode = connection.getResponseCode();
                if (responseCode != 404) {
                    logger.info("✅ Test avec données vides réussi");
                    return true;
                }
            } catch (ConnectException e) {
                logger.severe("🔌 Impossible de se connecter à l'API");
                return false;
            } catch (Exception e) {
                if (!e.getMessage().contains("404")) {
                    logger.info("✅ Endpoint accessible (erreur autre que 404)");
                    return true;
                }
            }
            
            logger.severe("❌ Aucune méthode de test n'a fonctionné");
            return false;
            
        } catch (Exception e) {
            logger.severe("❌ Test connexion API échoué: " + e.getMessage());
            return false;
        }
    }
    
    private String convertToJson(List<Map<String, Object>> data) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < data.size(); i++) {
            Map<String, Object> item = data.get(i);
            sb.append("{");
            int count = 0;
            for (Map.Entry<String, Object> entry : item.entrySet()) {
                sb.append("\"").append(entry.getKey()).append("\":");
                if (entry.getValue() instanceof String) {
                    sb.append("\"").append(entry.getValue()).append("\"");
                } else {
                    sb.append(entry.getValue());
                }
                if (++count < item.size()) {
                    sb.append(",");
                }
            }
            sb.append("}");
            if (i < data.size() - 1) {
                sb.append(",");
            }
        }
        sb.append("]");
        return sb.toString();
    }
    
    private String readResponse(HttpURLConnection connection) {
        try {
            BufferedReader in = new BufferedReader(
                new InputStreamReader(connection.getInputStream()));
            String inputLine;
            StringBuilder content = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                content.append(inputLine);
            }
            in.close();
            return content.toString();
        } catch (Exception e) {
            return "Erreur lecture réponse: " + e.getMessage();
        }
    }
    
    private String readError(HttpURLConnection connection) {
        try {
            BufferedReader in = new BufferedReader(
                new InputStreamReader(connection.getErrorStream()));
            String inputLine;
            StringBuilder content = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                content.append(inputLine);
            }
            in.close();
            return content.toString();
        } catch (Exception e) {
            return "Erreur lecture erreur: " + e.getMessage();
        }
    }
    
    private javax.net.ssl.SSLSocketFactory getTrustAllSocketFactory() {
        try {
            javax.net.ssl.TrustManager[] trustAllCerts = new javax.net.ssl.TrustManager[]{
                new javax.net.ssl.X509TrustManager() {
                    public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                        return null;
                    }
                    public void checkClientTrusted(
                        java.security.cert.X509Certificate[] certs, String authType) {
                    }
                    public void checkServerTrusted(
                        java.security.cert.X509Certificate[] certs, String authType) {
                    }
                }
            };
            
            javax.net.ssl.SSLContext sc = javax.net.ssl.SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());
            return sc.getSocketFactory();
        } catch (Exception e) {
            return null;
        }
    }
}