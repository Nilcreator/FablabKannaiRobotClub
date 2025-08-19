## Part 1: Japanese Version (日本語版)

### パート1：推奨開発環境のセットアップ

このセクションでは、Raspberry Pi Zero 2Wの準備、特定のレイアウトに合わせたハードウェアの接続、そして必要なすべてのソフトウェアのインストールについてガイドします。目標は、あなたのロボットのために安定して整理された基盤を構築することです。

#### 1.A: ハードウェアのピン設定

コンポーネントを正しく接続することが、最初の重要なステップです。Raspberry Pi Zero 2Wには40ピンのGPIOヘッダーがあります。ここでは、`piservo0`を含むほとんどのPythonライブラリで標準となっている**BCM番号方式**を使用します。

**ピン配置表（改訂版）：**

| コンポーネント | ワイヤー/ピン名 | RPiピン (BCM) | 物理ピン番号 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| **電源 & グラウンド** | 5V 電源 | 5V | 2 または 4 | サーボ、LCD、センサーで共有 |
| | グラウンド | GND | 6, 9, 14, etc. | 全コンポーネント共通のグラウンド |
| **サーボ1 (180° 左脚)** | Signal | GPIO 17 | 11 | 汎用サーボ制御 |
| **サーボ2 (180° 右脚)** | Signal | GPIO 27 | 13 | 汎用サーボ制御 |
| **サーボ3 (360° 左足)** | Signal | GPIO 22 | 15 | 駆動モーター制御 |
| **サーボ4 (360° 右足)** | Signal | GPIO 5 | 29 | 駆動モーター制御 |
| **サーボ5 (180° 左腕)** | Signal | GPIO 25 | 22 | 汎用サーボ制御 |
| **サーボ6 (180° 右腕)** | Signal | GPIO 23 | 16 | 汎用サーボ制御 |
| **LCDディスプレイ (SPI)** | MOSI | GPIO 10 | 19 | SPIデータピン（ハードウェア固定） |
| | SCLK | GPIO 11 | 23 | SPIクロックピン（ハードウェア固定） |
| | CS | GPIO 8 | 24 | SPIチップセレクト（ハードウェア固定） |
| | DC | GPIO 18 | 12 | データ/コマンドピン |
| | RST | GPIO 19 | 35 | リセットピン |
| | BL | GPIO 20 | 38 | バックライト制御 |
| **距離センサー (I2C)** | SDA | GPIO 2 | 3 | I2Cデータピン（ハードウェア固定） |
| | SCL | GPIO 3 | 5 | I2Cクロックピン（ハードウェア固定） |
| **ブザー** | Signal | GPIO 26 | 37 | 音を出すためのシンプルなデジタル出力 |

**なぜこれらのピンなのか？**

  * **ハードウェアインターフェース**: I2C (GPIO 2, 3) と SPI (GPIO 8, 10, 11) のピンはRaspberry Piに固定されたハードウェアインターフェースであり、変更できない理由がこれです。LCDと距離センサーが正しく機能するためには、これらのピンを使用する必要があります。
  * **汎用ピン**: サーボや他のLCD制御ライン（5, 17, 18, 19, 20, 22, 23, 25, 26, 27）に選ばれたGPIOピンは、すべて標準的で信頼性の高い汎用入出力（GPIO）ピンです。特別なブート機能から解放されているため、このプロジェクトに理想的です。

-----

#### 1.B: 推奨プロジェクトファイル構造

プロジェクトを整理し、バージョン管理（GitHubなど）に対応できるように、メインの`NinjaRobot`ディレクトリを作成します。このフォルダには`piservo0`ライブラリ自体を含むすべてのコードを格納し、プロジェクト全体が自己完結型になるようにします。

```
/home/pi/
└── NinjaRobot/        # <-- これがメインのプロジェクトフォルダ兼Gitリポジトリのルートです。
    ├── piservo0/      # サーボライブラリ。プロジェクトに直接クローンします。
    ├── main.py        # ロボットの中心的な「頭脳」となるファイル。
    ├── config.py      # GPIOピンやAPIキーなどの全設定を保存します。
    ├── modules/
    │   ├── __init__.py
    │   ├── servo_control.py
    │   ├── sensor_control.py
    │   ├── display_control.py
    │   └── buzzer_control.py
    └── utils/
        └── ai_assistant.py
```

`piservo0`を`NinjaRobot`の中に配置することで、特定の依存関係のバージョンを含むプロジェクト全体を簡単に管理・共有できます。

-----

#### 1.C: ステップ・バイ・ステップのインストールコマンド

