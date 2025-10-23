package com.zkteco;

import java.io.*;
import java.util.*;

public class ConfigManager {
    private Properties properties;
    private File configFile;
    
    public ConfigManager() {
        properties = new Properties();
        configFile = new File("config.properties");
        loadConfig();
    }
    
    private void loadConfig() {
        if (configFile.exists()) {
            try (FileInputStream input = new FileInputStream(configFile)) {
                properties.load(input);
            } catch (IOException e) {
                System.err.println("Erreur lecture config: " + e.getMessage());
            }
        } else {
            setDefaultConfig();
        }
    }
    
    private void setDefaultConfig() {
        properties.setProperty("zkteco_ip", "192.168.43.33");
        properties.setProperty("zkteco_port", "4370");
        properties.setProperty("api_url", "http://localhost:8000/api/pointages");
        properties.setProperty("polling_interval", "180");
        saveConfig();
    }
    
    public void saveConfig() {
        try (FileOutputStream output = new FileOutputStream(configFile)) {
            properties.store(output, "Configuration ZKTeco Service");
        } catch (IOException e) {
            System.err.println("Erreur sauvegarde config: " + e.getMessage());
        }
    }
    
    public String getString(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }
    
    public int getInt(String key, int defaultValue) {
        try {
            return Integer.parseInt(properties.getProperty(key));
        } catch (Exception e) {
            return defaultValue;
        }
    }
    
    public void setProperty(String key, String value) {
        properties.setProperty(key, value);
        saveConfig();
    }
    
    public Properties getProperties() {
        return new Properties(properties);
    }
}