from pyaccsharedmemory import accSharedMemory

class TelemetryReader:
    def __init__(self):
        self.asm = accSharedMemory()

    def read(self):
        sm = self.asm.read_shared_memory()
        if sm is None:
            return None

        return {
            "speed_kmh": sm.Physics.speed_kmh,
            "rpm": sm.Physics.rpm,
            "gear": sm.Physics.gear,
            "gas": sm.Physics.gas,
            "brake": sm.Physics.brake,
            "steer_angle": sm.Physics.steer_angle,
            # Graphics fields:
            "current_time_ms": sm.Graphics.current_time,   # current lap ms
            "last_time_ms": sm.Graphics.last_time,         # last lap ms
            "completed_laps": sm.Graphics.completed_lap    # lap counter
        }

    def close(self):
        self.asm.close()