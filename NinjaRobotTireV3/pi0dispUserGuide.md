### Part 1: Japanese Version (日本語版)

# pi0disp ユーザーガイド (初心者向け)

## 1. はじめに

`pi0disp`は、Raspberry Piを使ってST7789Vというチップを搭載した小型LCDディスプレイを制御するためのPythonライブラリです。このガイドでは、プログラミングやRaspberry Piが初めての方でも、ゼロからLCDアプリケーションを構築できるように、手順を一つずつ丁寧に解説します。

## 2. 準備するもの (ハードウェア)

まず、プロジェクトに必要な部品を揃えましょう。

*   **Raspberry Pi 本体**: Raspberry Pi 3, 4, Zero, Zero 2W のいずれか
*   **ST7789V LCDディスプレイ**: (例: Waveshare 1.3inch LCD Hat, Pimoroni Display HAT Miniなど)
*   **microSDカード**: 16GB以上を推奨
*   **Raspberry Pi用電源アダプター**
*   **その他**: (初期設定用) USBキーボード、マウス、HDMIケーブル、モニター

## 3. ハードウェアのセットアップ

次に、LCDディスプレイをRaspberry Piに接続します。

*   **HATタイプの場合**: Raspberry PiのGPIOピンヘッダーに、向きを合わせてLCDディスプレイを上からしっかりと差し込みます。
*   **ブレッドボードタイプの場合**: ジャンパーワイヤーを使って、LCDの各ピンをRaspberry Piの対応するGPIOピンに接続します。接続するピンはLCDの製品仕様書を確認してください。

> **なぜこれが必要なの？**
> Raspberry PiとLCDディスプレイが物理的に接続されていないと、電気信号を送受信できず、画面に何も表示することができません。HATタイプは接続が簡単なので初心者におすすめです。

## 4. Raspberry Piの初期設定とソフトウェアのインストール

ハードウェアの準備ができたら、次はソフトウェアのセットアップです。

### 4.1. Raspberry Pi OSのインストール

