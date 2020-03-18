import os
import sys

DOORPI_PATH = os.path.normpath(os.path.join(__file__, "..", "doorpi"))
if DOORPI_PATH not in sys.path:
    sys.path = [DOORPI_PATH] + sys.path
