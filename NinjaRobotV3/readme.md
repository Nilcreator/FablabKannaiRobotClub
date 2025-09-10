
# NinjaRobotV3 ユーザーガイド

このガイドでは、`pi0disp`、`piservo0`、`vl53l0x_pigpio`、および `pi0buzzer` ライブラリの概要と、`NinjaRobotV3` プロジェクト内での使用方法について説明します。

## 1. 初期設定

このプロジェクトでは、Pythonの仮想環境と依存関係の管理に `uv` を使用します。

### 1.1. 仮想環境の作成と有効化

このプロジェクトでは、仮想環境の使用を推奨します。

```bash
# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate
```

### 1.2. 依存関係のインストール

`uv` を使用して、すべてのライブラリに必要なパッケージをインストールします。

```bash
# サブディレクトリからすべての依存関係をインストール
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
uv pip install -e pi0buzzer
```

## 2. ライブラリの使用

### 2.1. `pi0disp` - ディスプレイドライバ

`pi0disp` ライブラリは、Raspberry Pi 上の ST7789V ベースのディスプレイ用の高速ドライバです。

#### ライブラリとして

Python スクリプトで `ST7789V` クラスを使用してディスプレイを制御できます。

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# ディスプレイの初期化
with ST7789V() as lcd:
    # PIL で画像を作成
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # 青い円を描画
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # 画像を表示
    lcd.display(image)

    time.sleep(5)

    # 部分更新の例
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI の使用法

`pi0disp` コマンドは、ディスプレイをテストするためのシンプルな CLI を提供します。

```bash
# ボールアニメーションデモを実行
uv run pi0disp ball_anime

# ディスプレイをオフにする
uv run pi0disp off
```

### 2.2. `piservo0` - サーボモーター制御

`piservo0` ライブラリは、サーボモーターを精密に制御します。

#### ライブラリとして

`PiServo` または `CalibrableServo` クラスを使用してサーボを制御します。

