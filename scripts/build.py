#!/usr/bin/env python3
"""Download Sub2API, apply all plugin patches, run tests, and build the installer."""

import argparse
import gzip
import os
from pathlib import Path, PurePosixPath
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/Wei-Shaw/sub2api.git"
TAG = "v0.2.18"
VERSION = TAG.removeprefix("v")
PNPM = "pnpm@9.15.9"


def run(argv, cwd, env=None):
    print("+ " + " ".join(map(str, argv)), flush=True)
    subprocess.run(list(map(str, argv)), cwd=cwd, env=env, check=True)


def discover_plugins(root):
    modules = root / ".gitmodules"
    if not modules.is_file():
        return []
    result = subprocess.run(
        ["git", "config", "--null", "--file", str(modules), "--get-regexp", r"^submodule\..*\.path$"],
        cwd=root, text=True, capture_output=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip())
    paths = [entry.split("\n", 1)[1] for entry in result.stdout.split("\0") if entry]
    plugins = sorted(path for path in paths if PurePosixPath(path).parts[0] == "plugins")
    for path in plugins:
        if not (root / path / ".git").exists():
            raise RuntimeError(f"Uninitialized submodule {path}. Run: git submodule update --init --recursive -- {path}")
    return [root / path for path in plugins]


def apply_patches(tree, plugins):
    for plugin in plugins:
        for patch in sorted((plugin / "patches").glob("*.patch")):
            print(f"Apply {plugin.name}/{patch.name}", flush=True)
            try:
                run(["git", "apply", "--binary", str(patch)], tree)
            except subprocess.CalledProcessError as error:
                raise RuntimeError(f"Patch failed: {plugin.name}/{patch.name}") from error


def test_entries(owner, tree, env, installer=None):
    support = runpy.run_path(str(ROOT / "tests/support.py"))
    support["test_entries"](owner, tree, env, run, installer)


def collect_licenses(staging, root, plugins):
    destination = staging / "licenses"
    destination.mkdir()
    for owner in [root, *plugins]:
        namespace = Path() if owner == root else owner.relative_to(root / "plugins")
        target = destination / namespace
        target.mkdir(parents=True, exist_ok=True)
        if (owner / "LICENSE").is_file():
            shutil.copyfile(owner / "LICENSE", target / "LICENSE")
        if (owner / "licenses").is_dir():
            shutil.copytree(owner / "licenses", target, dirs_exist_ok=True)


def prepare_installer(binary, workspace, tree, root, plugins):
    staging = workspace / "installer"
    shutil.copytree(root / "scripts/installer", staging)
    lines = (tree / "backend/go.mod").read_text().splitlines()
    directives = [line for line in lines if line.startswith(("go ", "toolchain "))]
    (staging / "go.mod").write_text("module sub2api-plugins-installer\n\n" + "\n".join(directives) + "\n")
    with binary.open("rb") as original, gzip.open(staging / "payload.gz", "wb") as compressed:
        shutil.copyfileobj(original, compressed)
    collect_licenses(staging, root, plugins)
    return staging


def build(root, workspace):
    plugins = discover_plugins(root)
    tree = workspace / "source"
    run(["git", "clone", "--depth", "1", "--branch", TAG, UPSTREAM, tree], workspace)
    apply_patches(tree, plugins)
    env = os.environ.copy()
    for name in ("GOOS", "GOARCH", "CGO_ENABLED"):
        env.pop(name, None)
    env.update(GOFLAGS="-mod=readonly", PYTHONDONTWRITEBYTECODE="1", SUB2API_BUILD_VERSION=VERSION)
    env.setdefault("COREPACK_ENABLE_DOWNLOAD_PROMPT", "0")
    env.setdefault("COREPACK_ENABLE_AUTO_PIN", "0")
    run(["corepack", "prepare", PNPM], root, env)
    run(["corepack", PNPM, "install", "--frozen-lockfile"], tree / "frontend", env)
    run(["corepack", PNPM, "build"], tree / "frontend", env)
    for plugin in plugins:
        test_entries(plugin, tree, env)
    run(["go", "vet", "./internal/server", "./internal/server/routes", "./internal/web"], tree / "backend", env)
    target = dict(env, GOOS="linux", GOARCH="amd64", CGO_ENABLED="0")
    binary = workspace / "sub2api-plugins"
    run(["go", "build", "-tags=embed", "-trimpath", f"-ldflags=-s -w -X main.Version={VERSION} -X main.BuildType=release", "-o", binary, "./cmd/server"], tree / "backend", target)
    staging = prepare_installer(binary, workspace, tree, root, plugins)
    test_entries(root, tree, env, staging)
    installer = workspace / "sub2api-plugins-installer"
    run(["go", "build", "-trimpath", f"-ldflags=-s -w -X main.buildVersion={VERSION}", "-o", installer, "."], staging, target)
    output = root / "dist/build"
    output.mkdir(parents=True, exist_ok=True)
    for artifact in (binary, installer):
        shutil.move(str(artifact), output / artifact.name)
    return output / binary.name, output / installer.name


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="sub2api-plugins-") as temporary:
            print(f"Build workspace: {temporary}", flush=True)
            for output in build(ROOT, Path(temporary)):
                print(output, flush=True)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}. No new outputs were published.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
