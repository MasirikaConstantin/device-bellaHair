from zk import ZK
from datetime import datetime
from typing import List, Dict, Any
import logging

class ZKTecoClient:
    def __init__(self, ip: str, port: int = 4370, timeout: int = 5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.zk = ZK(ip, port=port, timeout=timeout)
        self.conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Établir la connexion avec le device ZKTeco"""
        try:
            self.conn = self.zk.connect()
            self.logger.info(f"✅ Connecté au device ZKTeco {self.ip}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion ZKTeco: {e}")
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
    
    def get_attendance(self) -> List[Dict[str, Any]]:
        """Récupérer les pointages depuis le device et formater pour l'API"""
        if not self.connect():
            return []
        
        try:
            attendances = self.conn.get_attendance()
            self.logger.info(f"📊 {len(attendances)} pointages récupérés")
            
            formatted_attendances = []
            for att in attendances:
                # Format SIMPLIFIÉ pour l'API Laravel
                attendance_data = {
                    'uid': str(att.user_id),
                    'id': int(att.user_id),
                    'state': int(att.status) if att.status is not None else 0,
                    'timestamp': att.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': int(att.punch) if att.punch is not None else 0
                }
                formatted_attendances.append(attendance_data)
                
                # Log détaillé
                self.logger.debug(
                    f"👤 User: {att.user_id} | "
                    f"Time: {att.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Status: {att.status} | "
                    f"Punch: {att.punch}"
                )
            
            return formatted_attendances
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la récupération: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_attendance_since(self, since_date: datetime) -> List[Dict[str, Any]]:
        """Récupérer les pointages depuis une date spécifique"""
        all_attendances = self.get_attendance()
        if not since_date:
            return all_attendances
        
        filtered_attendances = []
        for att in all_attendances:
            att_timestamp = datetime.strptime(att['timestamp'], '%Y-%m-%d %H:%M:%S')
            if att_timestamp >= since_date:
                filtered_attendances.append(att)
        
        self.logger.info(f"📅 {len(filtered_attendances)} pointages depuis {since_date}")
        return filtered_attendances
    
    def get_attendance_by_date(self, start_date: datetime, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Récupérer les pointages entre deux dates"""
        if end_date is None:
            end_date = datetime.now()
            
        all_attendances = self.get_attendance()
        filtered_attendances = []
        
        for att in all_attendances:
            att_timestamp = datetime.strptime(att['timestamp'], '%Y-%m-%d %H:%M:%S')
            if start_date <= att_timestamp <= end_date:
                filtered_attendances.append(att)
        
        self.logger.info(f"📅 {len(filtered_attendances)} pointages entre {start_date} et {end_date}")
        return filtered_attendances
    
    def test_connection(self) -> bool:
        """Tester la connexion au device"""
        try:
            if self.connect():
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Test connexion échoué: {e}")
            return False
        finally:
            self.disconnect()