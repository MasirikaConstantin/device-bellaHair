package com.zkteco;

import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.List;
import java.awt.image.BufferedImage;
public class ZKTecoGUI extends JFrame {
    private ZKTecoService service;
    private ConfigManager configManager;
    
    // Composants UI
    private JTextField ipField, apiUrlField, intervalField;
    private JTextField startDateEntry, endDateEntry;
    private JButton startBtn, stopBtn;
    private JTextArea statusText;
    private JList<String> attendanceList;
    private JTextArea detailText;
    private JLabel resultLabel;
    
    private List<Map<String, Object>> attendancesData;
    
    public ZKTecoGUI() {
        this.service = new ZKTecoService();
        this.configManager = new ConfigManager();
        this.attendancesData = new ArrayList<>();
        
        initializeUI();
        setupTrayIcon();
        loadConfig();
        updateStatus();
    }
    
    private void initializeUI() {
        setTitle("Service ZKTeco - Configuration");
        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
        setSize(800, 700);
        setLocationRelativeTo(null);
        
        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                hideToTray();
            }
        });
        
        JTabbedPane notebook = new JTabbedPane();
        
        // Onglet Configuration
        notebook.addTab("Configuration", createConfigTab());
        
        // Onglet Envoi Manuel
        notebook.addTab("Envoi Manuel", createManualTab());
        
        // Onglet Logs
        notebook.addTab("Logs", createLogsTab());
        
        add(notebook);
    }
    
    private JPanel createConfigTab() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));
        
        // Titre
        JLabel titleLabel = new JLabel("Service de Pointage ZKTeco", JLabel.CENTER);
        titleLabel.setFont(new Font("Arial", Font.BOLD, 16));
        panel.add(titleLabel, BorderLayout.NORTH);
        
        // Configuration
        JPanel configGroup = new JPanel(new GridLayout(4, 2, 5, 5));
        configGroup.setBorder(new TitledBorder("Configuration"));
        
        configGroup.add(new JLabel("IP du device:"));
        ipField = new JTextField();
        configGroup.add(ipField);
        
        configGroup.add(new JLabel("URL API:"));
        apiUrlField = new JTextField();
        configGroup.add(apiUrlField);
        
        configGroup.add(new JLabel("Intervalle (secondes):"));
        intervalField = new JTextField();
        configGroup.add(intervalField);
        
        JPanel buttonPanel = new JPanel(new FlowLayout());
        JButton testBtn = new JButton("Tester Connexions");
        testBtn.addActionListener(e -> testConnections());
        
        JButton saveBtn = new JButton("Sauvegarder Configuration");
        saveBtn.addActionListener(e -> saveConfig());
        
        buttonPanel.add(testBtn);
        buttonPanel.add(saveBtn);
        
        JPanel configPanel = new JPanel(new BorderLayout());
        configPanel.add(configGroup, BorderLayout.CENTER);
        configPanel.add(buttonPanel, BorderLayout.SOUTH);
        
        panel.add(configPanel, BorderLayout.NORTH);
        
        // Statut du service
        JPanel statusGroup = new JPanel(new BorderLayout());
        statusGroup.setBorder(new TitledBorder("Statut du Service"));
        
        statusText = new JTextArea(10, 50);
        statusText.setEditable(false);
        JScrollPane statusScroll = new JScrollPane(statusText);
        statusGroup.add(statusScroll, BorderLayout.CENTER);
        
        panel.add(statusGroup, BorderLayout.CENTER);
        
        // Boutons service
        JPanel servicePanel = new JPanel(new FlowLayout());
        
        startBtn = new JButton("Démarrer le Service Auto");
        startBtn.addActionListener(e -> startService());
        
        stopBtn = new JButton("Arrêter le Service");
        stopBtn.addActionListener(e -> stopService());
        stopBtn.setEnabled(false);
        
        JButton syncBtn = new JButton("Synchronisation Immédiate");
        syncBtn.addActionListener(e -> forceSync());
        
        servicePanel.add(startBtn);
        servicePanel.add(stopBtn);
        servicePanel.add(syncBtn);
        
        panel.add(servicePanel, BorderLayout.SOUTH);
        
        return panel;
    }
    
    private JPanel createManualTab() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));
        
        // Titre
        JLabel titleLabel = new JLabel("Envoi Manuel des Pointages", JLabel.CENTER);
        titleLabel.setFont(new Font("Arial", Font.BOLD, 14));
        panel.add(titleLabel, BorderLayout.NORTH);
        
        // Période de récupération
        JPanel dateGroup = new JPanel(new GridLayout(2, 2, 5, 5));
        dateGroup.setBorder(new TitledBorder("Période de récupération"));
        
        // Date de début
        dateGroup.add(new JLabel("Du:"));
        JPanel startPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        startDateEntry = new JTextField(20);
        startPanel.add(startDateEntry);
        
        JButton todayBtn = new JButton("Aujourd'hui");
        todayBtn.addActionListener(e -> setDate("today"));
        startPanel.add(todayBtn);
        
        JButton yesterdayBtn = new JButton("Hier");
        yesterdayBtn.addActionListener(e -> setDate("yesterday"));
        startPanel.add(yesterdayBtn);
        
        dateGroup.add(startPanel);
        
        // Date de fin
        dateGroup.add(new JLabel("Au:"));
        JPanel endPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        endDateEntry = new JTextField(20);
        endPanel.add(endDateEntry);
        
        JButton nowBtn = new JButton("Maintenant");
        nowBtn.addActionListener(e -> setDate("now"));
        endPanel.add(nowBtn);
        
        dateGroup.add(endPanel);
        
        panel.add(dateGroup, BorderLayout.NORTH);
        
        // Boutons d'action
        JPanel actionPanel = new JPanel(new FlowLayout());
        
        JButton fetchBtn = new JButton("Récupérer les Pointages");
        fetchBtn.addActionListener(e -> fetchAttendances());
        
        JButton sendBtn = new JButton("Envoyer à l'API");
        sendBtn.addActionListener(e -> sendManual());
        
        JButton selectAllBtn = new JButton("Tout Sélectionner");
        selectAllBtn.addActionListener(e -> selectAll());
        
        actionPanel.add(fetchBtn);
        actionPanel.add(sendBtn);
        actionPanel.add(selectAllBtn);
        
        panel.add(actionPanel, BorderLayout.CENTER);
        
        // Liste et détails
        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        splitPane.setResizeWeight(0.7);
        
        // Liste des pointages
        JPanel listPanel = new JPanel(new BorderLayout());
        listPanel.setBorder(new TitledBorder("Pointages récupérés"));
        
        attendanceList = new JList<>();
        attendanceList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        JScrollPane listScroll = new JScrollPane(attendanceList);
        listPanel.add(listScroll, BorderLayout.CENTER);
        
        // Détails
        JPanel detailPanel = new JPanel(new BorderLayout());
        detailPanel.setBorder(new TitledBorder("Détails du pointage sélectionné"));
        detailPanel.setPreferredSize(new Dimension(300, 0));
        
        detailText = new JTextArea(10, 25);
        detailText.setEditable(false);
        JScrollPane detailScroll = new JScrollPane(detailText);
        detailPanel.add(detailScroll, BorderLayout.CENTER);
        
        splitPane.setLeftComponent(listPanel);
        splitPane.setRightComponent(detailPanel);
        
        panel.add(splitPane, BorderLayout.CENTER);
        
        // Résultat
        resultLabel = new JLabel("", JLabel.CENTER);
        resultLabel.setForeground(Color.GREEN);
        panel.add(resultLabel, BorderLayout.SOUTH);
        
        // Écouteur de sélection
        attendanceList.addListSelectionListener(e -> showAttendanceDetails());
        
        return panel;
    }
    
    private JPanel createLogsTab() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(new EmptyBorder(10, 10, 10, 10));
        
        JTextArea logsText = new JTextArea();
        logsText.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(logsText);
        
        panel.add(scrollPane, BorderLayout.CENTER);
        
        return panel;
    }
    
    private void setupTrayIcon() {
        if (!SystemTray.isSupported()) return;
        
        PopupMenu popup = new PopupMenu();
        MenuItem openItem = new MenuItem("Ouvrir");
        openItem.addActionListener(e -> setVisible(true));
        
        MenuItem exitItem = new MenuItem("Quitter");
        exitItem.addActionListener(e -> {
            stopService();
            System.exit(0);
        });
        
        popup.add(openItem);
        popup.add(exitItem);
        
        // Créer une image simple pour le tray
        Image image = createTrayImage();
        TrayIcon trayIcon = new TrayIcon(image, "Service ZKTeco", popup);
        trayIcon.setImageAutoSize(true);
        
        trayIcon.addActionListener(e -> setVisible(true));
        
        try {
            SystemTray.getSystemTray().add(trayIcon);
        } catch (AWTException e) {
            System.err.println("Impossible de créer le tray icon: " + e.getMessage());
        }
    }
    
    private Image createTrayImage() {
    // Image simple 16x16 pixels
    BufferedImage image = new BufferedImage(16, 16, BufferedImage.TYPE_INT_RGB);
    Graphics2D g2d = image.createGraphics();
    g2d.setColor(Color.GREEN);
    g2d.fillRect(0, 0, 16, 16);
    g2d.setColor(Color.BLACK);
    g2d.drawString("Z", 4, 12);
    g2d.dispose();
    return image;
}
    
    private void hideToTray() {
        setVisible(false);
        // Service continue de tourner en arrière-plan
    }
    
    private void setDate(String period) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Calendar cal = Calendar.getInstance();
        
        switch (period) {
            case "today":
                cal.set(Calendar.HOUR_OF_DAY, 0);
                cal.set(Calendar.MINUTE, 0);
                cal.set(Calendar.SECOND, 0);
                startDateEntry.setText(sdf.format(cal.getTime()));
                break;
            case "yesterday":
                cal.add(Calendar.DAY_OF_MONTH, -1);
                cal.set(Calendar.HOUR_OF_DAY, 0);
                cal.set(Calendar.MINUTE, 0);
                cal.set(Calendar.SECOND, 0);
                startDateEntry.setText(sdf.format(cal.getTime()));
                cal.set(Calendar.HOUR_OF_DAY, 23);
                cal.set(Calendar.MINUTE, 59);
                cal.set(Calendar.SECOND, 59);
                endDateEntry.setText(sdf.format(cal.getTime()));
                break;
            case "now":
                endDateEntry.setText(sdf.format(new Date()));
                break;
        }
    }
    
    private void fetchAttendances() {
        new Thread(() -> {
            try {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Date startDate = sdf.parse(startDateEntry.getText());
                Date endDate = sdf.parse(endDateEntry.getText());
                
                ZKTecoClient client = new ZKTecoClient(
                    configManager.getString("zkteco_ip", "192.168.43.33"),
                    configManager.getInt("zkteco_port", 4370)
                );
                
                attendancesData = client.getAttendanceByDate(startDate, endDate);
                
                SwingUtilities.invokeLater(() -> updateAttendanceList());
                
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> 
                    JOptionPane.showMessageDialog(this, "Erreur: " + e.getMessage(), "Erreur", JOptionPane.ERROR_MESSAGE));
            }
        }).start();
        
        JOptionPane.showMessageDialog(this, "Récupération des pointages en cours...");
    }
    
    private void updateAttendanceList() {
        DefaultListModel<String> model = new DefaultListModel<>();
        for (Map<String, Object> att : attendancesData) {
            String displayText = String.format("%s - User %s - Type %s", 
                att.get("timestamp"), att.get("id"), att.get("type"));
            model.addElement(displayText);
        }
        attendanceList.setModel(model);
        resultLabel.setText("📊 " + attendancesData.size() + " pointages récupérés");
    }
    
    private void showAttendanceDetails() {
        int index = attendanceList.getSelectedIndex();
        if (index >= 0 && index < attendancesData.size()) {
            Map<String, Object> att = attendancesData.get(index);
            detailText.setText(formatMapAsJson(att));
        }
    }
    
    private String formatMapAsJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            sb.append("  \"").append(entry.getKey()).append("\": \"")
              .append(entry.getValue()).append("\",\n");
        }
        if (!map.isEmpty()) {
            sb.setLength(sb.length() - 2); // Enlever la dernière virgule
        }
        sb.append("\n}");
        return sb.toString();
    }
    
    private void selectAll() {
        attendanceList.setSelectionInterval(0, attendanceList.getModel().getSize() - 1);
    }
    
    private void sendManual() {
        int[] indices = attendanceList.getSelectedIndices();
        if (indices.length == 0) {
            JOptionPane.showMessageDialog(this, "Veuillez sélectionner au moins un pointage");
            return;
        }
        
        List<Map<String, Object>> selectedAttendances = new ArrayList<>();
        for (int index : indices) {
            selectedAttendances.add(attendancesData.get(index));
        }
        
        new Thread(() -> {
            ApiClient apiClient = new ApiClient(configManager.getString("api_url", "http://localhost:8000/api/pointages"));
            boolean success = apiClient.sendAttendance(selectedAttendances);
            
            SwingUtilities.invokeLater(() -> showSendResult(success, selectedAttendances.size()));
        }).start();
        
        JOptionPane.showMessageDialog(this, "Envoi de " + selectedAttendances.size() + " pointages en cours...");
    }
    
    private void showSendResult(boolean success, int count) {
        if (success) {
            resultLabel.setText("✅ " + count + " pointages envoyés avec succès!");
            resultLabel.setForeground(Color.GREEN);
        } else {
            resultLabel.setText("❌ Erreur lors de l'envoi des pointages");
            resultLabel.setForeground(Color.RED);
        }
    }
    
    private void testConnections() {
        new Thread(() -> {
            Map<String, Object> results = service.testConnection();
            SwingUtilities.invokeLater(() -> showTestResults(results));
        }).start();
        
        JOptionPane.showMessageDialog(this, "Test des connexions en cours...");
    }
    
    private void showTestResults(Map<String, Object> results) {
        StringBuilder message = new StringBuilder();
        message.append("Résultats du test:\n\n");
        message.append("ZKTeco Device: ").append(Boolean.TRUE.equals(results.get("zkteco")) ? "✅ Connecté" : "❌ Non connecté").append("\n");
        message.append("API: ").append(Boolean.TRUE.equals(results.get("api")) ? "✅ Connectée" : "❌ Non connectée").append("\n");
        
        if (Boolean.TRUE.equals(results.get("zkteco")) && results.get("device_info") != null) {
            message.append("\nInformations du device:\n");
            Map<String, Object> deviceInfo = (Map<String, Object>) results.get("device_info");
            for (Map.Entry<String, Object> entry : deviceInfo.entrySet()) {
                message.append("  ").append(entry.getKey()).append(": ").append(entry.getValue()).append("\n");
            }
        }
        
        JOptionPane.showMessageDialog(this, message.toString());
    }
    
    private void saveConfig() {
        Map<String, Object> newConfig = new HashMap<>();
        newConfig.put("zkteco_ip", ipField.getText());
        newConfig.put("api_url", apiUrlField.getText());
        newConfig.put("polling_interval", Integer.parseInt(intervalField.getText()));
        
        if (service.updateConfig(newConfig)) {
            JOptionPane.showMessageDialog(this, "Configuration sauvegardée!");
        } else {
            JOptionPane.showMessageDialog(this, "Erreur lors de la sauvegarde", "Erreur", JOptionPane.ERROR_MESSAGE);
        }
    }
    
    private void startService() {
        service.start();
        startBtn.setEnabled(false);
        stopBtn.setEnabled(true);
        JOptionPane.showMessageDialog(this, "Service automatique démarré!\nL'application peut être masquée.");
    }
    
    private void stopService() {
        service.stop();
        startBtn.setEnabled(true);
        stopBtn.setEnabled(false);
        JOptionPane.showMessageDialog(this, "Service arrêté!");
    }
    
    private void forceSync() {
        new Thread(() -> {
            boolean success = service.forceSync();
            SwingUtilities.invokeLater(() -> 
                JOptionPane.showMessageDialog(this, 
                    success ? "✅ Synchronisation réussie!" : "❌ Échec de synchronisation"));
        }).start();
        
        JOptionPane.showMessageDialog(this, "Synchronisation immédiate en cours...");
    }
    
    private void loadConfig() {
        ipField.setText(configManager.getString("zkteco_ip", "192.168.43.33"));
        apiUrlField.setText(configManager.getString("api_url", "http://localhost:8000/api/pointages"));
        intervalField.setText(String.valueOf(configManager.getInt("polling_interval", 180)));
        
        // Définir les dates par défaut
        setDate("yesterday");
        setDate("now");
    }
    
    private void updateStatus() {
        Map<String, Object> status = service.getStatus();
        
        StringBuilder statusTextBuilder = new StringBuilder();
        statusTextBuilder.append("Statut: ").append(Boolean.TRUE.equals(status.get("running")) ? "🟢 EN COURS" : "🔴 ARRÊTÉ").append("\n");
        statusTextBuilder.append("Dernière vérification: ").append(status.get("last_check") != null ? status.get("last_check") : "Jamais").append("\n");
        statusTextBuilder.append("Dernière synchro: ").append(status.get("last_successful_sync") != null ? status.get("last_successful_sync") : "Jamais").append("\n");
        statusTextBuilder.append("Nombre d'erreurs: ").append(status.get("error_count")).append("\n\n");
        statusTextBuilder.append("Configuration actuelle:\n");
        
        Map<String, Object> config = (Map<String, Object>) status.get("config");
        statusTextBuilder.append("• IP ZKTeco: ").append(config.get("zkteco_ip")).append("\n");
        statusTextBuilder.append("• Port: ").append(config.get("zkteco_port")).append("\n");
        statusTextBuilder.append("• URL API: ").append(config.get("api_url")).append("\n");
        statusTextBuilder.append("• Intervalle: ").append(config.get("polling_interval")).append("s\n");
        
        statusText.setText(statusTextBuilder.toString());
        
        // Mettre à jour toutes les 5 secondes
        javax.swing.Timer timer = new javax.swing.Timer(5000, e -> updateStatus());
        timer.setRepeats(false);
        timer.start();
    }
    
   public static void main(String[] args) {
    java.awt.EventQueue.invokeLater(() -> {
        try {
            // Correction : utiliser getSystemLookAndFeelClassName()
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        new ZKTecoGUI().setVisible(true);
    });
}
}