まだOSをインストールしていない場合は、公式サイトの「Raspberry Pi Imager」を使ってmicroSDカードにOSを書き込みます。詳しい手順は[Raspberry Pi公式サイト](https://www.raspberrypi.com/software/)を参照してください。

### 4.2. SPIインターフェースの有効化

`pi0disp`はSPIという通信方式を使ってLCDと高速にデータをやり取りします。標準では無効になっているため、有効化する必要があります。

1.  デスクトップ左上のラズベリーパイアイコンをクリックし、「設定」 > 「Raspberry Pi の設定」を開きます。
2.  「インターフェイス」タブを選択します。
3.  リストの中から「SPI」を見つけ、「有効」を選択します。
4.  「OK」をクリックして設定を保存し、再起動します。

### 4.3. 必要なライブラリのインストール

ターミナル（コマンド入力画面）を開き、以下のコマンドを一行ずつ実行して、`pi0disp`が動作するために必要なソフトウェアをインストールします。

**1. `pigpio` Cライブラリとデーモンのインストール**

`pigpio`はGPIOを高速に制御するための重要なライブラリです。

```bash
# システムのパッケージリストを更新
sudo apt-get update

# pigpioをインストール
sudo apt-get install pigpio -y

# Raspberry Pi起動時にpigpioデーモンが自動で起動するように設定
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

**2. Pythonライブラリのインストール**

次に、Pythonから`pigpio`や画像処理を扱うためのライブラリをインストールします。

```bash
pip install pigpio Pillow numpy
```
> **なぜこれが必要なの？**
> `SPI`は高速なデータ通信規格です。`pigpio`はRaspberry Piのピンを正確にコントロールする心臓部。`Pillow`と`numpy`は画像を描画したり計算したりするための道具です。これらのソフトウェアを正しくインストールすることで、初めてPythonプログラムからLCDを制御できるようになります。

## 5. サンプルコードの実行

ライブラリに付属しているサンプルコードを実行して、セットアップが正しく完了したか確認しましょう。

### 5.1. サンプルコードのダウンロード

まず、`git`コマンドを使って、GitHubから`pi0disp`の全ファイルをダウンロードします。

```bash
git clone https://github.com/ytani01/pi0disp.git
```

### 5.2. `pi0disp`ライブラリのインストール**

最後に、このプロジェクトの主役である`pi0disp`をインストールします。インストールには2つの方法があります。

*   **方法A: PyPIからインストール **
    インターネット経由で簡単にインストールできます。
    ```bash
    pip install pi0disp
    ```

*   **方法B: ローカルからインストール**
    もしGitHubからソースコードを直接ダウンロードした場合（例えば、後のステップで使う`git clone`コマンドを実行した後）、そのフォルダ内からインストールできます。
    ```bash
    # まず、git cloneでダウンロードしたpi0dispフォルダに移動します
    # cd pi0disp

    # 次のコマンドでインストールします
    pip install .
    ```

### 5.3. サンプルの実行

ダウンロードしたフォルダに移動し、サンプルプログラムを実行します。

```bash
cd pi0disp/examples
python simple_text.py
```

このコマンドを実行すると、LCDに「Hello World!」という文字が表示されるはずです。表示されれば、セットアップは成功です！

## 6. 自分でプログラムを書いてみよう

最後に、簡単なプログラムを自分で作成してみましょう。

### 6.1. プログラムの作成

Thonny IDE（Raspberry Pi OSにプリインストールされています）などのエディタを開き、以下のコードを入力して `my_display.py` という名前で保存します。

```python
# 必要なライブラリをインポート
from pi0disp import ST7789V
from PIL import Image, ImageDraw, ImageFont
import time

# LCDディスプレイを初期化
with ST7789V() as lcd:
    # 新しい画像を作成 (黒い背景)
    # lcd.width と lcd.height で自動的に画面サイズを取得
    img = Image.new("RGB", (lcd.width, lcd.height), "black")

    # 画像に描画するための準備
    draw = ImageDraw.Draw(img)

    # 赤色の四角形を描画
    # (左上のx, y, 右下のx, y)
    draw.rectangle((10, 10, 100, 50), fill="red")

    # 白色でテキストを描画
    draw.text((10, 70), "My First App!", fill="white")

    # 作成した画像をディスプレイに表示
    lcd.display(img)

    # 5秒間表示を維持
    time.sleep(5)

```

### 6.2. プログラムの実行

ターミナルを開き、保存したファイルを実行します。

```bash
python my_display.py
```

LCDに赤い四角形と "My First App!" という文字が表示されれば成功です。これで、あなただけのLCDアプリケーションを作る第一歩を踏み出しました！

***

### Part 2: English Version

# pi0disp User Guide (for Beginners)

## 1. Introduction

`pi0disp` is a Python library for controlling ST7789V-based LCD displays with a Raspberry Pi. This guide will walk you through every step, from hardware setup to writing your first program, making it easy for anyone without prior coding or Raspberry Pi experience to build their own LCD application.

## 2. Required Hardware

First, let's gather the necessary components for this project.

*   **Raspberry Pi**: Any model like Raspberry Pi 3, 4, Zero, or Zero 2W.
*   **ST7789V LCD Display**: (e.g., Waveshare 1.3inch LCD Hat, Pimoroni Display HAT Mini).
*   **microSD Card**: 16GB or larger is recommended.
*   **Power Supply for Raspberry Pi**.
*   **Peripherals**: (For initial setup) USB Keyboard, Mouse, HDMI Cable, and a Monitor.

## 3. Hardware Setup

Next, connect the LCD display to your Raspberry Pi.

*   **For HATs**: Align the female header of the LCD HAT with the GPIO pins on the Raspberry Pi and press down firmly to connect it.
*   **For Breadboard Modules**: Use jumper wires to connect the pins on the LCD to the corresponding GPIO pins on the Raspberry Pi. You will need to consult the datasheet for your specific LCD to know the correct pinout.

> **Why is this necessary?**
> The Raspberry Pi needs a physical connection to the LCD to send electrical signals that control what is shown on the screen. HATs are recommended for beginners as they are simple to plug in and require no wiring.

## 4. Raspberry Pi Initial Setup and Software Installation

With the hardware ready, it's time to set up the software.

### 4.1. Install Raspberry Pi OS

If you haven't already, install the Raspberry Pi Operating System onto your microSD card using the official "Raspberry Pi Imager" tool. You can find detailed instructions on the [official Raspberry Pi website](https://www.raspberrypi.com/software/).

### 4.2. Enable the SPI Interface

The `pi0disp` library uses the SPI communication protocol to send data to the display at high speed. This is disabled by default and must be enabled.

1.  Click the Raspberry Pi icon in the top-left corner, go to "Preferences" > "Raspberry Pi Configuration".
2.  Navigate to the "Interfaces" tab.
3.  Find "SPI" in the list and select "Enabled".
4.  Click "OK" to save and reboot your Raspberry Pi.

### 4.3. Install Required Libraries

Open a Terminal window and run the following commands one by one to install the software `pi0disp` depends on.

**1. Install `pigpio` C library and daemon**

`pigpio` is a critical library for high-speed GPIO control.

```bash
# Update your system's package list
sudo apt-get update

# Install pigpio
sudo apt-get install pigpio -y

# Enable the pigpio daemon to start automatically on boot
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

**2. Install Python libraries**

Next, install the Python libraries needed for image processing and interfacing with `pigpio`.

```bash
pip install pigpio Pillow numpy
```
> **Why is this necessary?**
> `SPI` is the high-speed communication channel. `pigpio` is the engine that precisely controls the Raspberry Pi's pins. `Pillow` and `numpy` are the tools used to create and manipulate images. By installing these, you give your Python programs the ability to control the LCD.

## 5. Running the Example Code

Let's run a sample program included with the library to verify that everything is set up correctly.

### 5.1. Download the Example Code

First, use the `git` command to download all the `pi0disp` files from GitHub.

```bash
git clone https://github.com/ytani01/pi0disp.git
```

### 5.2. Install the `pi0disp` library**

Finally, install the main library for this project. There are two common ways to do this.

*   **Option A: Install from PyPI **
    This is the easiest method and installs the library directly from the internet.
    ```bash
    pip install pi0disp
    ```

*   **Option B: Install Locally from Source**
    If you have downloaded the source code directly from GitHub (for example, after running the `git clone` command in the next step), you can install it from the local folder.
    ```bash
    # First, navigate into the cloned pi0disp directory
    # cd pi0disp

    # Then, run the following command to install
    pip install .
    ```

### 5.2. Run the Example

Navigate into the downloaded folder and run the example script.

```bash
cd pi0disp/examples
python simple_text.py```

After running this command, your LCD screen should display the text "Hello World!". If it does, your setup is successful!

## 6. Writing Your Own Program

Finally, let's create a simple program from scratch.

### 6.1. Create the Program

Open a code editor like Thonny IDE (which comes pre-installed on Raspberry Pi OS) and type the following code. Save the file as `my_display.py`.

```python
# Import the necessary libraries
from pi0disp import ST7789V
from PIL import Image, ImageDraw, ImageFont
import time

# Initialize the display
with ST7789V() as lcd:
    # Create a new image with a black background
    # lcd.width and lcd.height automatically get the screen size
    img = Image.new("RGB", (lcd.width, lcd.height), "black")

    # Prepare to draw on the image
    draw = ImageDraw.Draw(img)

    # Draw a red rectangle
    # (top-left-x, top-left-y, bottom-right-x, bottom-right-y)
    draw.rectangle((10, 10, 100, 50), fill="red")

    # Draw text in white
    draw.text((10, 70), "My First App!", fill="white")

    # Display the image on the LCD
    lcd.display(img)

    # Keep the display on for 5 seconds
    time.sleep(5)
```

### 6.2. Run the Program

Open a Terminal and run the file you just saved.

```bash
python my_display.py
```

The LCD should now display a red rectangle with the text "My First App!". Congratulations, you've taken the first step toward creating your own custom LCD applications.
