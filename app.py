"""Trying things out"""

from pathlib import Path
import docker
from docker.models.containers import Container, ExecResult
from docker.models.images import Image


curr_path = Path(".")
import_packages_path = Path("./import-packages")
docker_path = Path("./docker")
client = docker.from_env()  # get default socket and config in env
WORKDIR = "/sivpack"


def build_image(tag: str) -> Image:
    image = client.images.build(path=str(docker_path.absolute()), tag=tag)
    return image[0]


def initialize_container(image: Image) -> Container:
    volumes = {str(curr_path.absolute()): {"bind": WORKDIR, "mode": "rw"}}

    container = client.containers.run(
        image,
        auto_remove=True,
        detach=True,
        ports=None,
        stdin_open=True,
        stdout=True,
        tty=True,
        volumes=volumes,
        entrypoint="bash"
    )
    return container


def run_command(cmd: str, container: Container) -> ExecResult:
    results = container.exec_run(cmd, workdir=WORKDIR)
    return results


def analyze_output(results: ExecResult) -> None:
    if results.exit_code == 0:
        return

    # error occurred
    print(f"{cmd} failed with output: {results.output}")


if __name__ == "__main__":
    image = build_image("siv-test-container:0.0.1")
    print(image)
    container = initialize_container(image)

    python_files = [item for item in import_packages_path.iterdir() if item.suffix == ".py"]

    for file in python_files:
        cmd = ["python3.6", str(file)]
        results = run_command(cmd, container)
        analyze_output(results)

    container.stop()
