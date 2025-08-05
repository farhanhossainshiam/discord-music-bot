class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.current = None
        self.volume = 0.5
        self.loop = False
    
    def add_to_queue(self, item):
        self.queue.append(item)
    
    def clear_queue(self):
        self.queue.clear()
    
    def skip(self):
        return True
    
    def set_volume(self, vol):
        self.volume = max(0.0, min(2.0, vol))
        if self.current:
            self.current.volume = self.volume
    
    def pause(self):
        return True
    
    def resume(self):
        return True