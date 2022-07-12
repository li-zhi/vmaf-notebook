import vmaf
from vmaf.core.quality_runner import VmafQualityRunner

import vmaf_notebook


# TODO: use upstream once updated
class VmafnegQualityRunner(VmafQualityRunner):
    """
    VMAF-NEG. See more at: https://github.com/Netflix/vmaf/blob/master/resource/doc/models.md#disabling-enhancement-gain-neg-mode
    """
    TYPE = 'VMAFNEG'
    DEFAULT_MODEL_FILEPATH = vmaf.model_path('vmaf_v0.6.1neg.json')


class VmafspQualityRunner(VmafQualityRunner):
    """
    VMAF version for studio production use case.
    """
    TYPE = 'VMAFSP'
    DEFAULT_MODEL_FILEPATH = vmaf_notebook.model_path('vmaf_v0.6.1neg_mfz.json')
