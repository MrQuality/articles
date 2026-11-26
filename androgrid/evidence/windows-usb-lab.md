# Windows USB lab setup

This is a source-reviewed setup for the article's operator walkthrough. The CLI flags were checked against `androgrid-cli 0.0.1-alpha.5`. A fresh host installation and QR enrollment through this configuration have not been verified end to end. The recorded HTTP experiment used an already configured worker; it is not evidence of a clean-install pass for this guide.

## Prerequisites

Use a dedicated lab directory and a supported spare Android device. Install Git, the Rust toolchain with the Windows MSVC build prerequisites, JDK 21, Android SDK Platform 34/build tools required by the worker build, and Android Platform Tools (`adb`). Configure the Android SDK path and `JAVA_HOME` for your installation. The reviewed worker declares `minSdk=28` and `compileSdk=34`; that declaration is not a device-compatibility certification.

## 1. Select the source revisions

Run these commands from a new lab directory:

```powershell
git clone https://github.com/ligature-platform/androgrid-backend.git
git -C androgrid-backend checkout 53ab5e51c581358acf822cf2c651d192b6363a4b
git clone https://github.com/ligature-platform/androgrid-android.git
git -C androgrid-android checkout e897036d91903df3dae1d821d05ad9d6846d7f31
```

These are the article's implementation-review references. They are not asserted build identities for the original measurement.

## 2. Build the host binaries and create lab credentials

```powershell
Set-Location .\androgrid-backend
cargo build --locked --release --bin androgrid-backend --bin androgrid-cli
.\target\release\androgrid-cli.exe cert init --out .\demo-data\pki --san 127.0.0.1
```

Use a new `demo-data` directory. Do not overwrite an existing cluster's credentials. Certificate initialization should create `runtime` and `operator` directories. Keep the operator private keys private.

## 3. Start a loopback-only control plane

In that same PowerShell terminal:

```powershell
$LabData = Join-Path (Get-Location).Path 'demo-data'
New-Item -ItemType Directory -Force (Join-Path $LabData 'artifacts') | Out-Null
$env:ANDROGRID_LISTEN_ADDR = '127.0.0.1:50051'
$env:ANDROGRID_ARTIFACT_LISTEN_ADDR = '127.0.0.1:50052'
$env:ANDROGRID_WEB_LISTEN_ADDR = '127.0.0.1:8080'
$env:ANDROGRID_CA_CERT_PATH = Join-Path $LabData 'pki\runtime\ca.crt'
$env:ANDROGRID_SERVER_CERT_PATH = Join-Path $LabData 'pki\runtime\server.crt'
$env:ANDROGRID_SERVER_KEY_PATH = Join-Path $LabData 'pki\runtime\server.key'
$env:ANDROGRID_CA_KEY_PATH = Join-Path $LabData 'pki\operator\ca.key'
$env:ANDROGRID_ARTIFACT_DIR = Join-Path $LabData 'artifacts'
$env:ANDROGRID_HOST_IP = '127.0.0.1'
$env:ANDROGRID_CLUSTER_ENDPOINT = '127.0.0.1:50051'
$env:ANDROGRID_ALLOW_PAIRING = 'true'
$env:ANDROGRID_ENABLE_WEB_UI = 'true'
$env:ANDROGRID_ENABLE_MDNS = 'false'
$env:RUST_LOG = 'info'
.\target\release\androgrid-backend.exe
```

This terminal remains occupied by the backend. Port conflicts must be resolved before continuing. In a separate terminal, confirm that `http://127.0.0.1:8080/api/snapshot` returns the cluster snapshot. The QR endpoint is deliberately loopback: it is intended for the ADB reverse connection, not direct LAN discovery.

## 4. Build and install the worker

From the sibling Android checkout:

```powershell
Set-Location .\androgrid-android
.\gradlew.bat assembleDebug
adb devices
adb install -r -t .\app\build\outputs\apk\debug\app-debug.apk
```

The commands assume exactly 1 authorized ADB device. If installation reports an incompatible signing key, stop and resolve the installation choice; do not uninstall an existing worker and its local state blindly. Open the worker app and respond to its camera and notification prompts as needed for enrollment and participation.

Continue with [step 2 of the article's walkthrough](../#2-connect-and-enroll-the-android-worker). The reader workflow uses the public enrollment interface, not a private certificate-generation script or test-only broadcast receiver.

## If the task does not complete

| Observation | Check |
| --- | --- |
| No worker appears | ADB authorization, reverse rules, app participation state, and enrollment result. |
| TLS or enrollment error | Matching CA and client credentials, endpoint SAN, fresh token, and compatible backend/worker versions. |
| Task remains pending | Worker eligibility, unmetered route classification, and thermal/battery admission state. |
| HTTP security error | The allowlisted hostname and whether DNS resolves to a forbidden private, loopback, or link-local address. |
| Quota or timeout error | The target response size, egress quota, request behavior, and task timeout. |

Do not disable certificate validation or egress restrictions to make the example pass. Preserve the diagnostic output and investigate the cause.
