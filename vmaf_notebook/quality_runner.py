from vmaf.core.quality_runner import VmafQualityRunner

import vmaf_notebook


class VmafspQualityRunner(VmafQualityRunner):
    """
    VMAF version for studio production use case.
    """
    TYPE = 'VMAFSP'
    DEFAULT_MODEL_FILEPATH = vmaf_notebook.model_path('vmaf_v0.6.1neg_mfz.json')
