import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime, timedelta
import json
from service import ZKTecoService
from zkteco_client import ZKTecoClient
from api_client import APIClient

class ZKTecoGUI:
    def __init__(self, root):
        self.root = root
        self.service = ZKTecoService()
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        self.root.title("Service ZKTeco - Configuration")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Configuration
        self.setup_config_tab()
        
        # Onglet Envoi Manuel
        self.setup_manual_tab()
        
        # Onglet Logs
        self.setup_logs_tab()
    
    def setup_config_tab(self):
        """Onglet de configuration"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Titre
        title_label = ttk.Label(config_frame, text="Service de Pointage ZKTeco", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Configuration
        config_group = ttk.LabelFrame(config_frame, text="Configuration", padding="10")
        config_group.pack(fill=tk.X, pady=(0, 10))
        
        # IP ZKTeco
        ip_frame = ttk.Frame(config_group)
        ip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ip_frame, text="IP du device:").pack(side=tk.LEFT)
        self.ip_entry = ttk.Entry(ip_frame, width=20)
        self.ip_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.ip_entry.insert(0, self.service.config.get('zkteco_ip'))
        
        # URL API
        api_frame = ttk.Frame(config_group)
        api_frame.pack(fill=tk.X, pady=5)
        ttk.Label(api_frame, text="URL API:").pack(side=tk.LEFT)
        self.api_entry = ttk.Entry(api_frame, width=40)
        self.api_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.api_entry.insert(0, self.service.config.get('api_url'))
        
        # Intervalle
        interval_frame = ttk.Frame(config_group)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="Intervalle (secondes):").pack(side=tk.LEFT)
        self.interval_entry = ttk.Entry(interval_frame, width=10)
        self.interval_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.interval_entry.insert(0, str(self.service.config.get('polling_interval')))
        
        # Boutons configuration
        btn_frame = ttk.Frame(config_group)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Tester Connexions", 
                  command=self.test_connections).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Sauvegarder Configuration", 
                  command=self.save_config).pack(side=tk.LEFT)
        
        # Statut du service
        status_group = ttk.LabelFrame(config_frame, text="Statut du Service", padding="10")
        status_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.status_text = scrolledtext.ScrolledText(status_group, height=10, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Boutons service
        service_frame = ttk.Frame(config_frame)
        service_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(service_frame, text="Démarrer le Service Auto", 
                                   command=self.start_service)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(service_frame, text="Arrêter le Service", 
                                  command=self.stop_service, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        ttk.Button(service_frame, text="Synchronisation Immédiate", 
                  command=self.force_sync).pack(side=tk.LEFT, padx=(10, 0))
    
    def setup_manual_tab(self):
        """Onglet d'envoi manuel"""
        manual_frame = ttk.Frame(self.notebook)
        self.notebook.add(manual_frame, text="Envoi Manuel")
        
        # Titre
        title_label = ttk.Label(manual_frame, text="Envoi Manuel des Pointages", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Contrôles de date
        date_group = ttk.LabelFrame(manual_frame, text="Période de récupération", padding="10")
        date_group.pack(fill=tk.X, pady=(0, 10))
        
        # Date de début
        start_frame = ttk.Frame(date_group)
        start_frame.pack(fill=tk.X, pady=5)
        ttk.Label(start_frame, text="Du:").pack(side=tk.LEFT)
        
        self.start_date_entry = ttk.Entry(start_frame, width=20)
        self.start_date_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'))
        
        ttk.Button(start_frame, text="Aujourd'hui", 
                  command=lambda: self.set_date('today')).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(start_frame, text="Hier", 
                  command=lambda: self.set_date('yesterday')).pack(side=tk.LEFT, padx=(5, 0))
        
        # Date de fin
        end_frame = ttk.Frame(date_group)
        end_frame.pack(fill=tk.X, pady=5)
        ttk.Label(end_frame, text="Au:").pack(side=tk.LEFT)
        
        self.end_date_entry = ttk.Entry(end_frame, width=20)
        self.end_date_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        ttk.Button(end_frame, text="Maintenant", 
                  command=lambda: self.set_date('now')).pack(side=tk.LEFT, padx=(10, 0))
        
        # Boutons d'action
        action_frame = ttk.Frame(manual_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Récupérer les Pointages", 
                  command=self.fetch_attendances).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Envoyer à l'API", 
                  command=self.send_manual).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Tout Sélectionner", 
                  command=self.select_all).pack(side=tk.LEFT)
        
        # Liste des pointages
        list_group = ttk.LabelFrame(manual_frame, text="Pointages récupérés", padding="10")
        list_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame pour la liste et les détails
        list_detail_frame = ttk.Frame(list_group)
        list_detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # Liste
        list_frame = ttk.Frame(list_detail_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.attendance_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.attendance_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attendance_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_listbox.config(yscrollcommand=scrollbar.set)
        
        # Détails
        detail_frame = ttk.LabelFrame(list_detail_frame, text="Détails du pointage sélectionné", width=200)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        detail_frame.pack_propagate(False)  # Garder la largeur fixe
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, height=10, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Lier la sélection à l'affichage des détails
        self.attendance_listbox.bind('<<ListboxSelect>>', self.show_attendance_details)
        
        # Résultat
        self.result_label = ttk.Label(manual_frame, text="", foreground="green")
        self.result_label.pack()
        
        # Stockage des données
        self.attendances_data = []
    
    def setup_logs_tab(self):
        """Onglet des logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=20, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def set_date(self, period):
        """Définir les dates automatiquement"""
        now = datetime.now()
        if period == 'today':
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, now.strftime('%Y-%m-%d 00:00:00'))
        elif period == 'yesterday':
            yesterday = now - timedelta(days=1)
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, yesterday.strftime('%Y-%m-%d 00:00:00'))
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, yesterday.strftime('%Y-%m-%d 23:59:59'))
        elif period == 'now':
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, now.strftime('%Y-%m-%d %H:%M:%S'))
    
    def fetch_attendances(self):
        """Récupérer les pointages manuellement"""
        def fetch():
            try:
                start_date = datetime.strptime(self.start_date_entry.get(), '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(self.end_date_entry.get(), '%Y-%m-%d %H:%M:%S')
                
                zk_client = ZKTecoClient(
                    self.service.config.get('zkteco_ip'),
                    self.service.config.get('zkteco_port')
                )
                
                self.attendances_data = zk_client.get_attendance_by_date(start_date, end_date)
                
                self.root.after(0, self.update_attendance_list)
                
            except ValueError as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", "Format de date invalide. Utilisez YYYY-MM-DD HH:MM:SS"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de la récupération: {e}"))
        
        threading.Thread(target=fetch, daemon=True).start()
        messagebox.showinfo("Info", "Récupération des pointages en cours...")
    
    def update_attendance_list(self):
        """Mettre à jour la liste des pointages"""
        self.attendance_listbox.delete(0, tk.END)
        
        for att in self.attendances_data:
            display_text = f"{att['timestamp']} - User {att['id']} - Type {att['type']}"
            self.attendance_listbox.insert(tk.END, display_text)
        
        self.result_label.config(text=f"📊 {len(self.attendances_data)} pointages récupérés")
    
    def show_attendance_details(self, event):
        """Afficher les détails du pointage sélectionné"""
        selection = self.attendance_listbox.curselection()
        if selection:
            index = selection[0]
            att = self.attendances_data[index]
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, json.dumps(att, indent=2, ensure_ascii=False))
            self.detail_text.config(state=tk.DISABLED)
    
    def select_all(self):
        """Sélectionner tous les pointages"""
        self.attendance_listbox.select_set(0, tk.END)
    
    def send_manual(self):
        """Envoyer les pointages sélectionnés manuellement"""
        selection = self.attendance_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un pointage")
            return
        
        # Préparer les données sélectionnées
        selected_attendances = [self.attendances_data[i] for i in selection]
        
        def send():
            api_client = APIClient(self.service.config.get('api_url'))
            success = api_client.send_attendance(selected_attendances)
            
            self.root.after(0, lambda: self.show_send_result(success, len(selected_attendances)))
        
        threading.Thread(target=send, daemon=True).start()
        messagebox.showinfo("Info", f"Envoi de {len(selected_attendances)} pointages en cours...")
    
    def show_send_result(self, success, count):
        """Afficher le résultat de l'envoi"""
        if success:
            self.result_label.config(text=f"✅ {count} pointages envoyés avec succès!", foreground="green")
        else:
            self.result_label.config(text=f"❌ Erreur lors de l'envoi des pointages", foreground="red")
    
    def test_connections(self):
        """Tester les connexions"""
        def test():
            results = self.service.test_connection()
            
            self.root.after(0, lambda: self.show_test_results(results))
        
        threading.Thread(target=test, daemon=True).start()
        messagebox.showinfo("Test", "Test des connexions en cours...")
    
    def show_test_results(self, results):
        """Afficher les résultats du test"""
        message = f"Résultats du test:\n\n"
        message += f"ZKTeco Device: {'✅ Connecté' if results['zkteco'] else '❌ Non connecté'}\n"
        message += f"API: {'✅ Connectée' if results['api'] else '❌ Non connectée'}"
        
        if results['zkteco'] and results['device_info']:
            message += f"\n\nInformations du device:\n"
            for key, value in results['device_info'].items():
                message += f"  {key}: {value}\n"
        
        messagebox.showinfo("Résultats du test", message)
    
    def save_config(self):
        """Sauvegarder la configuration"""
        new_config = {
            'zkteco_ip': self.ip_entry.get(),
            'api_url': self.api_entry.get(),
            'polling_interval': int(self.interval_entry.get())
        }
        
        if self.service.update_config(new_config):
            messagebox.showinfo("Succès", "Configuration sauvegardée!")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde")
    
    def start_service(self):
        """Démarrer le service"""
        self.service.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Service", "Service automatique démarré!")
    
    def stop_service(self):
        """Arrêter le service"""
        self.service.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        messagebox.showinfo("Service", "Service arrêté!")
    
    def force_sync(self):
        """Forcer une synchronisation"""
        def sync():
            success = self.service.force_sync()
            self.root.after(0, lambda: messagebox.showinfo(
                "Synchronisation", 
                "✅ Synchronisation réussie!" if success else "❌ Échec de synchronisation"
            ))
        
        threading.Thread(target=sync, daemon=True).start()
        messagebox.showinfo("Synchronisation", "Synchronisation immédiate en cours...")
    
    def update_status(self):
        """Mettre à jour le statut"""
        status = self.service.get_status()
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        status_text = f"Statut: {'🟢 EN COURS' if status['running'] else '🔴 ARRÊTÉ'}\n"
        status_text += f"Dernière vérification: {status['last_check'] or 'Jamais'}\n"
        status_text += f"Dernière synchro: {status['last_successful_sync'] or 'Jamais'}\n"
        status_text += f"Nombre d'erreurs: {status['error_count']}\n\n"
        status_text += f"Configuration actuelle:\n"
        status_text += f"• IP ZKTeco: {status['config']['zkteco_ip']}\n"
        status_text += f"• Port: {status['config']['zkteco_port']}\n"
        status_text += f"• URL API: {status['config']['api_url']}\n"
        status_text += f"• Intervalle: {status['config']['polling_interval']}s\n"
        
        self.status_text.insert(1.0, status_text)
        self.status_text.config(state=tk.DISABLED)
        
        # Mettre à jour toutes les 5 secondes
        self.root.after(5000, self.update_status)
    
    def on_closing(self):
        """Action lors de la fermeture"""
        if messagebox.askokcancel("Quitter", 
                                "Le service continue de tourner en arrière-plan.\n\nSouhaitez-vous vraiment fermer cette fenêtre?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = ZKTecoGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()