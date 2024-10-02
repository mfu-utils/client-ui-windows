import os.path
from config import CWD

from App.helpers import env

__CONFIG__ = {
    # For convertor set test data from demo assets
    'debug': env('CONVERTOR_DEBUG', False),

    'debug_image': env('CONVERTOR_DEBUG_IMAGE', os.path.join(CWD, 'tests', 'images', 'demo.tiff')),

    'debug_command': env('CONVERTOR_DEBUG_COMMAND', False),
}
