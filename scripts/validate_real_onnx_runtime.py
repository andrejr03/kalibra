from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_RUNTIME_TEST = (
    "tests/test_onnx_provider.py::test_onnx_provider_real_runtime_integration"
)
TEST_COMMAND = ("-m", "pytest", "tests/test_onnx_provider.py", "-q", "-rA")
TEST_DEPENDENCIES = ("pytest", "numpy")
OPTIONAL_RUNTIME_DEPENDENCY = "onnxruntime"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kalibra-onnx-runtime-evidence-") as tmp:
        venv_dir = Path(tmp) / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
        python = _venv_python(venv_dir)

        _run(
            python,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        )
        _run(
            python,
            "-m",
            "pip",
            "install",
            *TEST_DEPENDENCIES,
            OPTIONAL_RUNTIME_DEPENDENCY,
        )

        completed = _run(
            python,
            *TEST_COMMAND,
            capture_output=True,
            check=False,
        )
        output = f"{completed.stdout}\n{completed.stderr}"
        print(output, end="")
        if completed.returncode != 0:
            return completed.returncode
        if f"PASSED {REAL_RUNTIME_TEST}" not in output:
            print(
                "real ONNX Runtime provider test did not produce PASS evidence",
                file=sys.stderr,
            )
            return 1
        if f"SKIPPED {REAL_RUNTIME_TEST}" in output:
            print(
                "real ONNX Runtime provider test was skipped",
                file=sys.stderr,
            )
            return 1
        return 0


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python3"


def _run(
    python: Path,
    *args: str,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    completed = subprocess.run(
        [str(python), *args],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=capture_output,
    )
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


if __name__ == "__main__":
    raise SystemExit(main())
