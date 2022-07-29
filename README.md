# vmaf-notebook
vmaf-notebook is a dockerized environment to run [VMAF](https://github.com/Netflix/vmaf) (and [VMAF-NEG](https://github.com/Netflix/vmaf/blob/master/resource/doc/models.md#disabling-enhancement-gain-neg-mode), [PSNR](https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio), [SSIM](https://en.wikipedia.org/wiki/Structural_similarity)...) video quality metrics.

## Create a docker image

First, pull in the VMAF repo as a submodule and run preparation script:
```shell
git submodule update --init --recursive --depth 1
./prepare.sh
```

Build the docker image (this will invoke the commands in ./Dockerfile):
```shell
docker build -t vmaf-notebook .
```

## Start a docker container, bash into it and run tests

To start a docker container from the image created and bash into it:
```shell
docker run -dit --volume $(pwd):/opt/project --name vmaf-notebook-container vmaf-notebook
docker exec -it vmaf-notebook-container bash
```

(If you want to mount additional volumes, you can do something like adding a second `--volume /Users:/Users` to mount the entire `/Users` directory in your native OS to the docker container.)

To ensure that the container is configured correctly, run tests by invoking `tox` (this invokes commands in the ./tox.ini file):
```shell
tox
```
This command runs three checks: the standard (py39), coverage and style. Each can be individually triggered as well:
```shell
tox -e py39
tox -e coverage
tox -e style
```
You should expect all tests pass.

After use, to exit the container:
```shell
exit
```

To stop and destroy the container:
```shell
docker rm -f vmaf-notebook-container
```

## Run VMAF and other video quality metrics

Assume you are inside the docker container. There are two ways of running VMAF and other metrics:

### Way #1: the bare-bones way

The bare-bones way is to manually decode (using `ffmpeg`) both the reference and the encoded videos into raw videos (YUV format), and invoking the `vmaf` command line (aliased as `vmafossexec_lts` below for production reasons):
```shell
/tools/ffmpeg/ffmpeg -i /opt/project/tests/resource/y4m/ParkJoy_480x270_50.y4m -f rawvideo -pix_fmt yuv420p /opt/project/workspace/ParkJoy_480x270_50.yuv
/tools/ffmpeg/ffmpeg -i /opt/project/tests/resource/obu/parkjoy_qp160.obu -f rawvideo -pix_fmt yuv420p /opt/project/workspace/parkjoy_qp160.yuv
/usr/local/bin/vmaf --reference /opt/project/workspace/ParkJoy_480x270_50.yuv --distorted /opt/project/workspace/parkjoy_qp160.yuv --width 480 --height 270 --pixel_format 420 --bitdepth 8 --xml --feature psnr --feature float_ssim --model path=/opt/project/vmaf/python/vmaf/model/vmaf_v0.6.1.json:name=vmaf --model path=/opt/project/vmaf/python/vmaf/model/vmaf_v0.6.1neg.json:name=vmafneg --quiet --output /dev/stdout
```
You should expect output like:
```xml
<VMAF version="e19d489a">

    ...

    <metric name="psnr_y" min="41.751970" max="41.862815" mean="41.818631" harmonic_mean="41.818577" />
    <metric name="psnr_cb" min="42.725539" max="42.823630" mean="42.780453" harmonic_mean="42.780415" />
    <metric name="psnr_cr" min="43.622090" max="43.717101" mean="43.669397" harmonic_mean="43.669364" />
    <metric name="float_ssim" min="0.979634" max="0.980331" mean="0.980044" harmonic_mean="0.980044" />
    <metric name="vmaf" min="95.133704" max="100.000000" mean="98.377901" harmonic_mean="98.324069" />
    <metric name="vmafneg" min="93.549100" max="100.000000" mean="97.849700" harmonic_mean="97.754068" />
  </pooled_metrics>
  <aggregate_metrics />
</VMAF>
```
It computes the per-frame and aggregate VMAF, VMAF-NEG, PSNR, SSIM video quality metrics of a reference and an encoded video and report back the results in a XML file.

### Way #2: construct a script using the VMAF Python library

The second way is to utilize the Python library's `Asset` and `QualityRunner` classes to construct a script.

Enter the Python environment PYTHONPATH environment variable properly set:
```shell
PYTHONPATH=.:vmaf/python python
```

First, construct an `Asset` object:
```python
from vmaf.core.asset import Asset
import vmaf_notebook

asset = Asset(dataset="demo", content_id=0, asset_id=0,
              workdir_root=vmaf_notebook.workdir_path(),
              ref_path=vmaf_notebook.tests_resource_path('y4m', 'ParkJoy_480x270_50.y4m'),
              dis_path=vmaf_notebook.tests_resource_path('obu', 'parkjoy_qp160.obu'),
              asset_dict={
                  'ref_yuv_type': 'notyuv', 'ref_start_frame': 0, 'ref_end_frame': 2,
                  'dis_yuv_type': 'notyuv', 'dis_start_frame': 0, 'dis_end_frame': 2,
                  'fps': 50, 'quality_width': 480, 'quality_height': 270})
```

(If you want to construct your own `Asset` objects, follow the pattern and set the paths to the video files in your native OS's directory. Note that the `/Users` directory in the native OS is mapped to the `/Users` directory in the docker container. The mapping is defined in the ./.newt.yml file.)

Then, invoke four instances of `QualityRunner` subclasses:
```python
from vmaf.core.quality_runner import VmafQualityRunner, PsnrQualityRunner, SsimQualityRunner, VmafnegQualityRunner

runners = []
for QualityRunner in [VmafQualityRunner,
                      VmafnegQualityRunner,
                      PsnrQualityRunner,
                      SsimQualityRunner]:
    runner = QualityRunner(assets=[asset],
                           logger=None,
                           fifo_mode=True,
                           delete_workdir=True,
                           result_store=None,
                           optional_dict2={'n_threads': 10})
    runners.append(runner)
    runner.run()
    print(f'asset has average {runner.TYPE} score {runner.results[0][runner.get_score_key()]:.4f}')
```
This yields output:
```
asset has average VMAF score 98.3779
asset has average VMAFNEG score 97.8497
asset has average PSNR score 41.8186
asset has average SSIM score 0.9800
```

To obtain per-frame scores of a metric, use `get_scores_key()` instead of `get_score_key` method:
```python
for runner in runners:
    print(f'asset has per-frame {runner.TYPE} scores {runner.results[0][runner.get_scores_key()]}')
```
with output:
```
asset has per-frame VMAF scores [ 95.1337019 100.        100.       ]
asset has per-frame VMAFNEG scores [ 93.54910079 100.         100.        ]
asset has per-frame PSNR scores [41.75197, 41.841107, 41.862815]
asset has per-frame SSIM scores [0.979634, 0.980168, 0.980331]
```

As a bonus, you can also compute the bitrate of the encoded video:
```python
print(f'asset has bitrate {asset.dis_bitrate_kbps_for_entire_file:.2f} Kbps.')
```
with output:
```
asset has bitrate 11059.20 Kbps.
```

You can also plot the time series of scores:
```python
import matplotlib.pyplot as plt
import vmaf_notebook

vmaf_runner = runners[0]
vmafneg_runner = runners[1]
fig, ax = plt.subplots()
ax.plot(vmaf_runner.results[0][vmaf_runner.get_scores_key()],
        label=f"{vmaf_runner.TYPE} avg score: {vmaf_runner.results[0][vmaf_runner.get_score_key()]:.2f}")
ax.plot(vmafneg_runner.results[0][vmafneg_runner.get_scores_key()],
        label=f"{vmafneg_runner.TYPE} avg score: {vmafneg_runner.results[0][vmafneg_runner.get_score_key()]:.2f}")
ax.set_xlabel('Frame Number')
ax.set_ylabel('Score')
ax.grid()
ax.legend()
fig.tight_layout()
plt.savefig(vmaf_notebook.workspace_path('time_series.png'))
```
with output .png saved at ./workspace/time_series.png:

![time_series](doc/time_series.png)

## More on constructing an `Asset` object

`Asset` is an essentially class of the VMAF Python library. It provides some degrees of flexibility to construct the input to VMAF or other quality metrics. Above you have seen one example, reproduced below:
```python
asset = Asset(dataset="demo", content_id=0, asset_id=0,
              workdir_root=vmaf_notebook.workdir_path(),
              ref_path=vmaf_notebook.tests_resource_path('y4m', 'ParkJoy_480x270_50.y4m'),
              dis_path=vmaf_notebook.tests_resource_path('obu', 'parkjoy_qp160.obu'),
              asset_dict={
                  'ref_yuv_type': 'notyuv', 'ref_start_frame': 0, 'ref_end_frame': 2,
                  'dis_yuv_type': 'notyuv', 'dis_start_frame': 0, 'dis_end_frame': 2,
                  'fps': 50, 'quality_width': 480, 'quality_height': 270})
```

The fields `dataset`, `content_id` and `asset_id` will help uniquely identify an asset. This is inherited naturally from converting a dataset file into a list of assets by the [`read_dataset`](https://github.com/Netflix/vmaf/blob/01a5f4d25f11314cf2693ea5c7e5adf5437ee1e0/python/vmaf/routine.py#L20) function. These fields also comes handy to form a unique signature string, to uniquely identify an asset when caching its corresponding quality results already computed (see more in the next section).

Unsurprisingly, the `ref_path` and `dis_path` corresponds to the file path to the reference and distorted videos.

Here both the reference video and distorted video are with type `notyuv`, literally means `not YUV`. This implies that the file must be a non-YUV format that can be automatically recognized by `ffmpeg` (or by `ffprobe`). In this example, both the .y4m (YUV4MPEG) and .obu (elementary stream for AV1) can be recognized by the latest version of `ffmpeg`. 

You may wonder: what if the input reference or distorted video (or both) are YUV format? In this case, since YUV is a header-less format, you will have to manually specify its pixel format and resolution. One example is the following:
```python
asset = Asset(dataset="demo", content_id=0, asset_id=0,
              workdir_root=vmaf_notebook.workdir_path(),
              ref_path='ParkJoy_480x270_50.yuv',
              dis_path='parkjoy_qp160.yuv',
              asset_dict={
                  'ref_yuv_type': 'yuv420p', 'ref_width': 480, 'ref_height': 270, 'ref_start_frame': 0, 'ref_end_frame': 2,
                  'dis_yuv_type': 'yuv420p', 'dis_width': 480, 'dis_height': 270, 'dis_start_frame': 0, 'dis_end_frame': 2,
                  'fps': 50, 'quality_width': 480, 'quality_height': 270})
```
In this example, both the reference and distorted videos are both YUV with 420 chroma subsampling and 8-bit depth. For more information on the supported YUV types, refer to the class implementation [here](https://github.com/Netflix/vmaf/blob/01a5f4d25f11314cf2693ea5c7e5adf5437ee1e0/python/vmaf/core/asset.py).

You may notice that there are three resolutions specified: reference resolution (`(ref_width, ref_height)`), distorted resolution (`(dis_width, dis_height)`), and "quality resolution" (`(quality_width, quality_height)`). In the example above they are the same: `(480, 270)`. This is not always the case (refer to the "Computing VMAF at the Right Resolution" section of [this tech blog](https://netflixtechblog.com/vmaf-the-journey-continues-44b51ee9ed12) for the rationale behind). In the more generic case, the reference and distorted videos can be different resolutions, and they can both be rescaled to a "quality resolution" before VMAF is calculated. When rescaling is applicable, the rescaling (or `resampling_type`) can be specified (the default type is `bicubic`). The example below illustrates a 2160p source and a 720p distorted video and having their VMAF to be calculated at 1080p, with the reference scaled by lanczos and the distorted scaled by bicubic:
```python
asset = Asset(dataset="demo", content_id=0, asset_id=0,
              workdir_root=vmaf_notebook.workdir_path(),
              ref_path='x_3840x2160.yuv',
              dis_path='x_1280x720.yuv',
              asset_dict={
                  'ref_yuv_type': 'yuv420p', 'ref_width': 3840, 'ref_height': 2160, 'ref_resampling_type': 'lanczos', 'ref_start_frame': 0, 'ref_end_frame': 2,
                  'dis_yuv_type': 'yuv420p', 'dis_width': 1280, 'dis_height': 720, 'dis_resampling_type': 'bicubic', 'dis_start_frame': 0, 'dis_end_frame': 2,
                  'fps': 50, 'quality_width': 1920, 'quality_height': 1080})
```

Similar to resolutions, the reference and distorted videos may have different YUV types. It is custom to convert them to a common YUV types before the VMAF calculation. This is specified by the `workfile_yuv_type` field. For example, the following example convert a `yuv422p` reference and a `yuv420p` distorted video both into `yuv444p16le` before VMAF calculation:
```python
asset = Asset(dataset="demo", content_id=0, asset_id=0,
              workdir_root=vmaf_notebook.workdir_path(),
              ref_path='x_3840x2160.yuv',
              dis_path='x_1280x720.yuv',
              asset_dict={
                  'ref_yuv_type': 'yuv422p', 'ref_width': 3840, 'ref_height': 2160, 'ref_resampling_type': 'lanczos', 'ref_start_frame': 0, 'ref_end_frame': 2,
                  'dis_yuv_type': 'yuv420p', 'dis_width': 1280, 'dis_height': 720, 'dis_resampling_type': 'bicubic', 'dis_start_frame': 0, 'dis_end_frame': 2,
                  'fps': 50, 'quality_width': 1920, 'quality_height': 1080, 'workfile_yuv_type': 'yuv444p16le'})
```

The first example also specified the starting and ending frames of both videos. If not specified, it will assume the decoding starts with the first frame until all the frames are processed. If the two videos are of different frames, it will process until the smaller number of frames are processed.

Lastly, specifying `fps` (frames per second) will help determine the duration of the video (together with the number of frames to process), which in turn will help determine the distorted video's bitrate (in Kbit/sec, or Kbps). Note that `fps` will not impact the VMAF numerical result, since the current VMAF version is frame-rate agnostic (this may change in future versions).

### More on constructing a `QualityRunner` object

There are a number of house-keeping features in construction a `QualityRunner` object, including running with multi-threading, running on multiple assets in parallel, caching results already computed, etc. One simple example is below:
```python
runner = VmafQualityRunner(assets=[asset],
                           logger=None,
                           fifo_mode=True,
                           delete_workdir=True,
                           result_store=None,
                           optional_dict2={'n_threads': 10})
runner.run()
print(f'asset has average {runner.TYPE} score {runner.results[0][runner.get_score_key()]:.4f}')
```
Here logger can be assigned to `logging.getLogger()`. `fifo_mode` controls if you want to set intermediate raw videos as a FIFO pipe (`True`), or simply save them to disk before proceeding with VMAF calculation (`False`). I would set the field to `True` generally to save disk space during execution (in particular: parallel execution), but I may turn it to `False` during debugging, since FIFO mode may hide error messages. `delete_workdir` should be set to `True` in general to automatically clean up intermediate files, but setting it to `False` will come handy during debugging. The `n_threads` in the `optional_dict2` dictionary (forgive the anti-pattern of variable naming!!) indicates that you are running with 10 concurrent threads.

More on the rest of the options below.

If you have more than one assets, you can run them in parallel as below:
```python
runner = VmafQualityRunner(assets=[asset1, asset2],
                           logger=None,
                           fifo_mode=True,
                           delete_workdir=True,
                           result_store=None,
                           optional_dict2={'n_threads': 10})
runner.run(parallelize=True)
for result in runner.results:
    print(f'asset has average {runner.TYPE} score {result[runner.get_score_key()]:.4f}')
```
The `runner.results` will be a list of results in the same order as the input assets.

It is possible to cache the results already computed, such that the next time you run the same function, it avoids re-run the computations but to retrieve the result from the cache in the local file. This is done as follows:
```python
result_store = FileSystemResultStore(result_store_dir='path_to_directory')
runner = VmafQualityRunner(assets=[asset1, asset2],
                           logger=None,
                           fifo_mode=True,
                           delete_workdir=True,
                           result_store=result_store,
                           optional_dict2={'n_threads': 10})
runner.run(parallelize=True)
for result in runner.results:
    print(f'asset has average {runner.TYPE} score {result[runner.get_score_key()]:.4f}')
```

## Set up the docker image as Python interpreter in PyCharm Professional

To set up the docker image as the Python interpreter Pycharm will help debugging the Python scripts. You need PyCharm Professional because that the baseline version does not have the feature to import a docker image as interpreter.

To import the docker image created to PyCharm: Menu -> PyCharm -> Preferences... -> Project -> Python Interpreter -> on the upper-right corner, click on the gear icon -> Add... -> Docker -> Image name is the latest image built; Python interpreter path is `python` -> click 'OK'.

On the Project panel on the left, navigate to the directory `vmaf/python` -> right click -> Mark Directory as Sources Root.