Raspberry Pi OS Lite (64-bit) のクリーンインストール状態で、以下の手順に従ってください。これにより、開発環境全体をゼロからセットアップします。

**ステップ1：システムの更新とシステム依存関係のインストール**
まず、OSが最新の状態であることを確認し、`git`（コードのダウンロード用）と`pigpio`（サーボ制御に不可欠なサービス）をインストールします。

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git pigpio
```

**ステップ2：pigpioデーモンの起動と有効化**
`piservo0`ライブラリは、GPIOピンを管理するために`pigpio`サービスがバックグラウンドで実行されている必要があります。これらのコマンドは、サービスを今すぐ開始し、起動のたびに自動的に立ち上がるようにします。

```bash
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```

**説明**：これは最もよくある失敗の原因です。このデーモンが実行されていないと、`piservo0`はGPIOハードウェアに接続できず、失敗します。

**ステップ3：uv Pythonパッケージマネージャーのインストール**
`piservo0`のガイドブックで推奨されている通り、`uv`はPythonプロジェクトの依存関係や仮想環境を管理するための非常に高速でモダンなツールです。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

**ステップ4：プロジェクト構造の作成とpiservo0のインストール**
次に、`NinjaRobot`ディレクトリを作成し、その中にサーボライブラリをインストールして、自己完結型のプロジェクトを構築します。

```bash
# ホームディレクトリに移動
cd ~

# メインのプロジェクトフォルダを作成
mkdir NinjaRobot
cd NinjaRobot

# 現在のディレクトリにサーボライブラリをクローン
git clone https://github.com/ytani01/piservo0.git

# ライブラリのフォルダに移動してインストール
cd piservo0

# Python仮想環境を作成して有効化
uv venv
source .venv/bin/activate

# piservo0ライブラリを「編集可能」モードでインストール
uv pip install -e .
```

**説明**：`piservo0`ディレクトリ内に単一の仮想環境を作成します。このプロジェクト用の後続のPythonパッケージはすべてここにインストールされ、システム全体のPythonパッケージとの競合を防ぎます。

**ステップ5：追加のハードウェアライブラリのインストール**
仮想環境が有効な状態（プロンプトに`(.venv)`と表示されているはずです）で、他のハードウェアコンポーネントに必要なPythonライブラリをインストールします。

```bash
uv pip install adafruit-circuitpython-vl6180x Pillow requests
```

**説明**：

  * `adafruit-circuitpython-vl6180x`: VL6180X距離センサー用の、信頼性が高く信用できるライブラリ。
  * `Pillow`: 図形、テキスト、画像の描画にWaveshare LCDのサンプルコードで必要とされる、強力な画像処理ライブラリ。
  * `requests`: `piservo0`のAPIサーバーと通信するために使用する、使いやすいHTTPリクエスト用ライブラリ。

これで、正しいピンレイアウトを念頭に置いた開発環境が完全に設定されました。クリーンなプロジェクト構造、必要なすべてのシステムおよびPythonライブラリがインストールされ、中心となる`pigpio`サービスも実行されています。ロボットの制御ソフトウェアを書き始める準備が整いました。

-----

## Part 2: English Version

### Part 1: Recommended Development Environment Setup

This section will guide you through preparing your Raspberry Pi Zero 2W, connecting the hardware according to your specific layout, and installing all the necessary software. The goal is to create a stable and organized foundation for your robot.

#### 1.A: Hardware Pin Configuration

Properly connecting your components is the first critical step. The Raspberry Pi Zero 2W has a 40-pin GPIO header. We will use the **BCM numbering scheme**, which is standard for most Python libraries, including `piservo0`.

**Pinout Table (Revised):**

| Component | Wire/Pin Name | RPi Pin (BCM) | Physical Pin \# | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Power & Ground** | 5V Power | 5V | 2 or 4 | Shared by Servos, LCD, Sensor |
| | Ground | GND | 6, 9, 14, etc. | Common ground for all components |
| **Servo 1 (180° Left Leg)** | Signal | GPIO 17 | 11 | General purpose servo control |
| **Servo 2 (180° Right Leg)** | Signal | GPIO 27 | 13 | General purpose servo control |
| **Servo 3 (360° Left Foot)** | Signal | GPIO 22 | 15 | Drive motor control |
| **Servo 4 (360° Right Foot)** | Signal | GPIO 5 | 29 | Drive motor control |
| **Servo 5 (180° Left Arm)** | Signal | GPIO 25 | 22 | General purpose servo control |
| **Servo 6 (180° Right Arm)** | Signal | GPIO 23 | 16 | General purpose servo control |
| **LCD Display (SPI)** | MOSI | GPIO 10 | 19 | SPI Data Pin (Hardware Specific) |
| | SCLK | GPIO 11 | 23 | SPI Clock Pin (Hardware Specific) |
| | CS | GPIO 8 | 24 | SPI Chip Select (Hardware Specific) |
| | DC | GPIO 18 | 12 | Data/Command Pin |
| | RST | GPIO 19 | 35 | Reset Pin |
| | BL | GPIO 20 | 38 | Backlight Control |
| **Distance Sensor (I2C)** | SDA | GPIO 2 | 3 | I2C Data Pin (Hardware Specific) |
| | SCL | GPIO 3 | 5 | I2C Clock Pin (Hardware Specific) |
| **Buzzer** | Signal | GPIO 26 | 37 | Simple digital output for sound |

**Why these pins?**

  * **Hardware Interfaces**: The I2C (GPIO 2, 3) and SPI (GPIO 8, 10, 11) pins are fixed hardware interfaces on the Raspberry Pi, which is why they remain unchanged. The LCD and Distance Sensor must use these pins to function correctly.
  * **General Purpose Pins**: The GPIO pins selected for the servos and other LCD control lines (5, 17, 18, 19, 20, 22, 23, 25, 26, 27) are all standard, reliable general-purpose input/output (GPIO) pins, free from special boot functions, making them ideal for this project.

-----

#### 1.B: Recommended Project File Structure

To keep the project organized and ready for version control (like GitHub), we will create a main `NinjaRobot` directory. This folder will contain all our code, including the `piservo0` library itself, ensuring the entire project is self-contained.

```
/home/pi/
└── NinjaRobot/        # <-- This is your main project folder and Git repository root.
    ├── piservo0/      # The servo library, cloned directly into your project.
    ├── main.py        # The central "brain" of the robot.
    ├── config.py      # Stores all settings like GPIO pins and API keys.
    ├── modules/
    │   ├── __init__.py
    │   ├── servo_control.py
    │   ├── sensor_control.py
    │   ├── display_control.py
    │   └── buzzer_control.py
    └── utils/
        └── ai_assistant.py
