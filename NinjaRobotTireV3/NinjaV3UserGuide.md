# `piservo0` & `pi0disp` ユーザーガイド

## はじめに

ようこそ！このガイドは、Raspberry Piを使ってロボットや電子工作を始めたいあなたのための手引書です。

- **`piservo0`**: サーボモーターを精密に動かすためのライブラリ
- **`pi0disp`**: 小型ディスプレイに文字や画像を表示するためのライブラリ

これら2つのライブラリと、最新のPython開発ツール`uv`を使い、自分だけのロボット制御プログラムをゼロから作成する方法を、プログラミング経験がない方でも理解できるように、一歩一歩丁寧に解説します。

### 準備するもの

- **ハードウェア**:
    - Raspberry Pi (Pi 4, Pi 5, または Pi Zero 2 W推奨)
    - サーボモーター (SG90など)
    - ST7789Vチップを搭載したSPI接続の小型ディスプレイ
    - ジャンパーワイヤー

- **ソフトウェア**:
    - Raspberry Pi OS (インストール済みであること)
    - インターネット接続

---

## 第1章: 開発環境のセットアップ

まず、プログラムを作成し、ライブラリを動かすための「開発環境」を整えます。

### 1.1. `pigpio`のインストールと有効化

`pigpio`は、Raspberry PiのGPIOピン（電子部品を接続するピン）を安全かつ簡単に制御するための重要なソフトウェアです。

1.  **ターミナルを開く**: Raspberry Piのデスクトップ左上にある黒い画面のアイコンをクリックします。

2.  **`pigpio`をインストール**: 以下の2つのコマンドを1行ずつ入力し、それぞれ`Enter`キーを押します。
    ```bash
    sudo apt update
    sudo apt install pigpio
    ```

3.  **`pigpio`を起動し、自動起動を設定**: 同様に、以下の2つのコマンドを実行します。これにより、Raspberry Piが起動するたびに`pigpio`が自動で実行されるようになります。
    ```bash
    sudo systemctl start pigpiod
    sudo systemctl enable pigpiod
    ```

### 1.2. `uv`のインストール

`uv`は、Pythonのライブラリ（便利なプログラムの部品集）をインストールしたり管理したりするための、非常に高速なツールです。

1.  **ターミナルで以下のコマンドを実行**:
    ```bash
    curl -L -s https://astral.sh/uv/install.sh | sh
    ```
    これにより、`uv`がシステムにインストールされます。

### 1.3. プロジェクトの準備と仮想環境の作成

次に、あなたのプロジェクト専用の作業フォルダと、ライブラリを管理するための「仮想環境」を作成します。

1.  **プロジェクト用フォルダを作成**:
    ```bash
    mkdir my_robot
    cd my_robot
    ```
    `my_robot`という名前のフォルダが作成され、その中に移動します。

2.  **仮想環境の作成**:
    ```bash
    uv venv
    ```
    このコマンドを実行すると、現在のフォルダ（`my_robot`）内に`.venv`という名前の特別なフォルダが作成されます。これが仮想環境です。これにより、このプロジェクトで使うライブラリが他のプロジェクトと混ざってしまうのを防ぎます。

---

## 第2章: `piservo0`でサーボモーターを動かす

いよいよサーボモーターを制御します。

### 2.1. `piservo0`のインストール

`uv`を使って`piservo0`ライブラリをインストールします。

```bash
uv pip install piservo0
```

### 2.2. サーボのキャリブレーション（調整）

サーボモーターは個体差があり、同じ指示でも少しずつ動きが違うことがあります。そのため、最初に「キャリブレーション（調整）」を行い、正確な動きを教え込みます。

1.  **配線**: サーボモーターをRaspberry Piに接続します。
    - **茶色/黒**: GND（6番ピンなど）
    - **赤**: 5V（2番ピンなど）
    - **オレンジ/黄**: GPIOピン（例: 17番ピン）

2.  **キャリブレーションツールを起動**:
    サーボをGPIO 17番ピンに接続した場合、以下のコマンドを実行します。
    ```bash
    uv run piservo0 calib 17
    ```

3.  **対話的に調整**:
    - `h`キーを押すとヘルプが表示されます。
    - `w`キーと`s`キーでサーボが動きます。
    - `Tab`キーで調整する角度（-90度, 0度, 90度）を切り替えます。
    - それぞれの角度で、サーボが真横、正面、反対側の真横を向くように`w`/`s`で微調整し、位置が決まったら`Enter`キーを押して保存します。
    - `q`キーで終了します。

    この調整データは、プロジェクトフォルダ内に`servo.json`というファイル名で保存されます。

### 2.3. 初めてのサーボ制御スクリプト

