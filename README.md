# vmaf-notebook
vmaf-notebook is a dockerized environment to run [VMAF](https://github.com/Netflix/vmaf) (and [VMAF-NEG](https://github.com/Netflix/vmaf/blob/master/resource/doc/models.md#disabling-enhancement-gain-neg-mode), [PSNR](https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio), [SSIM](https://en.wikipedia.org/wiki/Structural_similarity)...) video quality metrics.

## Create a docker image

First, pull in the VMAF repo as a submodule and run preparation script:
```shell
git submodule update --init --recursive
./prepare.sh
```

Build the docker image (this will invoke the commands in ./Dockerfile):
```shell
docker build -t vmaf-notebook .
```

## Start a docker container, bash into it and run tests

To start a docker container from the image created and bash into it:
```shell
docker run -dit -v $(pwd):/opt/project --name vmaf-notebook-container vmaf-notebook
docker exec -it vmaf-notebook-container bash
```

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

To stop and remove the container:
```shell
docker rm -f vmaf-notebook-container
```
