# storage/lap_storage.py
import json
import os
from datetime import datetime
import shutil

class LapStorage:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.current_track = None
        self.current_session_path = None
        self.current_session_data = {}

        # Datos de la vuelta actual
        self.current_lap_data = []
        self.current_lap_number = 0
        self.current_lap_time = 0
        self.current_sector_times = [0, 0, 0]
        self.current_sector_splits = [0, 0, 0]
        self.current_sector = 0

        # Mejores tiempos de la sesión actual
        self.best_lap_time = float('inf')
        self.best_lap_number = None
        self.best_sectors = [float('inf'), float('inf'), float('inf')]
        self.best_sectors_lap = [None, None, None]

        # Mejores tiempos globales (por mapa)
        self.global_best_lap_time = float('inf')
        self.global_best_sectors = [float('inf'), float('inf'), float('inf')]

        # Historial de vueltas de la sesión actual
        self.laps = []

        # Cargar mejores tiempos globales si existen
        self._load_global_bests()

    def set_track(self, track_name):
        """Establecer el circuito actual"""
        self.current_track = track_name
        self._create_session()
        self._load_global_bests()
        print(f"Circuito establecido: {track_name}")

    def _create_session(self):
        """Crear una nueva sesión con timestamp"""
        if not self.current_track:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_session_path = os.path.join(
            self.base_path,
            self.current_track,
            timestamp
        )
        os.makedirs(self.current_session_path, exist_ok=True)

        # Inicializar datos de la sesión
        self.current_session_data = {
            'track': self.current_track,
            'timestamp': timestamp,
            'start_time': datetime.now().isoformat(),
            'best_lap': None,
            'best_sectors': [None, None, None],
            'total_laps': 0
        }

        print(f"Nueva sesión creada: {self.current_session_path}")

    def _load_global_bests(self):
        """Cargar mejores tiempos globales para el circuito actual"""
        if not self.current_track:
            return

        track_path = os.path.join(self.base_path, self.current_track)
        bests_file = os.path.join(track_path, 'bests.json')

        if os.path.exists(bests_file):
            try:
                with open(bests_file, 'r') as f:
                    bests = json.load(f)
                    self.global_best_lap_time = bests.get('best_lap', float('inf'))
                    self.global_best_sectors = bests.get('best_sectors', [float('inf'), float('inf'), float('inf')])
                print(f"Mejores tiempos globales cargados para {self.current_track}")
            except:
                pass

    def _save_global_bests(self):
        """Guardar mejores tiempos globales"""
        if not self.current_track:
            return

        track_path = os.path.join(self.base_path, self.current_track)
        os.makedirs(track_path, exist_ok=True)

        bests_file = os.path.join(track_path, 'bests.json')

        bests = {
            'best_lap': self.global_best_lap_time,
            'best_sectors': self.global_best_sectors,
            'last_updated': datetime.now().isoformat()
        }

        try:
            with open(bests_file, 'w') as f:
                json.dump(bests, f, indent=2)
        except Exception as e:
            print(f"Error guardando mejores tiempos globales: {e}")

    def start_new_lap(self, lap_number):
        """Iniciar nueva vuelta"""
        if self.current_lap_data:
            self.save_lap()

        self.current_lap_number = lap_number
        self.current_lap_data = []
        self.current_lap_time = 0
        self.current_sector_times = [0, 0, 0]
        self.current_sector_splits = [0, 0, 0]
        self.current_sector = 0

        print(f"Iniciando vuelta {lap_number}")

    def append(self, data):
        """Añadir datos a la vuelta actual"""
        self.current_lap_data.append(data.copy())

        # Extraer tiempo de vuelta
        if 'lap_time' in data:
            self.current_lap_time = data['lap_time']
        elif 'lapTime' in data:
            self.current_lap_time = data['lapTime']
        elif 'currentLapTime' in data:
            self.current_lap_time = data['currentLapTime']

        # Detectar sector
        if 'sector' in data:
            new_sector = data['sector']
            if new_sector != self.current_sector:
                # Cambio de sector
                if new_sector > self.current_sector:
                    sector_idx = self.current_sector
                    if sector_idx < 3:
                        # Guardar tiempo de sector
                        sector_time = None
                        for field in ['sector_time', 'sectorTime', f'sector{sector_idx+1}Time']:
                            if field in data:
                                sector_time = data[field]
                                break

                        if sector_time and sector_time > 0:
                            self.current_sector_times[sector_idx] = sector_time

                            # Calcular split
                            if sector_idx == 0:
                                split = sector_time
                            else:
                                split = sector_time - self.current_sector_times[sector_idx-1]

                            self.current_sector_splits[sector_idx] = split

                            # Actualizar mejores sectores de la sesión
                            if split < self.best_sectors[sector_idx]:
                                self.best_sectors[sector_idx] = split
                                self.best_sectors_lap[sector_idx] = self.current_lap_number

                            # Actualizar mejores sectores globales
                            if split < self.global_best_sectors[sector_idx]:
                                self.global_best_sectors[sector_idx] = split
                                self._save_global_bests()

                self.current_sector = new_sector

    def save_lap(self):
        """Guardar la vuelta actual en el historial"""
        if not self.current_lap_data or not self.current_session_path:
            return

        # Calcular tiempo total
        total_time = self.current_lap_time
        if total_time == 0 and len(self.current_lap_data) > 1:
            first_time = self.current_lap_data[0].get('time', 0)
            last_time = self.current_lap_data[-1].get('time', 0)
            total_time = last_time - first_time

        # Crear info de la vuelta
        lap_info = {
            'lap_number': self.current_lap_number,
            'total_time': total_time,
            'sector_times': self.current_sector_times.copy(),
            'sector_splits': self.current_sector_splits.copy(),
            'timestamp': datetime.now().isoformat(),
            'data': self.current_lap_data.copy()
        }

        self.laps.append(lap_info)

        # Actualizar mejor vuelta de la sesión
        if total_time < self.best_lap_time and total_time > 0:
            self.best_lap_time = total_time
            self.best_lap_number = self.current_lap_number
            self.current_session_data['best_lap'] = {
                'lap': self.current_lap_number,
                'time': total_time
            }

        # Actualizar mejor vuelta global
        if total_time < self.global_best_lap_time and total_time > 0:
            self.global_best_lap_time = total_time
            self._save_global_bests()

        # Guardar vuelta a disco
        self._save_lap_to_disk(lap_info)

        # Actualizar datos de la sesión
        self.current_session_data['total_laps'] = len(self.laps)
        self._save_session_data()

        print(f"Vuelta {self.current_lap_number} guardada: {self._format_time(total_time)}")

    def _save_lap_to_disk(self, lap_info):
        """Guardar vuelta en archivo JSON"""
        if not self.current_session_path:
            return

        filename = f"lap_{lap_info['lap_number']:03d}.json"
        filepath = os.path.join(self.current_session_path, filename)

        with open(filepath, 'w') as f:
            json.dump(lap_info, f, indent=2, default=str)

    def _save_session_data(self):
        """Guardar datos de la sesión"""
        if not self.current_session_path:
            return

        session_file = os.path.join(self.current_session_path, 'session.json')

        session_data = {
            'track': self.current_track,
            'timestamp': self.current_session_data['timestamp'],
            'start_time': self.current_session_data['start_time'],
            'end_time': datetime.now().isoformat(),
            'total_laps': len(self.laps),
            'best_lap': self.best_lap_time if self.best_lap_time != float('inf') else None,
            'best_sectors': [s if s != float('inf') else None for s in self.best_sectors],
            'laps': [{
                'number': l['lap_number'],
                'time': l['total_time'],
                'sectors': l['sector_splits']
            } for l in self.laps]
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def get_available_tracks(self):
        """Obtener lista de circuitos disponibles"""
        if not os.path.exists(self.base_path):
            return []

        tracks = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path) and item != '__pycache__':
                tracks.append(item)
        return sorted(tracks)

    def get_track_sessions(self, track_name):
        """Obtener sesiones disponibles para un circuito"""
        track_path = os.path.join(self.base_path, track_name)
        if not os.path.exists(track_path):
            return []

        sessions = []
        for item in os.listdir(track_path):
            item_path = os.path.join(track_path, item)
            if os.path.isdir(item_path) and len(item) == 15:  # Formato YYYYMMDD_HHMMSS
                session_file = os.path.join(item_path, 'session.json')
                if os.path.exists(session_file):
                    try:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                            sessions.append({
                                'path': item_path,
                                'timestamp': item,
                                'data': session_data
                            })
                    except:
                        pass

        # Ordenar por timestamp (más reciente primero)
        return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)

    def load_session(self, session_path):
        """Cargar una sesión completa"""
        session_file = os.path.join(session_path, 'session.json')
        if not os.path.exists(session_file):
            return None

        with open(session_file, 'r') as f:
            session_data = json.load(f)

        # Cargar todas las vueltas
        laps = []
        for i in range(session_data['total_laps']):
            lap_file = os.path.join(session_path, f"lap_{i+1:03d}.json")
            if os.path.exists(lap_file):
                with open(lap_file, 'r') as f:
                    laps.append(json.load(f))

        return {
            'session': session_data,
            'laps': laps
        }

    def get_current_lap_info(self):
        """Obtener información de la vuelta actual"""
        return {
            'lap_number': self.current_lap_number,
            'current_time': self.current_lap_time,
            'current_time_formatted': self._format_time(self.current_lap_time),
            'sector_times': self.current_sector_times.copy(),
            'sector_splits': self.current_sector_splits.copy(),
            'current_sector': self.current_sector
        }

    def get_best_times(self):
        """Obtener mejores tiempos de la sesión actual"""
        return {
            'best_lap': self.best_lap_time if self.best_lap_time != float('inf') else None,
            'best_lap_formatted': self._format_time(self.best_lap_time),
            'best_lap_number': self.best_lap_number,
            'best_sectors': [s if s != float('inf') else None for s in self.best_sectors],
            'best_sectors_formatted': [self._format_time(s) if s != float('inf') else None for s in self.best_sectors],
            'best_sectors_lap': self.best_sectors_lap
        }

    def get_global_bests(self):
        """Obtener mejores tiempos globales del circuito"""
        return {
            'best_lap': self.global_best_lap_time if self.global_best_lap_time != float('inf') else None,
            'best_lap_formatted': self._format_time(self.global_best_lap_time),
            'best_sectors': [s if s != float('inf') else None for s in self.global_best_sectors],
            'best_sectors_formatted': [self._format_time(s) if s != float('inf') else None for s in self.global_best_sectors]
        }

    def get_lap_summary(self):
        """Obtener resumen de todas las vueltas de la sesión"""
        summary = []
        for lap in self.laps:
            summary.append({
                'lap': lap['lap_number'],
                'time': self._format_time(lap['total_time']),
                'sector1': self._format_time(lap['sector_splits'][0]) if lap['sector_splits'][0] > 0 else '--',
                'sector2': self._format_time(lap['sector_splits'][1]) if lap['sector_splits'][1] > 0 else '--',
                'sector3': self._format_time(lap['sector_splits'][2]) if lap['sector_splits'][2] > 0 else '--'
            })
        return summary

    def _format_time(self, seconds):
        """Formatear tiempo en segundos a mm:ss.ms"""
        if seconds is None or seconds <= 0 or seconds == float('inf'):
            return '--:--.---'
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}:{secs:06.3f}"

    def get_current_lap_data(self):
        """Obtener datos de la vuelta actual"""
        return self.current_lap_data

    def get_lap_details(self, lap_number):
        """Obtener datos detallados de una vuelta específica"""
        for lap in self.laps:
            if lap['lap_number'] == lap_number:
                return lap
        return None

    def reset(self):
        """Reiniciar la sesión actual"""
        self.current_lap_data = []
        self.current_lap_number = 0
        self.current_lap_time = 0
        self.current_sector_times = [0, 0, 0]
        self.current_sector_splits = [0, 0, 0]
        self.current_sector = 0
        self.laps = []
        self.best_lap_time = float('inf')
        self.best_sectors = [float('inf'), float('inf'), float('inf')]