from datetime import datetime

class Chronograph:

    """
    Class to create a timer
    
    :param title: Title of the timer
    :type title: str
    """

    def __init__(self, title:str):
        self.title = title
        self.start_time = datetime.now()

    def time_measure(self):
        """
        Return the time measured by the timer
        
        """
        elapsed_time = datetime.now() - self.start_time
        return elapsed_time.total_seconds()