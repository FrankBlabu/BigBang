# DevOps Learnings

- Dev containers use standard format: Dev containers use the standard `.devcontainer/devcontainer.json` format defined by the Dev Containers specification.
- postCreateCommand hook: The `postCreateCommand` hook is ideal for running setup scripts after the container is created.
- Port forwarding in dev containers: Port forwarding requires explicit configuration via the `forwardPorts` array to expose development server ports.
- electron-builder configuration: Configure `electron-builder.yml` for packaging. Key settings: `appId`, `productName`, `directories.buildResources`, platform-specific `icon` paths.
- Package.json script orchestration: Build and packaging scripts should be orchestrated via npm scripts with clear dependencies.
- Installer size budgeting: Track installer size across platforms. Expected breakdown: Python runtime ~50-80 MB, dependencies ~50-70 MB, frontend ~5-10 MB, Electron ~50-80 MB.
- Git configuration for build artifacts: PyInstaller spec files and backend entry points are source code (track in git). Build outputs are typically git-ignored.
- System dependencies for HDF5: Install `libhdf5-dev`, `libsecret-1-dev`, `python3-setuptools`, X11 libraries during container setup.
- Playwright browser caching: Mount `.playwright` directory and set `PLAYWRIGHT_BROWSERS_PATH` to cache browsers between container rebuilds.
- Cross-platform build script validation: Bundle scripts should validate required files exist, Python venv exists, PyInstaller is installed, and previous builds are cleaned.
- electron-builder extraResources: Use `extraResources` in electron-builder.yml to include non-asar files (backend executable, config files).
- No cross-compilation: Each platform must be built on its native OS. Linux builds on Linux, Windows on Windows, macOS on macOS.
- Platform-specific build requirements: Windows requires Visual C++ Build Tools; Linux requires build essentials, libhdf5-dev; macOS requires Xcode Command Line Tools.
- Theia production vs development mode detection: When spawning backend processes in Theia, detect production mode by checking `process.resourcesPath`.
- Unified build scripts across monorepo: Create unified root-level scripts that orchestrate separate build systems.
