from App.Core import Config
from App.Core.Abstract import AbstractSubprocess
from App.Core.Logger import Log


#: TODO: Create options list for printer
class LpoptionsSubprocess(AbstractSubprocess):
    PARAMETER_EDGE_ENHANCEMENT = "JCLEdgeEnhance/Edge Enhancement"
    PARAMETER_SKIP_BLANK_PAGES = "JCLSkipBlankPages/Skip Blank Pages"
    PARAMETER_PAPER_SOURCE = "InputSlot/Paper Source"
    PARAMETER_COLOR_MODE = "ColorModel/Color Mode"
    PARAMETER_BRIGHTNESS = "seBrightness/[Adjustment Levels] Brightness"
    PARAMETER_TONER_SAVE = "TonerSaveMode/Toner Save"
    PARAMETER_PAPER_SIZE = "PageSize/Paper Size"
    PARAMETER_PAPER_TYPE = "MediaType/Paper Type"
    PARAMETER_CONTRAST = "secContrast Adjustment Levels Contrast"
    PARAMETER_QUALITY = "Quality/Quality"

    PARAMETER_KEY_EDGE_ENHANCEMENT = "edge_enhancement"
    PARAMETER_KEY_SKIP_BLANK_PAGES = "skip_blank_pages"
    PARAMETER_KEY_PAPER_SOURCE = "paper_source"
    PARAMETER_KEY_COLOR_MODE = "color_mode"
    PARAMETER_KEY_BRIGHTNESS = "brightness"
    PARAMETER_KEY_TONER_SAVE = "toner_save"
    PARAMETER_KEY_PAPER_SIZE = "paper_save"
    PARAMETER_KEY_PAPER_TYPE = "paper_type"
    PARAMETER_KEY_CONTRAST = "contrast"
    PARAMETER_KEY_QUALITY = "quality"

    PARAMETERS_NAMES = {
        PARAMETER_EDGE_ENHANCEMENT: PARAMETER_KEY_EDGE_ENHANCEMENT,
        PARAMETER_SKIP_BLANK_PAGES: PARAMETER_KEY_SKIP_BLANK_PAGES,
        PARAMETER_PAPER_SOURCE: PARAMETER_KEY_PAPER_SOURCE,
        PARAMETER_COLOR_MODE: PARAMETER_KEY_COLOR_MODE,
        PARAMETER_BRIGHTNESS: PARAMETER_KEY_BRIGHTNESS,
        PARAMETER_TONER_SAVE: PARAMETER_KEY_TONER_SAVE,
        PARAMETER_PAPER_SIZE: PARAMETER_KEY_PAPER_SIZE,
        PARAMETER_PAPER_TYPE: PARAMETER_KEY_PAPER_TYPE,
        PARAMETER_CONTRAST: PARAMETER_KEY_CONTRAST,
        PARAMETER_QUALITY: PARAMETER_KEY_QUALITY,
    }

    def __init__(self, log: Log, config: Config):
        super(LpoptionsSubprocess, self).__init__(log, config, "lpoptions")