1.  **ファイルを作成**: `control_servo.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo

    # --- 設定 ---
    SERVO_PIN = 17  # サーボを接続したGPIOピン番号

    # --- 初期化 ---
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioに接続できません。デーモンが実行されているか確認してください。")
        exit()

    # キャリブレーション済みのサーボとして初期化
    servo = CalibrableServo(pi, SERVO_PIN)
    print(f"GPIO {SERVO_PIN} のサーボを初期化しました。")

    try:
        # --- サーボを動かす ---
        print("中央 (0度) に移動します。")
        servo.move_angle(0)
        time.sleep(2)  # 2秒待つ

        print("最小角度 (-90度) に移動します。")
        servo.move_angle(-90)
        time.sleep(2)

        print("最大角度 (90度) に移動します。")
        servo.move_angle(90)
        time.sleep(2)

    except KeyboardInterrupt:
        print("
プログラムを終了します。")

    finally:
        # --- 終了処理 ---
        print("サーボをオフにします。")
        servo.off()
        pi.stop()
    ```

2.  **スクリプトを実行**:
    ```bash
    uv run python control_servo.py
    ```
    サーボが中央→片側→反対側へと順番に動けば成功です！

---

## 第3章: `pi0disp`でディスプレイに表示する

次に、ディスプレイに図形や文字を表示させます。

### 3.1. `pi0disp`のインストール

`uv`を使って`pi0disp`ライブラリをインストールします。`Pillow`という画像処理ライブラリも一緒にインストールされます。

```bash
uv pip install pi0disp Pillow
```

### 3.2. 初めてのディスプレイ表示スクリプト

1.  **配線**: ディスプレイのピンをRaspberry Piの対応するGPIOピンに接続します。（ディスプレイ製品の仕様書を確認してください）

2.  **ファイルを作成**: `show_on_display.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    from pi0disp import ST7789V
    from PIL import Image, ImageDraw

    print("ディスプレイを初期化します。")

    # 'with'構文を使うと、プログラム終了時に自動で後片付けをしてくれる
    with ST7789V() as lcd:
        # PILを使って画像を作成
        # lcd.width, lcd.height でディスプレイのサイズが取得できる
        image = Image.new("RGB", (lcd.width, lcd.height), "black")
        draw = ImageDraw.Draw(image)

        # 青い円を描画
        print("円を描画します。")
        draw.ellipse(
            (10, 10, lcd.width - 10, lcd.height - 10),
            fill="blue",
            outline="white"
        )

        # テキストを描画
        print("テキストを描画します。")
        draw.text((60, 150), "Hello, Robot!", fill="white")

        # 作成した画像（円とテキスト）をディスプレイに表示
        print("ディスプレイに表示します。")
        lcd.display(image)

    print("完了しました。")
    ```

3.  **スクリプトを実行**:
    ```bash
    uv run python show_on_display.py
    ```
    ディスプレイに黒い背景、青い円、そして"Hello, Robot!"という文字が表示されれば成功です。

---

## 第4章: すべてを組み合わせる

最後に、サーボの動きとディスプレイの表示を連動させたプログラムを作成します。

### 4.1. 目標

サーボモーターを-90度から+90度まで滑らかに動かし、現在の角度をリアルタイムでディスプレイに表示します。

### 4.2. 最終的なスクリプト

1.  **ファイルを作成**: `robot_control.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo
    from pi0disp import ST7789V, draw_text
    from PIL import Image, ImageDraw, ImageFont

    # --- 設定 ---
    SERVO_PIN = 17

    # --- 初期化 ---
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioに接続できません。")
        exit()

    servo = CalibrableServo(pi, SERVO_PIN)

    # 'with'構文でディスプレイを初期化
    with ST7789V() as lcd:
        print("サーボとディスプレイの連携を開始します。Ctrl+Cで終了します。")

        try:
            # -90度から90度まで5度ずつ動かす
            for angle in range(-90, 91, 5):
                # 1. サーボを動かす
                servo.move_angle(angle)

                # 2. 表示する画像を作成
                #    毎回新しい黒い画像を作成して、前の描画を消す
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)

                # 3. 現在の角度をテキストとして描画
                text = f"Angle: {angle}"
                
                # テキストを中央に大きく表示
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))

                # 4. ディスプレイに表示
                lcd.display(image)

                # 5. 少し待つ
                time.sleep(0.05)

            # 逆方向に動かす
            for angle in range(90, -91, -5):
                servo.move_angle(angle)
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)
                text = f"Angle: {angle}"
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))
                lcd.display(image)
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("
プログラムを終了します。")

        finally:
            # --- 終了処理 ---
            servo.off()
            pi.stop()
            print("サーボとディスプレイをオフにしました。")

    ```

### 4.3. 実行

```bash
uv run python robot_control.py
```

サーボがゆっくりと左右に往復し、その動きに合わせてディスプレイの角度表示がリアルタイムに更新されるはずです。

## まとめ

おめでとうございます！あなたは`piservo0`と`pi0disp`を使って、サーボモーターとディスプレイを連動させる基本的なプログラムを自力で作成することができました。

ここからが本当のスタートです。このガイドで学んだことを応用して、

-   複数のサーボを動かしてロボットアームを制御する
-   センサーの値に応じてサーボの動きやディスプレイ表示を変える
-   ボタン操作でロボットをコントロールする

など、あなたのアイデアを形にしていきましょう！

さらに詳しい情報や高度な使い方については、各ライブラリの`README.md`や`samples`フォルダの中のサンプルコードを参考にしてください。
