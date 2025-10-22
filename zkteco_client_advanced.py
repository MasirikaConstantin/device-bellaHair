from zk import ZK
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
import socket

class ZKTecoClient:
    def __init__(self, ip: str, port: int = None, timeout: int = 10):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.zk = None
        self.conn = None
        self.logger = logging.getLogger(__name__)
        
        # Ports communs pour ZKTeco
        self.common_ports = [4370, 80, 8080, 5000, 3000, 22]
    
    def detect_port(self) -> int:
        """Détecter automatiquement le port du device"""
        self.logger.info(f"🔍 Détection automatique du port pour {self.ip}...")
        
        for port in self.common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.ip, port))
                sock.close()
                
                if result == 0:
                    self.logger.info(f"✅ Port {port} détecté comme ouvert")
                    return port
                    
            except Exception:
                continue
        
        self.logger.warning("❌ Aucun port standard détecté, utilisation du port 4370 par défaut")
        return 4370
    
    def connect(self, port: int = None) -> bool:
        """Établir la connexion avec le device ZKTeco"""
        try:
            # Utiliser le port fourni, détecté ou par défaut
            if port:
                self.port = port
            elif not self.port:
                self.port = self.detect_port()
            
            self.logger.info(f"🔌 Tentative de connexion à {self.ip}:{self.port}")
            
            # Créer l'instance ZK avec le port déterminé
            self.zk = ZK(
                self.ip, 
                port=self.port, 
                timeout=self.timeout, 
                ommit_ping=False,
                force_udp=False
            )
            
            self.conn = self.zk.connect()
            self.logger.info(f"✅ Connecté au device ZKTeco {self.ip}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion ZKTeco sur {self.ip}:{self.port}: {str(e)}")
            
            # Essayer d'autres ports si la connexion échoue
            if not port and self.port == 4370:
                self.logger.info("🔄 Essai des autres ports...")
                for test_port in [80, 8080, 5000]:
                    try:
                        self.zk = ZK(self.ip, port=test_port, timeout=5)
                        self.conn = self.zk.connect()
                        self.port = test_port
                        self.logger.info(f"✅ Connecté sur le port alternatif {test_port}")
                        return True
                    except:
                        continue
            
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.conn:
            try:
                self.conn.disconnect()
                self.logger.info("✅ Déconnecté du device ZKTeco")
            except Exception as e:
                self.logger.error(f"❌ Erreur déconnexion: {e}")
            finally:
                self.conn = None
                self.zk = None
    
    def get_device_info(self) -> Dict[str, Any]:
        """Récupérer les informations du device"""
        if not self.connect():
            return {}
        
        try:
            info = {}
            
            # Informations de base
            info['ip_address'] = self.ip
            info['port'] = self.port
            info['connected'] = True
            
            # Informations spécifiques au device
            try:
                info['device_name'] = self.conn.get_device_name()
            except:
                info['device_name'] = 'N/A'
            
            try:
                info['firmware_version'] = self.conn.get_firmware_version()
            except:
                info['firmware_version'] = 'N/A'
            
            try:
                users = self.conn.get_users()
                info['users_count'] = len(users)
            except:
                info['users_count'] = 'N/A'
            
            try:
                attendances = self.conn.get_attendance()
                info['attendances_count'] = len(attendances)
            except:
                info['attendances_count'] = 'N/A'
            
            return info
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération info device: {e}")
            return {}
        finally:
            self.disconnect()
    
    def get_attendance(self, port: int = None) -> List[Dict[str, Any]]:
        """Récupérer les pointages depuis le device"""
        if not self.connect(port):
            return []
        
        try:
            attendances = self.conn.get_attendance()
            self.logger.info(f"📊 {len(attendances)} pointages récupérés sur le port {self.port}")
            
            formatted_attendances = []
            for att in attendances:
                attendance_data = {
                    'uid': str(att.user_id),
                    'id': int(att.user_id),
                    'state': int(att.status) if att.status is not None else 0,
                    'timestamp': att.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': int(att.punch) if att.punch is not None else 0,
                    'device_ip': self.ip,
                    'device_port': self.port
                }
                formatted_attendances.append(attendance_data)
                
                # Log détaillé pour les premiers pointages
                if len(formatted_attendances) <= 3:
                    self.logger.debug(
                        f"👤 User: {att.user_id} | "
                        f"Time: {att.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                        f"Status: {att.status}"
                    )
            
            return formatted_attendances
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la récupération: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_attendance_since(self, since_date: datetime, port: int = None) -> List[Dict[str, Any]]:
        """Récupérer les pointages depuis une date spécifique"""
        all_attendances = self.get_attendance(port)
        if not since_date:
            return all_attendances
        
        filtered_attendances = []
        for att in all_attendances:
            att_timestamp = datetime.strptime(att['timestamp'], '%Y-%m-%d %H:%M:%S')
            if att_timestamp >= since_date:
                filtered_attendances.append(att)
        
        self.logger.info(f"📅 {len(filtered_attendances)} pointages depuis {since_date}")
        return filtered_attendances
    
    def test_connection(self, port: int = None) -> Tuple[bool, Dict[str, Any]]:
        """Tester la connexion au device avec informations détaillées"""
        result = {
            'success': False,
            'ip': self.ip,
            'port': port or self.port,
            'device_info': {},
            'error': None
        }
        
        try:
            if self.connect(port):
                result['success'] = True
                result['port'] = self.port  # Port réel utilisé
                result['device_info'] = self.get_device_info()
            else:
                result['error'] = "Connexion impossible"
                
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"❌ Test connexion échoué: {e}")
        
        return result['success'], result