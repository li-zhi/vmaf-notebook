from vmaf.core.asset import Asset
from vmaf.core.quality_runner import PsnrQualityRunner, SsimQualityRunner, VmafQualityRunner
from vmaf.tools.misc import MyTestCase

import vmaf_notebook
from vmaf_notebook.quality_runner import VmafnegQualityRunner, VmafspQualityRunner


class QualityRunnerTest(MyTestCase):

    def tearDown(self):
        super().tearDown()

    def setUp(self):
        super().setUp()
        self.asset = \
            Asset(dataset="test_quality_runner", content_id=0, asset_id=0,
                  workdir_root=vmaf_notebook.workdir_path(),
                  ref_path=vmaf_notebook.tests_resource_path('y4m', 'ParkJoy_480x270_50.y4m'),
                  dis_path=vmaf_notebook.tests_resource_path('obu', 'parkjoy_qp160.obu'),
                  asset_dict={
                      'ref_yuv_type': 'notyuv',
                      'ref_start_frame': 0, 'ref_end_frame': 2,
                      'dis_yuv_type': 'notyuv',
                      'dis_start_frame': 0, 'dis_end_frame': 2,
                      'fps': 50,
                      'quality_width': 480, 'quality_height': 270,
                  })

    def test_bitrate(self):
        self.assertAlmostEqual(self.asset.dis_bitrate_kbps_for_entire_file, 11059.2, places=4)

    def test_psnr(self):
        runner = PsnrQualityRunner(
            assets=[self.asset],
            logger=None,
            fifo_mode=False,
            delete_workdir=True,
            result_store=None)
        runner.run(parallelize=False)
        self.assertAlmostEqual(runner.results[0]['PSNR_score'], 41.818631, places=4)

    def test_ssim(self):
        runner = SsimQualityRunner(
            assets=[self.asset],
            logger=None,
            fifo_mode=False,
            delete_workdir=True,
            result_store=None)
        runner.run(parallelize=False)
        self.assertAlmostEqual(runner.results[0]['SSIM_score'], 0.9800443333333333, places=4)

    def test_vmaf(self):
        runner = VmafQualityRunner(
            assets=[self.asset],
            logger=None,
            fifo_mode=False,
            delete_workdir=True,
            result_store=None)
        runner.run(parallelize=False)
        self.assertAlmostEqual(runner.results[0]['VMAF_score'], 98.377901, places=4)

    def test_vmafneg(self):
        runner = VmafnegQualityRunner(
            assets=[self.asset],
            logger=None,
            fifo_mode=False,
            delete_workdir=True,
            result_store=None,
        )
        runner.run(parallelize=False)
        self.assertAlmostEqual(runner.results[0]['VMAFNEG_score'], 97.84970026455467, places=4)

    def test_vmafsp(self):
        runner = VmafspQualityRunner(
            assets=[self.asset],
            logger=None,
            fifo_mode=False,
            delete_workdir=True,
            result_store=None,
        )
        runner.run(parallelize=False)
        self.assertAlmostEqual(runner.results[0]['VMAFSP_score'], 93.51747400708648, places=4)
