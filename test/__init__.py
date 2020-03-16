import os
import sys

doorpi_path = os.path.normpath(os.path.join(__file__, "..", "doorpi"))

if doorpi_path not in sys.path:
    sys.path = [doorpi_path] + sys.path