```

By placing `piservo0` inside `NinjaRobot`, the entire project, including its specific dependency version, can be easily managed and shared.

-----

#### 1.C: Step-by-Step Installation Commands

Follow these steps on a fresh installation of Raspberry Pi OS Lite (64-bit). This will set up your entire development environment from scratch.

**Step 1: Update System and Install System Dependencies**
First, ensure your OS is up-to-date and install `git` (for downloading code) and `pigpio` (the critical service for servo control).

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git pigpio
```

**Step 2: Start and Enable the pigpio Daemon**
The `piservo0` library requires the `pigpio` service to be running in the background to manage the GPIO pins. These commands start the service now and ensure it launches automatically on every boot.

```bash
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```

**Explanation**: This is the most common point of failure. If this daemon isn't running, `piservo0` cannot connect to the GPIO hardware and will fail.

**Step 3: Install uv Python Package Manager**
As recommended by the `piservo0` guidebook, `uv` is a very fast and modern tool for managing Python project dependencies and virtual environments.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

**Step 4: Create Project Structure and Install piservo0**
Now we will create our `NinjaRobot` directory and install the servo library inside it, creating a self-contained project.

```bash
# Go to your home directory
cd ~

# Create the main project folder
mkdir NinjaRobot
cd NinjaRobot

# Clone the servo library into the current directory
git clone https://github.com/ytani01/piservo0.git

# Navigate into the library folder to install it
cd piservo0

# Create and activate a Python virtual environment
uv venv
source .venv/bin/activate

# Install the piservo0 library in "editable" mode
uv pip install -e .
```

**Explanation**: We create a single virtual environment inside the `piservo0` directory. All subsequent Python packages for this project will be installed here, preventing conflicts with system-wide Python packages.

**Step 5: Install Additional Hardware Libraries**
With the virtual environment still active (`(.venv)` should be visible in your prompt), install the Python libraries needed for the other hardware components.

```bash
uv pip install adafruit-circuitpython-vl6180x Pillow requests
```

**Explanation**:

  * `adafruit-circuitpython-vl6180x`: A trusted, reliable library for the VL6180X distance sensor.
  * `Pillow`: A powerful imaging library required by the Waveshare LCD example code for drawing shapes, text, and images.
  * `requests`: A user-friendly library for making HTTP requests, which we will use to communicate with the `piservo0` API server.

Your development environment is now fully configured with the correct pin layout in mind. You have a clean project structure, all necessary system and Python libraries are installed, and the core `pigpio` service is running. You are ready to move on to writing the control software for the robot.
