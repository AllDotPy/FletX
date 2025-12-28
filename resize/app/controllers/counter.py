from fletx.core import (
    FletXController, RxInt
)

class CounterController(FletXController):
    """Counter page Controller"""
    
    count = RxInt(0)  # Reactive state