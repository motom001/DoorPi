import os
import sys

doorpi_path = os.path.normpath(os.path.join(__file__, "..", "doorpi"))

if not doorpi_path in sys.path:
    sys.path = [doorpi_path] + sys.path
