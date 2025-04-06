# Ninja ロボット - Raspberry Pi 音声/テキスト制御

このプロジェクトは、Raspberry Pi Zero W と DFRobot Raspberry Pi IO 拡張HAT を使用して制御される小型ロボットを実装します。主な特徴は以下の通りです。

*   **自然言語制御:** Google Gemini (API経由) を使用して、テキストまたは音声コマンドを解釈します。
*   **ウェブインターフェース:** ローカルWi-Fiネットワーク経由でアクセス可能な、シンプルなFlaskベースのウェブUIを提供します。
*   **音声＆テキスト入力:** テキストコマンドまたはブラウザのマイク（Web Speech APIを使用）を使ってロボットを制御できます。
*   **動作:** 4つのサーボモーターによる基本的な歩行、走行（タイヤモード）、旋回、および個別のサーボ角度制御。
*   **サウンドフィードバック:** ブザーが様々なアクションや状態に対して音声キューを提供します。
*   **障害物回避:** 超音波センサーが前進動作中に近くの物体を検出し、ロボットを停止させます。

## 機能

*   自然言語でロボットの動作（歩行、走行、旋回など）を制御。
*   ロボットのサウンド（挨拶、危険、喜びなど）を制御。
*   個々のサーボ角度を設定。
*   ローカルネットワーク上の任意のデバイスからアクセス可能なウェブベースのユーザーインターフェース。
*   テキスト入力と音声入力（ブラウザのWeb Speech API経由）の両方をサポート。
*   前進歩行/走行中の自動障害物検出と停止。
*   モジュール化されたコード構造（コアロジック、ウェブインターフェース、ハードウェアモジュール）。

## ハードウェア要件

