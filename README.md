# Sub2API-Plugins

[![Build](https://github.com/Nanboom233/Sub2API-Plugins/actions/workflows/build.yml/badge.svg)](https://github.com/Nanboom233/Sub2API-Plugins/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

将插件补丁应用到 Sub2API，并构建 Linux、macOS 和 Windows 程序及安装器。

| 插件 | 说明 |
| --- | --- |
| [codex-candy-eval](plugins/codex-candy-eval) | 账户评估、自动巡检和通知 |
| [sub2api-quota-extension](plugins/sub2api-quota-extension) | API Key 账户额度查询和自定义额度脚本 |
| [sub2api-plugin-template](plugins/sub2api-plugin-template) | 创建新插件的模板 |

## Installation

在本仓库的 [Actions](../../actions/workflows/build.yml) 中，打开一次成功的 `Build` 运行，按运行安装器的主机平台下载对应文件。

推送和 pull request 触发的构建使用上游最新正式 Release 的 tag。

> [!TIP]
> 如需构建指定版本，在 Actions 中选择 **Run workflow**，并在 `upstream_tag` 中填写准确的上游 tag。默认值为 `v0.2.19`。

文件名中包含该次构建使用的上游 tag。下表以 `v0.2.19` 为例，下载和运行时请替换为实际 tag：

| 主机 | Artifact |
| --- | --- |
| Linux x86_64 | `sub2api-plugins-installer-v0.2.19-linux-amd64` |
| Linux ARM64 | `sub2api-plugins-installer-v0.2.19-linux-arm64` |
| macOS Intel | `sub2api-plugins-installer-v0.2.19-darwin-amd64` |
| macOS Apple Silicon | `sub2api-plugins-installer-v0.2.19-darwin-arm64` |
| Windows x86_64 | `sub2api-plugins-installer-v0.2.19-windows-amd64.exe` |

下载的文件无需解压，可直接运行。以下示例使用 x86_64 安装器，其他平台请替换为对应文件名。

Linux 和 macOS 需要先添加执行权限：

```sh
chmod +x sub2api-plugins-installer-v0.2.19-linux-amd64
./sub2api-plugins-installer-v0.2.19-linux-amd64
```

Windows（PowerShell）：

```powershell
.\sub2api-plugins-installer-v0.2.19-windows-amd64.exe
```

根据现有部署方式选择安装模式：

- **Docker / Compose**：主机需要 Docker CLI 和目标容器的操作权限。选择正在运行的应用容器后，安装器替换 `/app/sub2api`，然后重启同一个容器。
- **原生程序**：输入程序路径和应用地址。安装器会控制现有的官方 systemd 服务。未使用该服务时，按提示用原有方式停止和启动应用，然后确认继续。
- **Apple container**：在 Apple Silicon macOS 上运行安装器并选择应用容器。安装器使用 Linux/arm64 程序替换 `/app/storage/runtime/sub2api`，并且只停止和启动该应用容器。

安装器会显示原程序的备份路径，并在替换后检查 `/health` 和 `/setup/status`。替换或启动失败时，安装器会恢复备份并重新检查原程序。

> [!IMPORTANT]
> 以下情况会使修改失效，需要重新安装：
>
> - **Docker / Compose**：从原镜像重建容器或迁移到新容器。同一容器重启后修改仍然保留。
> - **原生程序**：上游更新覆盖程序。程序重启后修改仍然保留。
> - **Apple container**：镜像 ID 改变后，官方部署会重置 runtime 程序。数据备份不包含 runtime 程序。

### Restore

如果自动恢复失败，或需要回退到安装前的程序，可使用安装器输出的备份路径手动恢复。以下命令中的容器名 `sub2api`、备份路径和程序路径均为示例，请替换为实际值。

#### Docker / Compose

```sh
docker stop sub2api
docker cp /path/to/backup/sub2api sub2api:/app/sub2api
docker start sub2api
```

#### Native Executable

1. 停止应用。使用官方 systemd 服务时运行 `sudo systemctl stop sub2api`，否则按原有方式停止。
2. 将备份复制回程序路径：

   ```sh
   sudo cp -p /path/to/backup/sub2api /opt/sub2api/sub2api
   ```

3. 启动应用。使用官方 systemd 服务时运行 `sudo systemctl start sub2api`，否则按原有方式启动。

#### Apple container

容器需处于运行状态：

```sh
container cp /path/to/backup/sub2api sub2api:/app/storage/runtime/sub2api.plugins-new
container exec -u 0 sub2api sh -c 'chown $(stat -c %u:%g /app/storage/runtime/sub2api) /app/storage/runtime/sub2api.plugins-new && chmod 755 /app/storage/runtime/sub2api.plugins-new && mv -f /app/storage/runtime/sub2api.plugins-new /app/storage/runtime/sub2api'
container stop --time 30 sub2api
container start sub2api
```

恢复后打开管理面板，确认应用可用。

## Development

所需工具版本见 [CI 配置](.github/workflows/build.yml)。

首次克隆：

```sh
git clone --recurse-submodules https://github.com/Nanboom233/Sub2API-Plugins.git
cd Sub2API-Plugins
python3 scripts/build.py
```

已克隆的仓库需先初始化子模块，再构建：

```sh
git submodule update --init --recursive
python3 scripts/build.py
```

构建需要联网下载上游源码和依赖。脚本会自动下载 Sub2API，按插件路径和补丁文件名顺序应用插件补丁，构建前端，并默认运行测试，随后编译服务器和安装器。任一补丁应用失败或测试失败，构建都会失败。

未设置 `UPSTREAM_TAG` 时，脚本使用上游最新正式 Release 的 tag。如需构建指定版本，设置 `UPSTREAM_TAG`：

```sh
UPSTREAM_TAG=v0.2.19 python3 scripts/build.py
```

产物位于：

```text
dist/build/<os>-<arch>/sub2api-plugins-<upstream_tag>-<os>-<arch>
dist/build/<os>-<arch>/sub2api-plugins-installer-<upstream_tag>-<os>-<arch>
```

## License

本仓库的构建与安装器代码采用 [MIT 许可证](LICENSE)。

随产物提供的 Sub2API 和插件代码保留各自的许可证。原始许可证文本位于 [licenses/](licenses/)。

## Credits

- [Sub2API](https://github.com/Wei-Shaw/sub2api)：本项目使用的管理平台。
- [LINUX DO](https://linux.do/)：新的理想型社区。