**基本的な使用法 (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**キャリブレーション済みでの使用法 (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # servo.json からキャリブレーションを読み込みます

servo.move_angle(45)  # 45度に移動
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI の使用法

`piservo0` コマンドは、キャリブレーションとリモート制御を可能にします。

**キャリブレーション**

```bash
# GPIO 17 のサーボをキャリブレーション
uv run piservo0 calib 17
```

**API サーバー**

```bash
# GPIO 17, 27, 22, 25 のサーボ用の API サーバーを起動
uv run piservo0 api-server 17 27 22 25
```

**API クライアント**

```bash
# API サーバーに接続
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - 距離センサー

`vl53l0x_pigpio` ライブラリは、VL53L0X 飛行時間型距離センサー用のドライバです。

#### ライブラリとして

`VL53L0X` クラスを使用して距離測定値を取得します。

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio に接続できませんでした")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"距離: {distance} mm")
        else:
            print("無効なデータ")
finally:
    pi.stop()
```

#### CLI の使用法

`vl53l0x_pigpio` コマンドは、センサーと対話するためのツールを提供します。

**距離の取得**

```bash
# 5 回の距離測定値を取得
uv run vl53l0x_pigpio get --count 5
```

**パフォーマンステスト**

```bash
# 500 回の測定でパフォーマンステストを実行
uv run vl53l0x_pigpio performance --count 500
```

**キャリブレーション**

```bash
# 150mm のターゲットでセンサーをキャリブレーション
uv run vl53l0x_pigpio calibrate --distance 150
```

### 2.4. `pi0buzzer` - ブザーライブラリ

`pi0buzzer` ライブラリは、ピエゾブザー用のシンプルなドライバです。

#### ライブラリとして

Python スクリプトで `Buzzer` クラスを使用してブザーを制御できます。

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# pigpio の初期化
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio デーモンに接続できませんでした")

# ブザーの初期化
buzzer = Buzzer(pi, 18)

# カスタムサウンドの再生
try:
    while True:
        buzzer.play_sound(440, 0.5) # 440 Hz の音を 0.5 秒間再生
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.off()
    pi.stop()
```

#### CLI の使用法

`pi0buzzer` コマンドは、ブザーと対話するためのシンプルな CLI を提供します。

**初期化**

```bash
# GPIO 18 のブザーを初期化
pi0buzzer init 18
```

**音楽の再生**

ブザーを初期化した後、キーボードで音楽を再生できます:

```bash
pi0buzzer playmusic
```

# NinjaRobotV3 User Guide

This guide provides a comprehensive overview of the `pi0disp`, `piservo0`, `vl53l0x_pigpio`, and `pi0buzzer` libraries and how to use them within the `NinjaRobotV3` project.

## 1. Initial Setup

This project uses `uv` for managing Python virtual environments and dependencies.

### 1.1. Create and Activate the Virtual Environment

It is recommended to use a virtual environment for this project.

```bash
# Create the virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

### 1.2. Install Dependencies

Install the necessary packages for all libraries using `uv`.

```bash
# Install all dependencies from the subdirectories
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
uv pip install -e pi0buzzer
```

## 2. Using the Libraries

### 2.1. `pi0disp` - Display Driver

The `pi0disp` library is a high-speed driver for ST7789V-based displays on Raspberry Pi.

#### As a Library

You can use the `ST7789V` class to control the display in your Python scripts.

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# Initialize the display
with ST7789V() as lcd:
    # Create an image with PIL
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # Draw a blue circle
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # Display the image
    lcd.display(image)

    time.sleep(5)

    # Example of partial update
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI Usage

The `pi0disp` command provides a simple CLI for testing the display.

```bash
# Run the ball animation demo
uv run pi0disp ball_anime

# Turn the display off
uv run pi0disp off
```

### 2.2. `piservo0` - Servo Motor Control

The `piservo0` library provides precise control over servo motors.

#### As a Library

Use the `PiServo` or `CalibrableServo` class to control your servos.

**Basic Usage (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**Calibrated Usage (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # Loads calibration from servo.json

servo.move_angle(45)  # Move to 45 degrees
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI Usage

The `piservo0` command allows for calibration and remote control.

**Calibration**

```bash
# Calibrate the servo on GPIO 17
uv run piservo0 calib 17
```

**API Server**

```bash
# Start the API server for servos on GPIO 17, 27, 22, 25
uv run piservo0 api-server 17 27 22 25
```

**API Client**

```bash
# Connect to the API server
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - Distance Sensor

The `vl53l0x_pigpio` library is a driver for the VL53L0X time-of-flight distance sensor.

#### As a Library

Use the `VL53L0X` class to get distance measurements.

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"Distance: {distance} mm")
        else:
            print("Invalid data.")
finally:
    pi.stop()
```

#### CLI Usage

The `vl53l0x_pigpio` command provides tools for interacting with the sensor.

**Get Distance**

```bash
# Get 5 distance readings
uv run vl53l0x_pigpio get --count 5
```

**Performance Test**

```bash
# Run a performance test with 500 measurements
uv run vl53l0x_pigpio performance --count 500
```

**Calibration**

```bash
# Calibrate the sensor with a target at 150mm
uv run vl53l0x_pigpio calibrate --distance 150
```

### 2.4. `pi0buzzer` - Buzzer Driver

The `pi0buzzer` library is a simple driver for a piezo buzzer.

#### As a Library

You can use the `Buzzer` class to control the buzzer in your Python scripts.

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

# Initialize the buzzer
buzzer = Buzzer(pi, 18)

# Play a custom sound
try:
    while True:
        buzzer.play_sound(440, 0.5) # Play 440 Hz for 0.5 seconds
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.off()
    pi.stop()
```

#### CLI Usage

The `pi0buzzer` command provides a simple CLI for interacting with the buzzer.

**Initialization**

```bash
# Initialize the buzzer on GPIO 18
pi0buzzer init 18
```

**Play Music**

After initializing the buzzer, you can play music with it using your keyboard:

```bash
pi0buzzer playmusic
```

---