1.  **Raspberry Pi:** Raspberry Pi Zero W 推奨（Wi-Fi内蔵のため）。他のモデルでもWi-Fi/ネットワークアクセスがあれば動作するはずです。
2.  **SDカード:** Raspberry Pi OSがインストールされ、設定済み（Wi-Fi設定を含む）のもの。
3.  **電源:** Raspberry Piと接続されたハードウェアに十分な電力供給ができるもの。
4.  **DFRobot Raspberry Pi IO 拡張HAT:** （または同等のI2C PWMおよびGPIOアクセスを提供するボード）。製品リンク: [https://www.dfrobot.com/product-1 expansion board.html](https://www.dfrobot.com/product-1%20expansion%20board.html) （注意: 実際のリンクは異なる場合があります。確認してください）。
5.  **サーボ:** 4 x 標準 90g サーボ（例: MG90S または同等品）。HAT上のPWMチャンネル0～3に接続。
6.  **超音波センサー:** 1 x HC-SR04 超音波距離センサー。HAT上のGPIOピンに接続。
7.  **アクティブブザー:** 1 x アクティブブザーモジュール。HAT上のGPIOピンに接続。
8.  **ロボットシャーシ/フレーム:** Pi、HAT、サーボ、センサー、ブザーを取り付けるためのもの。
9.  **ジャンパー線:** センサーとブザーをHATに接続するためのもの。

## ソフトウェア要件とインストール

1.  **Raspberry Pi OS:** Piが最新バージョンのRaspberry Pi OS（Legacyまたはそれ以降）で動作していることを確認してください。
2.  **Python 3:** Raspberry Pi OSにプリインストールされているはずです。
3.  **pip:** Pythonパッケージインストーラー。
4.  **必要なPythonライブラリ:** pipを使用してインストールします:
    ```bash
    pip install Flask google-generativeai RPi.GPIO DFRobot_RaspberryPi_Expansion_Board
    ```
    *（注意: `RPi.GPIO`はプリインストールされている場合があります。`DFRobot_...`ライブラリは、HATのドキュメントに従ってダウンロードまたはインストール済みであることを前提としています。）*
5.  **Google Gemini APIキー:** Google AI Studio ([https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)) からAPIキーを取得する必要があります。通常、無料枠でこのプロジェクトには十分です。

## ファイル構造の概要

- ninja_core.py # コアロジック: 初期化、クリーンアップ、Gemini呼び出し、アクション実行
- web_interface.py # Flaskウェブサーバーアプリケーション
- Ninja_Movements_v1.py # サーボ制御関数
- Ninja_Buzzer.py # ブザーサウンド関数と定義
- Ninja_Distance.py # 超音波センサー関数
- DFRobot_RaspberryPi_Expansion_Board.py # DFRobot HATライブラリファイル（または必要に応じてサブディレクトリに配置）
- templates/index.html # ウェブインターフェース用HTMLテンプレート
- README.md # このファイル (日本語版)


## 設定

1.  **Google Gemini APIキー:**
    *   `ninja_core.py` ファイルを開きます。
    *   `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"` という行を見つけます。
    *   `"YOUR_GOOGLE_API_KEY"` を、Google AI Studioから取得した実際のAPIキーに置き換えます。
    *   *（または、キーを削除し、Pi上でGoogle Cloud Application Default Credentials (ADC) を設定することもできますが、このプロジェクトではAPIキーを使用する方が簡単です。）*

2.  **ハードウェアピンとパラメータ（任意）:**
    *   **距離センサーピン:** `Ninja_Distance.py`内で定義されています (`TRIG_PIN = 21`, `ECHO_PIN = 22`)。異なるGPIOピンを使用する場合は変更してください。
    *   **ブザーピン:** `Ninja_Buzzer.py`内で定義されています (`BUZZER_PIN = 23`)。異なるGPIOピンを使用する場合は変更してください。
    *   **障害物しきい値:** `ninja_core.py`内で定義されています (`DISTANCE_THRESHOLD_CM = 5.0`)。ロボットが停止する距離（cm単位）を調整します。
    *   **I2Cアドレス/バス:** HATのアドレス（`0x10`）とI2Cバス（`1`）は `Ninja_Movements_v1.py` の `init_board_and_servo()` 内で設定されています。HATの設定が異なる場合のみ変更してください。

## ハードウェア接続（例）

*   **HAT:** DFRobot拡張HATをRaspberry PiのGPIOヘッダーにしっかりと取り付けます。
*   **サーボ:** 4つのサーボをHAT上の `PWM0` から `PWM3` とラベル付けされたPWMチャンネルに接続します。極性（+、-、信号線）を確認してください。
*   **超音波センサー (HC-SR04):**
    *   `VCC` -> HAT `5V` ピン
    *   `GND` -> HAT `GND` ピン
    *   `Trig` -> HAT上のBCM `21` に対応するGPIOピン（HATのピン配置図を確認）
    *   `Echo` -> HAT上のBCM `22` に対応するGPIOピン（HATのピン配置図を確認）
*   **アクティブブザー:**
    *   `VCC` または `+` -> HAT `3.3V` または `5V` ピン（ブザーの要件を確認）
    *   `GND` または `-` -> HAT `GND` ピン
    *   `I/O` または `Signal` -> HAT上のBCM `23` に対応するGPIOピン（HATのピン配置図を確認）

*   **HATのラベルとBCM番号の正確なマッピングについては、DFRobot拡張HATのドキュメントを参照してください。**

## ロボットの実行

1.  **Piへの接続:** Raspberry Piの電源がオンで、ローカルWi-Fiネットワークに接続されていることを確認します。SSH経由で接続するか、Piに直接ターミナルを使用します。
2.  **コードディレクトリへの移動:** ターミナルを開き、すべてのプロジェクトファイルを保存したディレクトリに移動します。
    ```bash
    cd /path/to/your/robot/code
    ```
3.  **ウェブインターフェースの実行:** Flaskアプリケーションスクリプトを実行します。
    ```bash
    python web_interface.py
    ```
4.  **IPアドレスの確認:** スクリプトはPiのIPアドレスを表示しようとします。次のような行を探してください:
    ```
    *** Your Pi's Likely IP Address: 192.168.1.XXX ***
    *** Open http://192.168.1.XXX:5000 in your browser ***
    ```
    検出に失敗した場合は、別のターミナルウィンドウで `hostname -I` を実行してIPアドレスを手動で確認します。

## ウェブインターフェースの使用

1.  **ブラウザを開く:** Raspberry Piと同じWi-Fiネットワークに接続されている別のデバイス（PC、タブレット、スマートフォン）でブラウザを開きます。
2.  **アクセス:** ウェブブラウザ（Web Speech APIのサポートが最も良いChromeまたはEdgeを推奨）を開き、アドレスバーに `http://<YOUR_PI_IP_ADDRESS>:5000` と入力します（`<YOUR_PI_IP_ADDRESS>` は前のステップで確認したアドレスに置き換えます）。
3.  **インターフェース:**
    *   **テキストコマンド:** テキストボックスにコマンド（例: "walk forward", "say hello", "turn right", "stop"）を入力し、「Send Text」をクリックします。
    *   **音声コマンド:**
        *   「Record Command」ボタンをクリックします。初回はブラウザがマイクの使用許可を求める場合がありますので、許可してください。
        *   コマンドをはっきりと話します。
        *   録音を停止するには、もう一度ボタン（「Listening...」と表示されている）をクリックします。
        *   ブラウザが音声を文字に変換し（Web Speech APIを使用）、そのテキストをロボットに送信します。
    *   **STOPボタン:** 赤い「STOP ROBOT」ボタンをクリックすると、即時停止コマンドが送信されます。
    *   **ステータスエリア:** ページに表示されるステータスメッセージ、最後のコマンド、AIの解釈を確認します。

## カスタマイズ

*   **サーボ角度:** `ninja_core.py` 内の `reset_servos`（起立姿勢）と `rest`（休憩姿勢）のデフォルト角度を、実際のロボットの構造に合わせて調整します。`Ninja_Movements_v1.py` 内の動作関数（`walk`、`run` など）の角度を微調整します。
*   **サウンド:** `Ninja_Buzzer.py` 内のサウンドシーケンスを変更または追加します。新しい音符の周波数を定義したり、`SOUND_MAP` を変更したりします。新しいサウンドキーワードを追加した場合は、`ninja_core.py` 内のGeminiプロンプトも更新することを忘れないでください。
*   **Geminiプロンプト:** `ninja_core.py` 内の `get_gemini_interpretation` 関数内の `prompt` 文字列を編集して、Geminiがコマンドを解釈する方法を変更したり、新しい機能に関する情報を追加したりします。
*   **動作ロジック:** `Ninja_Movements_v1.py` 内のステップシーケンスやタイミングを変更して、ロボットの歩き方、曲がり方、走り方を変更します。

## トラブルシューティング / 重要事項

*   **マイクアクセス (HTTPS):** ブラウザは、IPアドレス（`localhost`以外）経由でサイトにアクセスする場合、マイクへのアクセスを許可するために安全な接続（HTTPS）を要求することがよくあります。音声入力が機能しない場合:
    *   ネットワークがmDNS/Bonjourをサポートしている場合は、`http://<PI_HOSTNAME>.local:5000` でアクセスしてみてください。
    *   *テスト目的のみ:* ブラウザのフラグを使用して安全でないオリジンを許可します（例: Chromeの `chrome://flags/#unsafely-treat-insecure-origin-as-secure` – **これは安全ではありません**）。
    *   適切な解決策は、FlaskでHTTPSを設定することですが、より複雑です（例: 証明書を使用して `app.run` で `ssl_context` を使う、またはNginxのようなリバースプロキシを使用する）。
*   **ネットワーク:** Piと制御デバイスが*同じ*Wi-Fiネットワーク上にあることを確認してください。ファイアウォールがポート5000へのアクセスをブロックしている可能性があります。
*   **パフォーマンス:** Raspberry Pi Zeroはそれほど強力ではありません。複雑なGeminiとのやり取りや素早いコマンド入力は遅く感じるかもしれません。
*   **APIコスト:** Google Geminiには寛大な無料枠がありますが、使用量が非常に多くなった場合の潜在的なコストに注意してください。Googleの料金を確認してください。
*   **デバッグ:** Raspberry PiのFlaskターミナルウィンドウの出力を確認して、詳細なログやエラーメッセージを確認します。ブラウザの開発者コンソール（通常F12）を使用して、Web Speech APIや`fetch`呼び出しに関連するJavaScriptエラーやネットワークの問題を確認します。
*   **電源:** 電源供給がPi、HAT、および**4つすべてのサーボが同時に動く**ことを処理できることを確認してください（特に複雑な動作や起動時）。電力不足は不安定さや再起動を引き起こす可能性があります。
