# Part 1: Japanese version

## 対話型エージェントプレイブック：Google ADKによる音声とストリーミングのガイド

### 第1章：対話型エージェントの基礎

人工知能の最前線へようこそ。ここでは、単純な質疑応答ボットを超え、真に対話的で自律的なAIエージェントを作成します。このガイドは、技術愛好家、好奇心旺盛な実験家、そして市民開発者など、プログラミングの正式なバックグラウンドがなくても洗練されたAIシステムを構築したいと願うすべての人を対象としています。私たちは、複雑なAIシステムの作成を簡素化する強力なオープンソースフレームワークであるGoogleのAgent Development Kit (ADK) を使用し、実践的でハンズオンな旅に出ます。¹ このプレイブックを終える頃には、あなたの命令を理解するだけでなく、リアルタイムで応答し、デジタルの指示と物理的な行動の間のギャップを埋める、3つの異なる音声制御エージェントを構築していることでしょう。

#### 1.1 AIエージェントとは？単純なボットから自律的な思考者へ

その核心において、AIエージェントとは、あなたに代わって特定の目標を達成するために行動するように設計されたソフトウェアプログラムです。⁴ これは従来のチャットボットからの大きな飛躍です。チャットボットがスクリプトに基づいて質問に答えるのに対し、AIエージェントは環境を認識し、意思決定を行い、複数のステップからなるタスクを完了するための行動を起こすことができます。⁶
この概念をより具体的にするために、AIエージェントを人間のように3つの基本コンポーネントで考えると役立ちます ⁹：

*   **脳（意思決定）：** これは、通常、GoogleのGeminiのような大規模言語モデル（LLM）によって駆動される、中核となる推論エンジンです。¹² LLMにより、エージェントは自然言語を理解し、複雑な要求をより小さなステップに分解し、行動計画を策定することができます。⁶ これはエージェントの「思考」する部分です。
*   **感覚（知覚）：** エージェントは、環境とユーザーの要求を理解するために情報を収集する必要があります。これらの「感覚」は、ユーザーのテキスト入力、音声コマンド、データベースからの情報、またはWeb APIからのリアルタイムデータなど、さまざまなソースからのデータであり得ます。⁸
*   **手（行動とツール）：** エージェントが計画を立てたら、それを実行する方法が必要です。ここで「ツール」が登場します。ツールはエージェントの能力、つまり世界と対話するための「手」です。² ツールは、ウェブを検索する関数から、データベースをクエリする関数、メールを送信する関数、さらには物理的なデバイスを制御する関数まで、何でもあり得ます。¹⁴

GoogleのAgent Development Kit (ADK) のようなフレームワークは、これらのコンポーネントを組み立てるための構造化された、コードファーストの環境を提供します。ADKをAI向けのハイテクな組み立てキットと考えてください。それは、設計図（`Agent`クラス）、既製の部品（組み込みツール）、そして組み立て説明書（オーケストレーションロジック）を提供し、それらがどのように接続されるかという低レベルのエンジニアリングに悩まされることなく、エージェントに何をさせたいかに集中できるようにします。¹ このアプローチにより、エージェント開発は現代のソフトウェア開発のようになり、この分野に新しい人々にもアクセスしやすくなります。

#### 1.2 対話の魔法 パート1：エージェントがリアルタイムで「話す」仕組み

現代のAIエージェントの最も魅力的な特徴の一つは、気まずい間を置かずに流暢にコミュニケーションする能力です。このリアルタイムのフィードバックは、単なる見た目の改善ではありません。それは、エージェントの応答性と知性に対するユーザーの認識を根本的に変えます。この能力は、サーバー送信イベント（Server-Sent Events, SSE） と呼ばれるウェブ技術によって支えられています。²¹

ライブのニュース放送を見ていると想像してください。更新があるかどうかを確認するために数秒ごとに画面をリフレッシュする必要はありません。新しい情報（画面下部のニュースティッカーや速報バナー）は、発生すると同時に画面に「プッシュ」されます。これがSSEの基本原則です。それは、サーバー（エージェントが存在する場所）からブラウザ（クライアント）への持続的な一方向の通信チャネルを確立します。²²

`adk web`コマンドを実行すると、特別なエンドポイント`/run_sse`を含むローカルウェブサーバーが起動します。²⁵ ブラウザのADKウェブインターフェースがこのエンドポイントに接続すると、それはまるでそのライブ放送にチャンネルを合わせるようなものです。エージェントは、思考プロセス全体が完了するまで待ってから応答を送信するわけではありません。代わりに、LLMがトークンごと（単語ごと）に応答を生成するにつれて、ADKサーバーは各部分をこの開かれたチャネルを通じて即座に送信します。²⁸

ユーザーにとっての結果は、おなじみの「ライブタイピング」効果です。エージェントの応答が、まるでリアルタイムでタイプされているかのように画面に表示されます。これにより、知覚される遅延が劇的に減少します。完全な回答を生成するのに合計で数秒かかったとしても、ユーザーはほぼ瞬時に応答が形成され始めるのを見るため、対話がより速く、より自然で、より魅力的に感じられます。²⁸ このストリーミングアーキテクチャは、私たちが構築する対話型エージェントの基盤です。

#### 1.3 対話の魔法 パート2：エージェントがあなたの声を「聞く」仕組み

自然な会話のもう半分は、もちろん聞くことです。ADKウェブインターフェースは、音声を使ってエージェントとシームレスに対話する方法を提供し、これは現代のウェブブラウザに直接組み込まれた強力な技術、Web Speech API を活用することで実現されます。²⁹

音声からテキストへの変換の「魔法」がどこで起こるかを理解することが不可欠です。最初にあなたの声を処理するのは、ADKエージェントやサーバーではありません。代わりに、ブラウザ自体がこのタスクを処理します。ADKウェブUIのマイクアイコンをクリックすると、ブラウザにマイクへのアクセス許可を与えることになります。³¹ このアクションにより、Web Speech APIの`SpeechRecognition`インターフェースが有効になります。²⁹

データフローはシンプルでありながらエレガントです：

1.  **あなたが話す：** 「パリの天気は？」のような口頭でのコマンドを発します。
2.  **ブラウザが聞く：** ブラウザでローカルに実行されているWeb Speech APIが、マイクからの音声をキャプチャします。
3.  **ブラウザが文字起こしする：** ブラウザはこの音声をサーバーベースの認識エンジン（GoogleアシスタントやSiriのようなサービスを動かしているものと同じことが多い）に送信し、テキストの文字起こしを返してもらいます。²⁹
4.  **テキストが送信される：** 結果として得られたテキスト文字列「パリの天気は？」は、ADKウェブUIの入力ボックスに配置され、手動でタイプした場合とまったく同じようにADKサーバーに送信されます。

このアーキテクチャ設計は、大きな利点をもたらします。私たちがPythonで書くAIエージェントの中核ロジックは、入力方法から完全に独立しています。エージェントはテキストを受け取って処理するように設計されています。そのテキストがキーボードから来たのか、マイクから来たのか、あるいは別の自動化システムから来たのかを知る必要も気にする必要もありません。この関心の分離—ブラウザに音声処理の複雑さを任せ、エージェントに推論と行動のロジックを任せること—は、音声対応アプリケーションの構築を驚くほど簡単にする強力な原則です。これにより、私たちエージェントビルダーは、インターフェースが話し言葉から書き言葉への翻訳を優雅に処理できると確信しながら、エージェントの能力と知性の定義に完全に集中することができます。

#### 1.4 我々の頭脳：音声最適化モデルの選択

最も自然で応答性の高い音声対話を作成するためには、この目的のために特別に設計されたモデルを使用する必要があります。多くのモデルはテキストを処理できますが、音声会話をリアルに感じさせる低遅延の双方向通信に最適化されているモデルは限られています。これらのモデルは、「Live API」として知られるものをサポートしています。³³

このガイドのすべてのプロジェクトで、私たちは**gemini-live-2.5-flash-preview**モデルを使用します。このモデルはGeminiファミリーの一部ですが、音声、ビデオ、またはテキストのリアルタイムストリームを処理し、即座に人間らしい話し言葉の応答を提供するために特別に設計されています。³⁴ このモデルを使用することで、私たちのエージェントは音声コマンドを理解するだけでなく、ほぼ瞬時に応答を開始でき、真に流動的で対話的な会話体験を実現できます。

#### 1.5 私たちの目標：真に対話的なエージェントの構築

リアルタイムのストリーミング出力（SSE）とブラウザベースの音声入力（Web Speech API）、そして音声に最適化されたLLMを組み合わせることで、私たちはエージェントを単純なコマンドラインツールから、ダイナミックで会話型のパートナーへと昇華させることができます。以下の表は、これらの技術が可能にするユーザーエクスペリエンスの大きな飛躍を示しており、これがこのプレイブックの中心的な目標です。

**表1：標準エージェントから対話型エージェントへ**

| 機能 | 標準的なエージェントとの対話 | 強化された対話型エージェント（私たちの目標） | 主な利点 |
| :--- | :--- | :--- | :--- |
| **入力方法** | テキストのみ。コマンドのタイピングが必要。 | 音声起動。ユーザーは自然にコマンドを話す。 | **アクセシビリティと速度：** 参入障壁を下げ、より速くハンズフリーな対話を可能にする。 |
| **応答の配信** | 「ブロッキング」。ユーザーは完全な応答が生成されるまで待つ必要がある。 | 「ストリーミング」。エージェントの応答がリアルタイムでトークンごとに表示される。 | **知覚される遅延の削減：** エージェントがより応答性が高く「生きている」ように感じられ、ユーザーエンゲージメントが向上する。 |
| **フィードバックループ** | 不透明。ユーザーは中間ステップを理解せずに最終結果のみを見る。 | 透明。UIは、ツール呼び出しとその結果を含むエージェントの「思考プロセス」をリアルタイムで表示できる。 | **信頼と理解：** エージェントの推論を解明し、ユーザーがどのようにして答えにたどり着いたかを見ることができる。 |
| **モダリティ** | ユニモーダル（テキスト入力、テキスト出力）。 | マルチモーダル（音声入力、テキスト/音声出力）。 | **自然な対話：** より直感的で多用途な、人間らしい会話体験を創出する。 |

この基礎的な理解をもって、私たちは開発環境をセットアップし、最初の対話型エージェントの構築を始める準備ができました。

### 第2章：ADK開発環境：恐れることのないセットアップガイド

構築を始める前に、作業場が必要です。このセクションでは、エージェント開発のためにコンピュータを準備するための、綿密でステップバイステップのガイドを提供します。これらの指示に注意深く従うことで、クリーンで隔離された機能的な環境が作成され、一般的な問題を回避し、スムーズな旅路を保証します。目標は、セットアップの摩擦をなくし、エージェント構築の創造的なプロセスに集中できるようにすることです。

#### 2.1 必須ツール：PythonとVisual Studio Code

私たちのエージェントは、AI開発の標準である強力で読みやすいプログラミング言語、Pythonで書かれます。私たちは、すべての主要なオペレーティングシステムで動作する、無料で非常に多機能なコードエディタであるVisual Studio Code（VS Code）を使用します。

*   **Pythonのインストール：** Agent Development KitはPythonバージョン3.9以上を必要とします。² Pythonがインストールされていない、または古いバージョンをお持ちの場合は、公式Pythonウェブサイト[python.org](https://python.org)にアクセスしてください。お使いのオペレーティングシステム（Windows、macOS、またはLinux）用のインストーラーをダウンロードし、インストール手順に従ってください。重要なこととして、Windowsでは、インストールプロセス中に「Add Python to PATH」というボックスにチェックを入れてください。
*   **Visual Studio Codeのインストール：** VS Codeは、エージェントのコードを書いたり編集したりするための主要なツールになります。構文のハイライトや統合ターミナルなどの便利な機能を提供します。公式サイト[code.visualstudio.com](https://code.visualstudio.com)から無料でダウンロードしてください。

#### 2.2 「サンドボックス」の作成：仮想環境の力

Pythonプロジェクトで作業する際には、「仮想環境」を使用することが非常に重要なベストプラクティスです。各プロジェクトごとにクリーンでプライベートなサンドボックスまたはワークスペースを作成するものと考えてください。² このサンドボックスには、独自のPythonのコピーと独自のインストール済みライブラリのセットが含まれており、あるプロジェクトのツールが別のプロジェクトのツールと干渉しないようにします。

サンドボックスを作成し、有効化しましょう。新しいターミナルまたはコマンドプロンプトを開いて進めてください。Windowsでは、「コマンドプロンプト」または「PowerShell」を検索できます。macOSでは、「ユーティリティ」フォルダに「ターミナル」アプリがあります。

1.  **プロジェクトフォルダの作成：** まず、すべてのエージェントプロジェクトを格納するメインフォルダを作成します。
        ```bash
        mkdir my_interactive_agents
        cd my_interactive_agents
        ```

2.  **仮想環境の作成：** この新しいフォルダ内で、次のコマンドを実行します。これにより、サンドボックスを含む`.venv`という名前のサブフォルダが作成されます。
        ```bash
        python -m venv .venv
        ```

3.  **仮想環境の有効化：** サンドボックスの使用を開始するには、それを「有効化」する必要があります。コマンドはオペレーティングシステムによって若干異なります。³¹
        *   **macOSまたはLinuxの場合：**
                ```bash
                source .venv/bin/activate
                ```
        *   **Windows（コマンドプロンプト使用）の場合：**
                ```cmd
                .venv\Scripts\activate
                ```
        *   **Windows（PowerShell使用）の場合：**
                ```powershell
                .venv\Scripts\Activate.ps1
                ```
        仮想環境が有効になると、コマンドプロンプトの前に`(.venv)`が表示されるようになります。このプロジェクトで作業するために新しいターミナルを開くたびに、この有効化ステップを実行する必要があります。

#### 2.3 エージェント構築キットのインストール

仮想環境が有効になったので、Google ADKライブラリとAPI呼び出しに必要な`requests`ライブラリをインストールできます。
ターミナルで次のコマンドを実行してください：

```bash
pip install google-adk requests
```

このインストールプロセスには1〜2分かかることがあります。完了すると、有効化された環境内で`adk`コマンドラインツールが利用可能になります。³⁹

#### 2.4 王国への鍵：APIキーの取得

私たちのエージェントの「頭脳」であるGemini LLMは、Googleが提供する強力なクラウドサービスです。このサービスにアクセスするために、エージェントはAPIキー、つまりリクエストを認証するユニークなパスワードが必要です。最初のプロジェクトでは、3つのキーが必要になります。

*   **Google APIキー（エージェントの頭脳用）：**
        1.  Google AI Studioに移動します：[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)。³
        2.  Googleアカウントでサインインします。
        3.  「新しいプロジェクトでAPIキーを作成」をクリックします。
        4.  生成されたキーをコピーし、安全な場所に保管してください。
*   **OpenWeatherMap APIキー（天気データ用）：**
        1.  [openweathermap.org](https://openweathermap.org)にアクセスし、無料アカウントを作成します。⁴⁰
        2.  サインイン後、アカウントページに移動し、「APIキー」タブを見つけます。
        3.  デフォルトのAPIキーをコピーします。このキーが有効になるまで数分かかる場合があることに注意してください。
*   **API-Ninjas APIキー（ジオコーディング用）：**
        1.  [api-ninjas.com](https://api-ninjas.com)にアクセスし、無料アカウントを登録します。
        2.  サインイン後、APIキーがアカウントページに表示されます。
        3.  このキーをコピーします。無料枠は寛大で、私たちのプロジェクトに最適です。

#### 2.5 最初のAIエージェントプロジェクトの構造化

ADKは、プロジェクトが特定のフォルダ構造に従うことを期待しています。この慣習により、フレームワークはエージェントを自動的に発見し、実行することができます。最初のプロジェクトである天気予報エージェントの構造を作成しましょう。³⁷
ターミナルで、仮想環境が有効になっている`my_interactive_agents`ディレクトリ内にいることを確認してください。次のコマンドを実行します：

```bash
mkdir weather_agent
touch weather_agent/__init__.py
touch weather_agent/agent.py
touch weather_agent/.env
```

これにより、エージェント用の新しいフォルダと、その中に3つの空のファイルが作成されます。各ファイルの目的を説明します：

*   `weather_agent/`: これは天気エージェント用の自己完結型の「モジュール」です。さらにエージェントを構築する際には、それぞれに同様のフォルダを作成します。
*   `__init__.py`: これは特別な、しばしば空のPythonファイルで、Pythonに`weather_agent`フォルダをパッケージ、つまりインポート可能なコードのコレクションとして扱うように指示します。このファイルには1行追加します。
*   `agent.py`: これはエージェントの実際のロジック、つまりツールと「頭脳」を記述するメインファイルです。
*   `.env`: これは環境変数、最も重要なのは秘密のAPIキーを保存するために使用される特別なファイルです。ADKフレームワークは、このファイルを自動的に読み取るように設計されており、秘密をメインコードから分離して保管します。

#### 2.6 APIキーの設定

最後のセットアップステップは、Google ADKが見つけられる場所にAPIキーを安全に保存することです。

1.  **VS Codeでプロジェクトを開く：** ターミナルで、`my_interactive_agents`ディレクトリから`code .`と入力してEnterキーを押します。これにより、プロジェクトフォルダ全体がVisual Studio Codeで開きます。
2.  **.envファイルを編集する：** VS Codeの左側にあるファイルエクスプローラーで、`weather_agent`フォルダに移動し、`.env`ファイルをクリックして開きます。
3.  **キーを追加する：** 以下の行をファイルに貼り付けます ³⁶：
        ```
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY="PASTE_YOUR_GOOGLE_API_KEY_HERE"
        OPENWEATHER_API_KEY="PASTE_YOUR_OPENWEATHER_API_KEY_HERE"
        API_NINJAS_KEY="PASTE_YOUR_API_NINJAS_KEY_HERE"
        ```
4.  **プレースホルダーを置き換える：** プレースホルダーテキストを、取得した実際のAPIキーに置き換えてください。引用符は必ず保持してください。
5.  **__init__.pyファイルを編集する：** `__init__.py`ファイルを開き、次の行を追加します。これにより、ADKはこのパッケージからエージェントをロードする方法を知ることができます。³¹
        ```python
        from . import agent
        ```
6.  **両方のファイルを保存する：** 両方のファイルへの変更を保存します。

これで開発環境の構成は完了です。APIキーを安全に保管する場所、構造化されたプロジェクトフォルダ、そして必要なすべてのソフトウェアがインストールされました。最初のAIエージェントを構築する準備が整いました。

### 第3章：プロジェクト1：音声対応ストリーミング天気予報エージェント

最初のプロジェクトは、ライブのリアルタイムデータを使用する会話型の天気エージェントです。これを実現するために、2段階のワークフローを構築します。まず、エージェントがジオコーディングツールを使用して都市名を地理座標（緯度と経度）に変換します。次に、別のエージェントがそれらの座標を取得し、天気ツールを使用して現在の状況を取得します。このマルチツール、マルチエージェントのアプローチは、複雑な問題を解決するための強力なパターンです。

#### 3.1 エージェントにスキルを与える：ジオコーディングと天気ツール

2つのツールを定義します。1つ目の`get_coordinates`は、API-Ninjasサービスを使用して都市の位置を検索します。2つ目の`get_weather`は、OpenWeatherMap APIを使用してその場所の予報を取得します。⁴⁰
VS Codeで`weather_agent/agent.py`ファイルを開き、次のPythonコードを追加します：

```python
# weather_agent/agent.py内
import os
import requests

# --- ツール1：ジオコーディング（都市 -> 座標） ---
def get_coordinates(city: str) -> dict:
        """
        都市名をその地理的な緯度と経度に変換します。

        Args:
                city (str): 都市名（例：「ニューヨーク」や「ロンドン」）。

        Returns:
                dict: 成功時には'latitude'と'longitude'を含む辞書、
                          失敗時には'error_message'を含む辞書。
        """
        print(f"--- ツール実行：get_coordinates(city='{city}') ---")
        api_key = os.getenv("API_NINJAS_KEY")
        if not api_key:
                return {"status": "error", "error_message": "API-Ninjasキーが見つかりません。"}

        api_url = f'https://api.api-ninjas.com/v1/geocoding?city={city}'
        try:
                response = requests.get(api_url, headers={'X-Api-Key': api_key})
                response.raise_for_status()
                data = response.json()
                if data and isinstance(data, list):
                        return {
                                "status": "success",
                                "latitude": data[0]['latitude'],
                                "longitude": data[0]['longitude']
                        }
                else:
                        return {"status": "error", "error_message": f"{city}の座標が見つかりませんでした。"}
        except requests.exceptions.RequestException as e:
                return {"status": "error", "error_message": f"APIリクエストに失敗しました：{e}"}

# --- ツール2：天気（座標 -> 予報） ---
def get_weather(lat: float, lon: float) -> dict:
        """
        指定された緯度と経度の現在の天気予報を取得します。

        Args:
                lat (float): 場所の緯度。
                lon (float): 場所の経度。

        Returns:
                dict: 天気予報またはエラーメッセージを含む辞書。
        """
        print(f"--- ツール実行：get_weather(lat={lat}, lon={lon}) ---")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
                return {"status": "error", "error_message": "OpenWeatherMap APIキーが見つかりません。"}

        api_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                report = (
                        f"天気は{data['weather'][0]['description']}、気温は"
                        f"{data['main']['temp']}℃、湿度は{data['main']['humidity']}%です。"
                )
                return {"status": "success", "report": report}
        except requests.exceptions.RequestException as e:
                return {"status": "error", "error_message": f"APIリクエストに失敗しました：{e}"}
```

各関数の明確で説明的なdocstringに注目してください。これらはLLMが各ツールの機能と正しい使用方法を理解するために不可欠です。⁴²

#### 3.2 エージェントの頭脳（複数）を構築する

2段階のプロセスがあるため、`SequentialAgent`によって管理される2つのエージェントからなる組み立てラインを作成します。

*   **ジオコーダーエージェント：** このエージェントの唯一の仕事は、`get_coordinates`ツールを使用することです。結果はセッションステートに保存されます。
*   **天気エージェント：** このエージェントはセッションステートから座標を読み取り、`get_weather`ツールを使用して最終的なレポートを取得します。

`weather_agent/agent.py`ファイルの末尾に次のコードを追加してください：

```python
# weather_agent/agent.py内、ツール関数の下

from google.adk.agents import Agent, SequentialAgent

# (上記のツール関数がここにあるべきです)

# --- エージェント1：ジオコーダー ---
geocoder_agent = Agent(
        name="geocoder",
        model="gemini-live-2.5-flash-preview",
        instruction="ユーザーから都市名が与えられたら、get_coordinatesツールを使用してその緯度と経度を検索します。",
        tools=[get_coordinates],
        output_key="coordinates" # 出力をセッションステートに保存
)

# --- エージェント2：天気予報士 ---
weather_agent = Agent(
        name="weather_forecaster",
        model="gemini-live-2.5-flash-preview",
        instruction=(
                "セッションステートの'coordinates'キーの下に座標を受け取ります。"
                "これらの座標をget_weatherツールで使用して天気予報を取得し、"
                "その予報をフレンドリーで明確な方法でユーザーに提示してください。"
        ),
        tools=[get_weather]
)

# --- マネージャー：シーケンシャルワークフロー ---
root_agent = SequentialAgent(
        name="weather_workflow",
        sub_agents=[geocoder_agent, weather_agent],
        description="最初に都市の座標を見つけ、次にその場所の天気を取得する2段階のエージェント。"
)
```

#### 3.3 対話型コンソールの起動：`adk web`

ツールとエージェントのワークフローが定義されたので、いよいよ私たちの創造物を動かしてみましょう。

1.  **親ディレクトリに移動：** ターミナルで、`my_interactive_agents`ディレクトリにいることを確認してください。
2.  **コマンドの実行：** 次のコマンドを実行します³⁷：
        ```bash
        adk web
        ```
3.  **UIを開く：** ターミナルに、サーバーが起動したことを示すメッセージが表示されます。通常は`http://127.0.0.1:8000`です。このURLをウェブブラウザで開いてください。

#### 3.4 最初の音声コマンド

エージェントとの最初の会話をしてみましょう。

1.  **エージェントの選択：** 左上のドロップダウンメニューをクリックし、`weather_agent`を選択します。
2.  **マイクの有効化：** マイクアイコンをクリックし、ブラウザにマイクの使用を許可します。
3.  **コマンドを話す：** はっきりと「東京の天気はどうですか？」と話してください。

ブラウザがあなたの音声をテキストに変換し、エージェントに送信します。そして、東京のリアルタイムの天気予報がチャットウィンドウにストリーミングで表示されるのを見ることができます。

#### 3.5 エージェントの思考を見る：「イベント」タブ

UIの左側にある「イベント」タブをクリックして、魔法が起こる様子を見てみましょう。³¹
`SequentialAgent`が動作しているのがわかります。まず、`geocoder_agent`を呼び出し、それが`get_coordinates`ツールを呼び出します。結果（東京の緯度と経度）はセッションステートに保存されます。次に、`weather_agent`が呼び出されます。それはステートから座標を読み取り、`get_weather`ツールを呼び出して最終的なレポートを取得し、それがフォーマットされてあなたにストリーミングで返されます。このビジュアライザーにより、複雑なワークフロー全体が透明で理解しやすくなります。

#### 3.6 機能強化：エージェントに声を与える（テキスト読み上げ）

現在の会話は一方的な音声です。私たちが話し、エージェントはテキストで返信します。これを完全に音声ベースの対話にするために、エージェントに応答を声に出して話す能力を与えることができます。これには、Googleのテキスト読み上げ（TTS）APIを使用する新しいツールを作成します。

1.  **ライブラリのインストール：** まず、必要なGoogle Cloudライブラリをインストールする必要があります。ターミナルで（`.venv`が有効な状態で）、次を実行します：
        ```bash
        pip install google-cloud-texttospeech
        ```
2.  **`speak_text`ツールの作成：** 次に、`weather_agent/agent.py`ファイルに新しいツールを追加します。この関数はテキストを受け取り、それを音声データに変換してMP3ファイルとして保存します。
        ```python
        # weather_agent/agent.pyに、他のツールと並べてこの関数を追加します
        from google.cloud import texttospeech

        def speak_text(text_to_speak: str) -> dict:
                """
                テキスト文字列を音声に変換し、MP3ファイルとして保存します。
                このツールを使用して、ユーザーに音声応答を提供します。

                Args:
                        text_to_speak (str): 音声に合成するテキストコンテンツ。

                Returns:
                        dict: 保存された音声のステータスとファイル名を示す辞書。
                """
                try:
                        client = texttospeech.TextToSpeechClient()
                        synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)

                        voice = texttospeech.VoiceSelectionParams(
                                language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                        )

                        audio_config = texttospeech.AudioConfig(
                                audio_encoding=texttospeech.AudioEncoding.MP3
                        )

                        response = client.synthesize_speech(
                                input=synthesis_input, voice=voice, audio_config=audio_config
                        )

                        filename = "response.mp3"
                        with open(filename, "wb") as out:
                                out.write(response.audio_content)
                                print(f"--- 音声コンテンツが'{filename}'に書き込まれました ---")

                        return {"status": "success", "file_saved": filename}
                except Exception as e:
                        print(f"TTSツールでエラーが発生しました：{e}")
                        return {"status": "error", "error_message": str(e)}
        ```
        この関数はTTSクライアントを初期化し、音声と音声フォーマットを設定し、APIを呼び出して音声を合成し、結果のバイナリ音声データを`response.mp3`という名前のファイルに書き込みます。⁴⁵

3.  **エージェントの更新：** 最後に、`root_agent`を更新して、この新しいツールを認識させ、その使用方法を指示する必要があります。`agent.py`の`root_agent`定義を次のように変更します：
        ```python
        # weather_agent/agent.pyで、root_agentの定義を更新します

        # --- 天気予報士を更新して出力を保存するようにします ---
        weather_agent = Agent(
                name="weather_forecaster",
                model="gemini-live-2.5-flash-preview",
                instruction=(
                        "セッションステートの'coordinates'キーの下に座標を受け取ります。"
                        "これらの座標をget_weatherツールで使用して天気予報を取得します。"
                ),
                tools=[get_weather],
                output_key="report" # 最終レポートをステートに保存
        )

        # --- 話すための新しいエージェントを追加 ---
        speaker_agent = Agent(
                name="speaker",
                model="gemini-live-2.5-flash-preview",
                instruction=(
                        "セッションステートの'report'キーの下に天気予報を受け取ります。"
                        "まず、この予報をテキスト形式でユーザーに提示します。"
                        "次に、'speak_text'ツールを使用して同じ予報テキストを音声に変換します。"
                        "最後に、音声版が保存されたことをユーザーに伝えます。"
                ),
                tools=[speak_text]
        )

        # --- マネージャーを更新して新しいスピーカーエージェントを含める ---
        root_agent = SequentialAgent(
                name="weather_workflow",
                sub_agents=[geocoder_agent, weather_agent, speaker_agent], # speaker_agentを末尾に追加
                description="座標を見つけ、天気を取得し、結果を話す3段階のエージェント。"
        )
        ```
        新しい専門家`speaker_agent`を追加し、それを`SequentialAgent`の組み立てラインの最後に追加しました。

4.  **音声出力のテスト：**
        `adk web`サーバーを再起動します。ブラウザを更新し、`weather_agent`を選択して、「ニューヨークの天気はどうですか？」と声で尋ねてみてください。
        エージェントは以前と同様にテキスト応答をストリーミングしますが、今度は「天気は...この予報の音声版も保存しました。」のようなことも言います。コンピュータの`my_interactive_agents`フォルダを確認すると、新しいファイル`response.mp3`が見つかり、それを再生してエージェントの声を聞くことができます。

---

# Part 2: English version

## The Interactive Agent Playbook: A Guide to Voice and Streaming with Google ADK

### Section 1: The Foundations of Interactive Agents

Welcome to the frontier of artificial intelligence, where we move beyond simple question-and-answer bots to create truly interactive and autonomous AI agents. This guide is designed for the technical enthusiast, the curious tinkerer, and the citizen developer—anyone who wants to build sophisticated AI without needing a formal background in programming. We will embark on a practical, hands-on journey using Google's Agent Development Kit (ADK), a powerful open-source framework that simplifies the creation of complex AI systems.¹ By the end of this playbook, you will have built three distinct, voice-controlled agents that not only understand your commands but also respond in real time, bridging the gap between digital instructions and physical actions.

#### 1.1 What is an AI Agent? From Simple Bots to Autonomous Thinkers

At its core, an AI agent is a software program designed to act on your behalf to achieve specific goals.⁴ It's a significant leap from a traditional chatbot. While a chatbot might answer a question based on a script, an AI agent can perceive its environment, make decisions, and take actions to complete multi-step tasks.⁶
To make this concept more tangible, it's helpful to think of an AI agent as having three fundamental components, much like a person ⁹:

*   **The Brain (Decision-Making):** This is the core reasoning engine, typically powered by a Large Language Model (LLM) like Google's Gemini.¹² The LLM allows the agent to understand natural language, break down complex requests into smaller steps, and formulate a plan of action.⁶ It's the part of the agent that "thinks."
*   **The Senses (Perception):** An agent needs to gather information to understand its environment and the user's request. These "senses" can be data from various sources: user text input, voice commands, information from a database, or real-time data from a web API.⁸
*   **The Hands (Action & Tools):** Once the agent has a plan, it needs a way to execute it. This is where "tools" come in. Tools are the agent's capabilities—its "hands"—that allow it to interact with the world.² A tool can be anything from a function that searches the web, to one that queries a database, sends an email, or even controls a physical device.¹⁴

Frameworks like Google's Agent Development Kit (ADK) provide a structured, code-first environment for assembling these components. Think of ADK as a high-tech construction kit for AI. It provides the blueprints (`Agent` classes), pre-fabricated parts (built-in tools), and assembly instructions (orchestration logic) that let you focus on what you want your agent to do, rather than getting bogged down in the low-level engineering of how it all connects.¹ This approach makes agent development feel more like modern software development, accessible even to those new to the field.

#### 1.2 The Magic of Interaction Part 1: How Your Agent "Talks" in Real Time

One of the most compelling features of a modern AI agent is its ability to communicate fluidly, without awkward pauses. This real-time feedback is not just a cosmetic enhancement; it fundamentally changes the user's perception of the agent's responsiveness and intelligence. This capability is powered by a web technology called Server-Sent Events (SSE).²¹

Imagine you are watching a live news broadcast. You don't have to refresh your screen every few seconds to see if there's an update; the new information—the news ticker at the bottom, the breaking news banner—is "pushed" to your screen as it happens. This is the core principle of SSE. It establishes a persistent, one-way communication channel from the server (where the agent lives) to your browser (the client).²²

When you run the `adk web` command, it starts a local web server that includes a special endpoint: `/run_sse`.²⁵ When the ADK web interface in your browser connects to this endpoint, it's like tuning into that live broadcast. The agent doesn't wait until its entire thought process is complete to send a response. Instead, as the LLM generates the answer token by token (word by word), the ADK server sends each piece immediately down this open channel.²⁸

The result for the user is the familiar "live typing" effect, where the agent's response appears on the screen as if it's being typed out in real time. This dramatically reduces perceived latency. Even if the total time to generate the full answer is a few seconds, the user sees a response begin to form almost instantly, making the interaction feel faster, more natural, and more engaging.²⁸ This streaming architecture is a cornerstone of the interactive agents we will build.

#### 1.3 The Magic of Interaction Part 2: How Your Agent "Listens" to Your Voice

The other half of a natural conversation is, of course, listening. The ADK web interface provides a seamless way to interact with your agents using your voice, and it accomplishes this by leveraging a powerful technology built directly into modern web browsers: the Web Speech API.²⁹

It is essential to understand where the "magic" of speech-to-text transcription happens. It's not the ADK agent or the server that initially processes your voice. Instead, the browser itself handles this task. When you click the microphone icon in the ADK web UI, you are giving the browser permission to access your microphone.³¹ This action activates the `SpeechRecognition` interface of the Web Speech API.²⁹

The data flow is simple yet elegant:

1.  **You Speak:** You issue a verbal command, like "What's the weather in Paris?"
2.  **The Browser Listens:** The Web Speech API, running locally in your browser, captures the audio from your microphone.
3.  **The Browser Transcribes:** The browser sends this audio to a server-based recognition engine (often the same one that powers services like Google Assistant or Siri) and receives a text transcription in return.²⁹
4.  **Text is Sent:** The resulting text string, "What's the weather in Paris?", is then placed into the input box of the ADK web UI and sent to the ADK server, exactly as if you had typed it manually.

This architectural design provides a profound advantage. The core logic of our AI agent, which we will write in Python, remains completely independent of the input method. The agent is designed to receive and process text. It doesn't need to know or care whether that text originated from a keyboard, a microphone, or another automated system. This separation of concerns—letting the browser handle the complexities of audio processing and the agent handle the logic of reasoning and action—is a powerful principle that makes building voice-enabled applications surprisingly straightforward. It allows us, as agent builders, to focus entirely on defining our agent's capabilities and intelligence, confident that the interface can gracefully handle the translation from spoken word to written command.

#### 1.4 The Right Brain for the Job: Choosing a Voice-Optimized Model

To create the most natural and responsive voice interactions, we need to use a model specifically designed for this purpose. While many models can process text, only certain models are optimized for the low-latency, bidirectional communication that makes a voice conversation feel real. These models support what is known as the "Live API." ³³

For all the projects in this guide, we will use the **`gemini-live-2.5-flash-preview`** model. This model is part of the Gemini family but is specifically engineered to handle real-time streams of audio, video, or text and deliver immediate, human-like spoken responses.³⁴ Using this model ensures that our agents can not only understand our voice commands but can also begin responding almost instantly, enabling a truly fluid and interactive conversational experience.

#### 1.5 Our Goal: Building Truly Interactive Agents

By combining real-time streaming output (SSE) with browser-based voice input (Web Speech API) and a voice-optimized LLM, we can elevate our agents from simple command-line tools to dynamic, conversational partners. The following table illustrates the significant leap in user experience that these technologies enable, which is the central goal of this playbook.

**Table 1: From Standard to Interactive Agents**

| Feature | Standard Agent Interaction | Enhanced Interactive Agent (Our Goal) | Key Benefit |
| :--- | :--- | :--- | :--- |
| **Input Method** | Text-only; requires typing commands. | Voice-activated; user speaks commands naturally. | **Accessibility & Speed:** Lowers the barrier to entry and allows for faster, hands-free interaction. |
| **Response Delivery** | "Blocking"; user waits for the full response to be generated before seeing any output. | "Streaming"; the agent's response appears token-by-token in real time. | **Reduced Perceived Latency:** The agent feels more responsive and "alive," improving user engagement. |
| **Feedback Loop** | Opaque; the user only sees the final result without understanding the intermediate steps. | Transparent; the UI can show the agent's "thought process," including tool calls and their results as they happen. | **Trust & Understanding:** Demystifies the agent's reasoning, allowing users to see how it arrived at an answer. |
| **Modality** | Unimodal (Text in, Text out). | Multimodal (Voice in, Text/Voice out). | **Natural Interaction:** Creates a more human-like conversational experience that is more intuitive and versatile. |

With this foundational understanding, we are now ready to set up our development environment and begin building our first interactive agent.

### Section 2: Your ADK Development Environment: A No-Fear Setup Guide

Before we can build, we need a workshop. This section provides a meticulous, step-by-step guide to preparing your computer for agent development. Following these instructions carefully will create a clean, isolated, and functional environment, preventing common issues and ensuring a smooth journey ahead. The goal is to eliminate any setup friction, allowing you to focus on the creative process of agent building.

#### 2.1 Essential Tools: Python and Visual Studio Code

Our agents will be written in Python, a powerful and readable programming language that is the standard for AI development. We will use Visual Studio Code (VS Code), a free and highly versatile code editor that works on all major operating systems.

*   **Install Python:** The Agent Development Kit requires Python version 3.9 or higher.² If you don't have Python installed, or have an older version, visit the official Python website at [python.org](https://python.org). Download the installer for your operating system (Windows, macOS, or Linux) and follow the installation instructions. Crucially, on Windows, ensure you check the box that says "Add Python to PATH" during the installation process.
*   **Install Visual Studio Code:** VS Code will be our primary tool for writing and editing the agent's code. It provides helpful features like syntax highlighting and an integrated terminal. Download it for free from the official website: [code.visualstudio.com](https://code.visualstudio.com).

#### 2.2 Creating a "Sandbox": The Power of Virtual Environments

When working on Python projects, it is a critical best practice to use a "virtual environment." Think of it as creating a clean, private sandbox or workspace for each project.² This sandbox contains its own copy of Python and its own set of installed libraries, ensuring that the tools for one project don't interfere with the tools for another.

Let's create and activate our sandbox. Open a new terminal or command prompt to proceed. On Windows, you can search for "Command Prompt" or "PowerShell". On macOS, you can find the "Terminal" app in your Utilities folder.

1.  **Create a Project Folder:** First, create a main folder where all our agent projects will live.
        ```bash
        mkdir my_interactive_agents
        cd my_interactive_agents
        ```

2.  **Create the Virtual Environment:** Inside this new folder, run the following command. This creates a sub-folder named `.venv` which will contain our sandbox.
        ```bash
        python -m venv .venv
        ```

3.  **Activate the Virtual Environment:** To start using the sandbox, you must "activate" it. The command differs slightly based on your operating system.³¹
        *   **On macOS or Linux:**
                ```bash
                source .venv/bin/activate
                ```
        *   **On Windows (using Command Prompt):**
                ```cmd
                .venv\Scripts\activate
                ```
        *   **On Windows (using PowerShell):**
                ```powershell
                .venv\Scripts\Activate.ps1
                ```
        You will know the virtual environment is active because your command prompt will now be prefixed with `(.venv)`. You must perform this activation step every time you open a new terminal to work on this project.

#### 2.3 Installing the Agent Construction Kit

With our virtual environment active, we can now install the Google ADK library and the `requests` library, which we'll need for making API calls.
Run the following command in your terminal:

```bash
pip install google-adk requests
```

This installation process may take a minute or two. Once it's complete, the `adk` command-line tool will be available within your activated environment.³⁹

#### 2.4 The Keys to the Kingdom: Obtaining Your API Keys

Our agents will need to access external services to perform their tasks. Each service requires a unique API key—a password that authenticates the agent's requests. For our first project, we will need three keys.

*   **Google API Key (for the Agent's Brain):**
        1.  Navigate to Google AI Studio: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey).³
        2.  Sign in with your Google account.
        3.  Click "Create API key in new project".
        4.  Copy the generated key and store it somewhere safe.
*   **OpenWeatherMap API Key (for Weather Data):**
        1.  Go to [openweathermap.org](https://openweathermap.org) and create a free account.⁴⁰
        2.  After signing in, navigate to your account page and find the "API keys" tab.
        3.  Copy your default API key. Note that it may take a few minutes for this key to become active.
*   **API-Ninjas API Key (for Geocoding):**
        1.  Go to [api-ninjas.com](https://api-ninjas.com) and register for a free account.
        2.  After signing in, your API key will be displayed on your account page.
        3.  Copy this key. The free tier is generous and perfect for our project.

#### 2.5 Structuring Your First Agent Project

The ADK expects projects to follow a specific folder structure. This convention helps the framework automatically discover and run your agents. Let's create the structure for our first project, the weather forecaster.³⁷
Ensure you are still inside the `my_interactive_agents` directory in your terminal, with your virtual environment active. Run the following commands:

```bash
mkdir weather_agent
touch weather_agent/__init__.py
touch weather_agent/agent.py
touch weather_agent/.env
```

This creates a new folder for our agent and three empty files inside it. Let's break down the purpose of each file:

*   `weather_agent/`: This is a self-contained "module" for our weather agent. As we build more agents, we will create similar folders for each one.
*   `__init__.py`: This is a special, often empty, Python file that tells Python to treat the `weather_agent` folder as a package—a collection of code that can be imported. We will add one line to this file.
*   `agent.py`: This is the main file where we will write the actual logic for our agent—its tools and its "brain."
*   `.env`: This is a special file used to store environment variables, most importantly, our secret API keys. The ADK framework is designed to automatically read this file, keeping our secrets out of our main code.

#### 2.6 Configuring Your API Keys

The final setup step is to securely store your API keys where the ADK can find them.

1.  **Open the Project in VS Code:** In your terminal, from the `my_interactive_agents` directory, type `code .` and press Enter. This will open the entire project folder in Visual Studio Code.
2.  **Edit the `.env` file:** In the VS Code file explorer on the left, navigate into the `weather_agent` folder and click on the `.env` file to open it.
3.  **Add Your Keys:** Paste the following lines into the file ³⁶:
        ```
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY="PASTE_YOUR_GOOGLE_API_KEY_HERE"
        OPENWEATHER_API_KEY="PASTE_YOUR_OPENWEATHER_API_KEY_HERE"
        API_NINJAS_KEY="PASTE_YOUR_API_NINJAS_KEY_HERE"
        ```
4.  **Replace the Placeholders:** Replace the placeholder text with the actual API keys you copied. Be sure to keep the quotation marks.
5.  **Edit the `__init__.py` file:** Open the `__init__.py` file and add the following line. This tells the ADK how to load the agent from this package.³¹
        ```python
        from . import agent
        ```
6.  **Save Both Files:** Save your changes to both files.

Your development environment is now fully configured. We have a secure place for our API keys, a structured project folder, and all the necessary software installed. We are ready to build our first agent.

### Section 3: Project 1: The Voice-Enabled Streaming Weather Forecaster

Our first project will be a conversational weather agent that uses live, real-time data. To achieve this, we will build a two-step workflow. First, an agent will use a geocoding tool to convert a city name into geographic coordinates (latitude and longitude). Second, another agent will take those coordinates and use a weather tool to fetch the current conditions. This multi-tool, multi-agent approach is a powerful pattern for solving complex problems.

#### 3.1 Giving Your Agent Skills: The Geocoding and Weather Tools

We will define two tools. The first, `get_coordinates`, will use the API-Ninjas service to find a city's location. The second, `get_weather`, will use the OpenWeatherMap API to get the forecast for that location.⁴⁰
Open the `weather_agent/agent.py` file in VS Code and add the following Python code:

```python
# In weather_agent/agent.py
import os
import requests

# --- TOOL 1: Geocoding (City -> Coordinates) ---
def get_coordinates(city: str) -> dict:
        """
        Converts a city name into its geographical latitude and longitude.

        Args:
                city (str): The name of the city, for example "New York" or "London".

        Returns:
                dict: A dictionary containing 'latitude' and 'longitude' on success,
                          or an 'error_message' on failure.
        """
        print(f"--- Tool Executed: get_coordinates(city='{city}') ---")
        api_key = os.getenv("API_NINJAS_KEY")
        if not api_key:
                return {"status": "error", "error_message": "API-Ninjas key not found."}

        api_url = f'https://api.api-ninjas.com/v1/geocoding?city={city}'
        try:
                response = requests.get(api_url, headers={'X-Api-Key': api_key})
                response.raise_for_status()
                data = response.json()
                if data and isinstance(data, list):
                        return {
                                "status": "success",
                                "latitude": data[0]['latitude'],
                                "longitude": data[0]['longitude']
                        }
                else:
                        return {"status": "error", "error_message": f"Could not find coordinates for {city}."}
        except requests.exceptions.RequestException as e:
                return {"status": "error", "error_message": f"API request failed: {e}"}

# --- TOOL 2: Weather (Coordinates -> Forecast) ---
def get_weather(lat: float, lon: float) -> dict:
        """
        Retrieves the current weather report for a given latitude and longitude.

        Args:
                lat (float): The latitude of the location.
                lon (float): The longitude of the location.

        Returns:
                dict: A dictionary containing the weather report or an error message.
        """
        print(f"--- Tool Executed: get_weather(lat={lat}, lon={lon}) ---")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
                return {"status": "error", "error_message": "OpenWeatherMap API key not found."}

        api_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                report = (
                        f"The weather is {data['weather'][0]['description']} with a temperature of "
                        f"{data['main']['temp']}°C and {data['main']['humidity']}% humidity."
                )
                return {"status": "success", "report": report}
        except requests.exceptions.RequestException as e:
                return {"status": "error", "error_message": f"API request failed: {e}"}
```

Notice the clear and descriptive docstrings for each function. These are essential for the LLM to understand what each tool does and how to use it correctly.⁴²

#### 3.2 Building the Agent's Brains (Plural)

Since we have a two-step process, we will create a two-agent assembly line managed by a `SequentialAgent`.

*   **Geocoder Agent:** This agent's only job is to use the `get_coordinates` tool. It will save its result to the session state.
*   **Weather Agent:** This agent will read the coordinates from the session state and use the `get_weather` tool to get the final report.

Add the following code to the bottom of your `weather_agent/agent.py` file:

```python
# In weather_agent/agent.py, below the tool functions

from google.adk.agents import Agent, SequentialAgent

# (The tool functions from above should be here)

# --- AGENT 1: The Geocoder ---
geocoder_agent = Agent(
        name="geocoder",
        model="gemini-live-2.5-flash-preview",
        instruction="Given a city name from the user, use the get_coordinates tool to find its latitude and longitude.",
        tools=[get_coordinates],
        output_key="coordinates" # Save the output to the session state
)

# --- AGENT 2: The Weather Forecaster ---
weather_agent = Agent(
        name="weather_forecaster",
        model="gemini-live-2.5-flash-preview",
        instruction=(
                "You will receive coordinates in the session state under the key 'coordinates'. "
                "Use these coordinates with the get_weather tool to get the weather report. "
                "Then, present this report to the user in a friendly and clear manner."
        ),
        tools=[get_weather]
)

# --- THE MANAGER: The Sequential Workflow ---
root_agent = SequentialAgent(
        name="weather_workflow",
        sub_agents=[geocoder_agent, weather_agent],
        description="A two-step agent that first finds a city's coordinates and then gets the weather for that location."
)
```

#### 3.3 Launching the Interactive Console: `adk web`

With our tools and agent workflow defined, it's time to bring our creation to life.

1.  **Navigate to the Parent Directory:** In your terminal, make sure you are in the `my_interactive_agents` directory.
2.  **Run the Command:** Execute the following command ³⁷:
        ```bash
        adk web
        ```
3.  **Open the UI:** Your terminal will display a message indicating that the server has started, usually on `http://127.0.0.1:8000`. Open this URL in your web browser.

#### 3.4 Your First Voice Command

Let's have our first conversation with the agent.

1.  **Select the Agent:** Click the dropdown menu in the top-left and select `weather_agent`.
2.  **Activate the Microphone:** Click the microphone icon and allow your browser to use it.
3.  **Speak Your Command:** Clearly say, "What is the weather like in Tokyo?"

The browser will transcribe your speech, send it to the agent, and you will see the real-time weather report for Tokyo stream into the chat window.

#### 3.5 Seeing the Agent Think: The Events Tab

Click on the "Events" tab on the left side of the UI to see the magic happen.³¹ You will see the `SequentialAgent` at work. First, it invokes the `geocoder_agent`, which calls the `get_coordinates` tool. The result (the latitude and longitude for Tokyo) is saved to the session state. Then, the `weather_agent` is invoked. It reads the coordinates from the state and calls the `get_weather` tool to get the final report, which is then formatted and streamed back to you. This visualizer makes the entire complex workflow transparent and easy to understand.

#### 3.6 Enhancement: Giving the Agent a Voice (Text-to-Speech)

Our conversation is currently one-way voice. We speak, and it types back. To make it a fully voice-based interaction, we can give our agent the ability to speak its responses aloud. We'll do this by creating a new tool that uses Google's Text-to-Speech (TTS) API.

1.  **Install the Library:** First, we need to install the necessary Google Cloud library. In your terminal (with the `.venv` still active), run:
        ```bash
        pip install google-cloud-texttospeech
        ```
2.  **Create the `speak_text` Tool:** Now, let's add a new tool to our `weather_agent/agent.py` file. This function will take text, convert it into audio data, and save it as an MP3 file.
        ```python
        # In weather_agent/agent.py, add this function alongside the other tools
        from google.cloud import texttospeech

        def speak_text(text_to_speak: str) -> dict:
                """
                Converts a string of text into spoken audio and saves it as an MP3 file.
                Use this tool to provide a voice response to the user.

                Args:
                        text_to_speak (str): The text content to be synthesized into speech.

                Returns:
                        dict: A dictionary indicating the status and the filename of the saved audio.
                """
                try:
                        client = texttospeech.TextToSpeechClient()
                        synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)

                        voice = texttospeech.VoiceSelectionParams(
                                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                        )

                        audio_config = texttospeech.AudioConfig(
                                audio_encoding=texttospeech.AudioEncoding.MP3
                        )

                        response = client.synthesize_speech(
                                input=synthesis_input, voice=voice, audio_config=audio_config
                        )

                        filename = "response.mp3"
                        with open(filename, "wb") as out:
                                out.write(response.audio_content)
                                print(f"--- Audio content written to '{filename}' ---")

                        return {"status": "success", "file_saved": filename}
                except Exception as e:
                        print(f"Error in TTS tool: {e}")
                        return {"status": "error", "error_message": str(e)}
        ```
        This function initializes the TTS client, configures the voice and audio format, calls the API to synthesize the speech, and writes the resulting binary audio data to a file named `response.mp3`.⁴⁵

3.  **Update the Agent:** Finally, we need to update our `root_agent` to make it aware of this new tool and instruct it on how to use it. Modify the `root_agent` definition in `agent.py`:
        ```python
        # In weather_agent/agent.py, update the root_agent definition

        # --- Update the Weather Forecaster to save its output ---
        weather_agent = Agent(
                name="weather_forecaster",
                model="gemini-live-2.5-flash-preview",
                instruction=(
                        "You will receive coordinates in the session state under the key 'coordinates'. "
                        "Use these coordinates with the get_weather tool to get the weather report."
                ),
                tools=[get_weather],
                output_key="report" # Save the final report to the state
        )

        # --- Add a new agent for speaking ---
        speaker_agent = Agent(
                name="speaker",
                model="gemini-live-2.5-flash-preview",
                instruction=(
                        "You will receive a weather report in the session state under the key 'report'. "
                        "First, present this report to the user in text form. "
                        "Second, use the 'speak_text' tool to convert the same report text to audio. "
                        "Finally, inform the user that an audio version has been saved."
                ),
                tools=[speak_text]
        )

        # --- Update THE MANAGER to include the new speaker agent ---
        root_agent = SequentialAgent(
                name="weather_workflow",
                sub_agents=[geocoder_agent, weather_agent, speaker_agent], # Add speaker_agent to the end
                description="A three-step agent that finds coordinates, gets the weather, and speaks the result."
        )
        ```
        We've added a new specialist `speaker_agent` and added it to the end of our `SequentialAgent`'s assembly line.

4.  **Testing the Voice Output:**
        Restart the `adk web` server. Refresh your browser, select the `weather_agent`, and use your voice to ask, "What's the weather in New York?"
        The agent will stream its text response as before, but now it will also say something like: "The weather is... I have also saved an audio version of this forecast for you." If you check the `my_interactive_agents` folder on your computer, you will find a new file, `response.mp3`, which you can play to hear the agent's voice.

### Section 4: Project 2: The Voice-Powered Content Creation Team

Having mastered a multi-agent workflow, we now apply this pattern to a more complex task: researching, writing, and translating a blog post. This project demonstrates how to break down a creative task into a series of manageable steps, with a specialized agent assigned to each step.

#### 4.1 The Assembly Line Pattern: `SequentialAgent`

As in our weather project, we will use a `SequentialAgent` to act as a factory manager, ensuring that the user's request moves from one specialist to the next in the correct order.¹⁴ The output of one agent becomes the input for the next, creating a powerful content pipeline.⁴⁸

#### 4.2 Meet the Team: Researcher, Writer, and Translator

Our content creation assembly line will consist of three specialist agents. First, let's set up a new project folder. In your terminal, inside the `my_interactive_agents` directory, create the structure for our new agent:

```bash
mkdir content_creator
touch content_creator/__init__.py
touch content_creator/agent.py
touch content_creator/.env
```

Copy the contents of your `weather_agent/.env` file (with your API keys) into the new `content_creator/.env` file. Then, open `content_creator/agent.py` in VS Code.

*   **Agent 1: The Researcher**
        The first agent's job is to gather raw information using ADK's built-in `google_search` tool.¹⁷ It will save its findings to the session state using the `output_key` parameter.²
        Add the following code to `content_creator/agent.py`:
        ```python
        # In content_creator/agent.py
        from google.adk.agents import Agent, SequentialAgent
        from google.adk.tools import google_search

        # --- AGENT 1: The Researcher ---
        researcher_agent = Agent(
                name="researcher",
                model="gemini-live-2.5-flash-preview",
                description="A research specialist that uses Google Search to find information on a given topic.",
                instruction=(
                        "You are a world-class researcher. Given a user's topic, use the google_search tool "
                        "to find relevant facts, statistics, and key points. Synthesize your findings into "
                        "a concise set of bullet points. Do not write a full article, only provide research notes."
                ),
                tools=[google_search],
                output_key="research_notes" # Save the output to the session state
        )
        ```

*   **Agent 2: The Writer**
        The second agent takes the `research_notes` and transforms them into a well-structured article draft.
        Add this code below the researcher agent in the same file:
        ```python
        # --- AGENT 2: The Writer ---
        writer_agent = Agent(
                name="writer",
                model="gemini-live-2.5-flash-preview",
                description="A content writer that drafts articles based on research notes.",
                instruction=(
                        "You are a skilled blog post writer. Your task is to take the research notes provided in "
                        "the session state under the key 'research_notes' and write a clear, engaging, and "
                        "well-structured blog post. The post should have an introduction, a body, and a conclusion."
                ),
                output_key="draft_content" # Save the new draft to the session state
        )
        ```

*   **Agent 3: The Translator**
        The final specialist translates the English draft into another language using a custom `translate_text` tool, which leverages the Google Cloud Translation API.
        First, install the necessary library in your terminal:
        ```bash
        pip install google-cloud-translate
        ```
        Now, add the tool and the translator agent to your `agent.py` file. We will target Japanese for our translation.⁵¹
        ```python
        # Add this import at the top of the file
        from google.cloud import translate_v2 as translate

        # --- TRANSLATION TOOL ---
        def translate_text(text_to_translate: str, target_language: str) -> dict:
                """
                Translates a given text into a specified target language using the
                Google Cloud Translation API.

                Args:
                        text_to_translate (str): The text content to be translated.
                        target_language (str): The ISO 639-1 code for the target language (e.g., 'ja' for Japanese).

                Returns:
                        dict: A dictionary containing the translated text or an error message.
                """
                try:
                        translate_client = translate.Client()
                        result = translate_client.translate(text_to_translate, target_language=target_language)
                        return {"status": "success", "translated_text": result['translatedText']}
                except Exception as e:
                        return {"status": "error", "error_message": str(e)}

        # --- AGENT 3: The Translator ---
        translator_agent = Agent(
                name="translator",
                model="gemini-live-2.5-flash-preview",
                description="A language specialist that translates text into a target language.",
                instruction=(
                        "You are a professional translator. Your task is to take the blog post content from "
                        "the session state under the key 'draft_content'. Use the 'translate_text' tool "
                        "to translate this content into the language requested by the user. If the user does not specify "
                        "a language, default to Japanese ('ja')."
                ),
                tools=[translate_text]
        )
        ```

#### 4.3 Assembling the Workflow

Now, we assemble the workflow with our `SequentialAgent`.
Add the following code to the very bottom of your `content_creator/agent.py` file:

```python
# In content_creator/agent.py

# (All agent and tool definitions from above should be here)

# --- THE MANAGER: Sequential Agent ---
root_agent = SequentialAgent(
        name="content_pipeline",
        sub_agents=[
                researcher_agent,
                writer_agent,
                translator_agent
        ],
        description="A multi-agent pipeline for researching, writing, and translating content."
)
```

#### 4.4 Initiating the Workflow with a Single Voice Command

1.  **Run the Web UI:** Restart your `adk web` server.
2.  **Select the Agent:** In the web UI, refresh the page and select the `content_creator` agent.
3.  **Give the Command:** Click the microphone and issue a command like: "Research the main benefits of regular exercise, write a short blog post about it, and then translate the post into Japanese."

The final output streamed to the chat window will be the fully translated Japanese blog post, the result of a collaborative effort between three specialized AI agents, all triggered by a single voice command.

### Section 5: Project 3: Bridging Digital and Physical with a Voice-Controlled Robot Arm

Our capstone project takes our agents into the physical world. We will build a system where you can speak a command to your computer, and a robot arm connected to a Raspberry Pi will move in response. This project powerfully illustrates how AI agents can serve as intuitive natural language interfaces for robotics.

#### 5.1 The Hardware Setup: Raspberry Pi and a Servo Motor

*   **Raspberry Pi:** Any model with Wi-Fi and GPIO pins.
*   **Servo Motor:** A small, standard servo like an SG90.
*   **Power Supply:** A 5V external power supply for the servo.
*   **Jumper Wires:** To connect the components.

> **Crucially, do not power the servo directly from the Raspberry Pi's GPIO pins.** Use a separate power supply for the motor to avoid damaging the Pi.⁵⁶

Follow this connection diagram carefully:

1.  Connect the servo's red wire (power) to the positive (+) terminal of your 5V external power supply.
2.  Connect the servo's brown or black wire (ground) to the negative (-) terminal.
3.  Connect the servo's orange or yellow signal wire to GPIO 17 on the Raspberry Pi.
4.  Run a jumper wire from a Ground (GND) pin on the Raspberry Pi to the negative (-) terminal of your external power supply to create a common ground.

#### 5.2 The Software on the Pi: A Simple Control Server

We will turn the Raspberry Pi into a simple web server that listens for commands over the local Wi-Fi network using Flask and the `gpiozero` library.⁵⁶

On your Raspberry Pi:

1.  **Access its terminal** (e.g., via SSH).⁵⁸
2.  **Install Libraries:**
        ```bash
        sudo apt-get update
        sudo apt-get install python3-pip
        pip3 install Flask gpiozero
        ```
3.  **Find the Pi's IP Address:** Run `hostname -I` on the Pi and write down the IP address.
4.  **Create the Server Script:** On your Raspberry Pi, create a file named `robot_server.py` and add the following code:
        ```python
        # On the Raspberry Pi: robot_server.py
        from flask import Flask, request, jsonify
        from gpiozero import Servo
        from time import sleep

        servo = Servo(17) # Assumes servo signal wire is on GPIO 17
        app = Flask(__name__)

        @app.route('/set_angle', methods=['POST'])
        def set_angle():
                data = request.get_json()
                if 'angle' not in data:
                        return jsonify({"status": "error", "message": "'angle' parameter missing"}), 400

                angle = int(data['angle'])
                if not 0 <= angle <= 180:
                        return jsonify({"status": "error", "message": "Angle must be between 0 and 180"}), 400

                # gpiozero's Servo.value maps angle to -1 (min) to 1 (max).
                # We need to convert our 0-180 degree input to this range.
                servo_value = (angle / 90.0) - 1.0
                servo.value = servo_value

                print(f"Moved servo to {angle} degrees.")
                sleep(1) # Give the servo time to move

                return jsonify({"status": "success", "angle_set": angle})

        if __name__ == '__main__':
                # Run the server, making it accessible to any device on the network
                app.run(host='0.0.0.0', port=5000)
        ```
5.  **Run the server:**
        ```bash
        python3 robot_server.py
        ```
        The server is now running on your Raspberry Pi, listening for network requests on port 5000.

#### 5.3 The Robot Controller Agent: A Tool for Physical Action

Now, back on your main computer, we will build the ADK agent that acts as the robot's brain. This agent's "tool" will be a function that sends a network request to the Raspberry Pi's server.

1.  **Project Setup:** On your main computer, inside the `my_interactive_agents` folder, create the new project structure:
        ```bash
        mkdir robot_controller
        touch robot_controller/__init__.py
        touch robot_controller/agent.py
        touch robot_controller/.env
        ```
        Copy your `.env` file with API keys into this new folder.

2.  **Install `requests` library:**
        ```bash
        pip install requests
        ```

3.  **Define the Tool and Agent:** Open `robot_controller/agent.py` and add the following code. Remember to replace `"YOUR_PI_IP_ADDRESS"` with the actual IP address of your Raspberry Pi.
        ```python
        # In robot_controller/agent.py on your main computer
        import requests
        from google.adk.agents import Agent

        # --- IMPORTANT: Change this to your Raspberry Pi's IP address ---
        PI_IP_ADDRESS = "YOUR_PI_IP_ADDRESS"
        # ----------------------------------------------------------------

        # --- Robot Control Tool ---
        def move_servo(angle: int) -> dict:
                """
                Moves the servo motor on the robot arm to a specific angle.

                Args:
                        angle (int): The target angle for the servo. An integer between 0 and 180.

                Returns:
                        dict: A dictionary indicating the result of the operation.
                """
                if not 0 <= angle <= 180:
                        return {"status": "error", "message": "Invalid angle. Please provide a value between 0 and 180."}

                url = f"http://{PI_IP_ADDRESS}:5000/set_angle"
                payload = {"angle": angle}

                try:
                        print(f"--- Sending command to robot: Move to {angle} degrees ---")
                        response = requests.post(url, json=payload, timeout=5)
                        response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
                        return response.json()
                except requests.exceptions.RequestException as e:
                        error_message = f"Failed to communicate with robot: {e}"
                        print(error_message)
                        return {"status": "error", "message": error_message}

        # --- Robot Controller Agent ---
        root_agent = Agent(
                name="robot_arm_controller",
                model="gemini-live-2.5-flash-preview",
                description="An agent that controls a physical robot arm by sending it commands.",
                instruction=(
                        "You are a precision robot arm controller. Your purpose is to translate human language "
                        "commands into specific angles for the robot arm. When the user asks to move the arm, "
                        "you must extract the numerical angle from the request and use the 'move_servo' tool to "
                        "execute the movement. Respond to the user by confirming the action you took."
                ),
                tools=[move_servo]
        )
        ```

#### 5.4 Commanding the Robot with Your Voice

The full system is now in place.

1.  **Run the Web UI:** Restart the `adk web` server from your `my_interactive_agents` directory.
2.  **Select the Agent:** Refresh the UI in your browser and select the `robot_controller` agent.
3.  **Issue Voice Commands:** Click the microphone and speak your commands. Try these:
        *   "Move the arm to 45 degrees."
        *   "Set the robot's position to 120."
        *   "Point the arm straight up, to 90 degrees."

With each command, you will see the physical servo motor move into position. You have now completed the end-to-end flow: your voice is transcribed by the browser, the text is sent to the ADK agent, the LLM intelligently parses the angle from your sentence and calls the `move_servo` tool, the tool sends an HTTP request over your Wi-Fi network to the Raspberry Pi, the Flask server on the Pi receives the request and instructs the GPIO pin to move the servo, and finally, a success message travels all the way back and streams into the web UI as confirmation. You are now controlling the physical world with your voice, mediated by an intelligent AI agent.

### Section 6: Architectural Insights and The Path Forward

Through these three projects, you have not only built applications but have also implemented powerful architectural patterns, gaining a deep, practical understanding of how modern interactive AI systems are constructed. This final section will consolidate that knowledge with a full system diagram and provide a clear path for continuing your agent development journey.

#### 6.1 The Big Picture: Tying It All Together

The robot controller project is the culmination of every concept we have covered. It combines voice input, natural language understanding, tool use, streaming output, and interaction with the physical world. The diagram below illustrates the complete, end-to-end flow of information in this system, showing how each component communicates with the next.

This diagram is a visual summary of the entire playbook. It demonstrates the elegant principle of separation of concerns: the browser handles audio, the ADK agent handles reasoning, the Python tool handles communication, the Flask server handles hardware abstraction, and the servo handles physical action. Understanding this flow is the key to designing your own complex, interactive systems.

#### 6.2 Key Patterns You Have Mastered

In building these three projects, you have gained hands-on experience with fundamental and powerful AI agent design patterns that are applicable to a wide range of real-world problems:

*   **Specialist Tool Agent:** Our weather forecaster is a classic example of this pattern: an agent with a narrow but deep set of capabilities defined by its specialized tools. This is the foundational pattern for building modular, reusable AI components.
*   **Sequential Workflow (The Assembly Line):** The content creation team demonstrated how to chain specialist agents together using `SequentialAgent`. This pattern is ideal for complex, multi-step processes where the order of operations is fixed and predictable, enabling higher-quality and more reliable outcomes.
*   **Physical World Interface (The Remote Control):** Our robot controller implemented a key pattern for IoT and robotics. The agent's tool does not control the hardware directly but instead communicates with a server running on the device. This abstracts away the complexity of hardware control and creates a clean, scalable, and robust interface between the AI "brain" and the physical "body."

#### 6.3 Where to Go From Here

You have taken the first significant steps into the world of agent development and are now equipped with the skills to build truly interactive applications. The journey doesn't end here. The Agent Development Kit and the broader AI ecosystem offer many avenues for further exploration:

*   **Explore Other Workflow Agents:** We focused on `SequentialAgent`, but ADK also provides `ParallelAgent` for running tasks concurrently and `LoopAgent` for iterative tasks, such as refining a piece of content until it meets a specific quality standard.¹⁴
*   **Give Your Agents Persistent Memory:** In our projects, the agent's memory (its "state") was ephemeral, lasting only for a single conversation. ADK includes a `SessionService` that can be configured to use a database, allowing your agents to remember information and context across multiple conversations with a user, leading to more personalized and intelligent interactions.³⁹
*   **Dive Deeper into Tools:** Explore the rich ecosystem of tools, from integrating with third-party libraries and connecting to Google Cloud services to even using other agents as tools for more complex delegation patterns.³⁹
*   **Consult Official Resources:** The official Google ADK documentation is an invaluable resource for deep dives into all features. The ADK Samples repository on GitHub also provides a wealth of ready-to-run examples for various use cases.¹

The field of AI agents is evolving at an incredible pace. By mastering the fundamental skills in this playbook, you are no longer a bystander but a builder, capable of turning your ideas into intelligent, interactive, and impactful AI agents. The possibilities are limited only by your imagination. Happy building!

### Works cited

1.  [google/adk-docs: An open-source, code-first Python toolkit ... - GitHub](https://github.com/google/adk-docs), accessed August 25, 2025
2.  [The Complete Guide to Google's Agent Development Kit (ADK) - Sid ...](https://www.siddharthbharath.com/the-complete-guide-to-googles-agent-development-kit-adk/), accessed August 25, 2025
3.  [Step-by-Step Guide to Create an AI agent with Google ADK ...](https://www.marktechpost.com/2025/05/20/step-by-step-guide-to-create-an-ai-agent-with-google-adk/), accessed August 25, 2025
4.  [Introduction to AI Agents - Prompt Engineering Guide](https://www.promptingguide.ai/agents/introduction), accessed August 25, 2025
5.  [Building AI Agents with ADK: The Foundation - Codelabs](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation), accessed August 25, 2025
6.  [What are AI Agents?- Agents in Artificial Intelligence Explained - AWS](https://aws.amazon.com/what-is/ai-agents/), accessed August 25, 2025
7.  [Understanding AI Agents: A Beginner's Guide - Domo](https://www.domo.com/blog/understanding-ai-agents-a-beginners-guide), accessed August 25, 2025
8.  [ai-agents-for-beginners | 11 Lessons to Get Started Building AI Agents](https://microsoft.github.io/ai-agents-for-beginners/01-intro-to-ai-agents/), accessed August 25, 2025
9.  [AI Agents Explained: Functions, Types, and Applications - HatchWorks](https://hatchworks.com/blog/ai-agents/ai-agents-explained/), accessed August 25, 2025
10. [Learn the Core Components of AI Agents - SmythOS](https://smythos.com/developers/agent-development/ai-agents-components/), accessed August 25, 2025
11. [Understanding AI Agents: A Beginner's Guide - Domo](https://www.domo.com/blog/understanding-ai-agents-a-beginners-guide/), accessed August 25, 2025
12. [What are AI agents? Definition, examples, and types | Google Cloud](https://cloud.google.com/discover/what-are-ai-agents), accessed August 25, 2025
13. [From Hello World to Hello Agent: Google's ADK Made Easy | by The AI Guy - Medium](https://medium.com/google-cloud/from-hello-world-to-hello-agent-googles-adk-made-easy-02a21bb9ce75), accessed August 25, 2025
14. [Google Agent Development Kit (ADK): A hands-on tutorial | articles - Wandb](https://wandb.ai/google_articles/articles/reports/Google-Agent-Development-Kit-ADK-A-hands-on-tutorial--VmlldzoxMzM2NTIwMQ), accessed August 25, 2025
15. [What are Components of AI Agents? - IBM](https://www.ibm.com/think/topics/components-of-ai-agents), accessed August 25, 2025
16. [Tools - Agent Development Kit - Google](https://google.github.io/adk-docs/tools/), accessed August 25, 2025
17. [Google Agent Development Kit (ADK): Tools and Integrations | by DhanushKumar | Medium](https://medium.com/@danushidk507/google-agent-development-kit-adk-tools-and-integrations-bfcccfc8ed64), accessed August 25, 2025
18. [Tools Make an Agent: From Zero to Assistant with ADK | Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk), accessed August 25, 2025
19. [google/adk-python: An open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. - GitHub](https://github.com/google/adk-python), accessed August 25, 2025
20. [proflead/how-to-build-ai-agent: How to build your own AI agent easily with Google ADK! In this beginner-friendly tutorial, I'll walk you through installing ADK, writing basic agent tools, creating your first AI agent, and running it! - GitHub](https://github.com/proflead/how-to-build-ai-agent), accessed August 25, 2025
21. [Streaming server-sent events | Apigee - Google Cloud](https://cloud.google.com/apigee/docs/api-platform/develop/server-sent-events), accessed August 25, 2025
22. [Real-Time Data Streaming with Server-Sent Events (SSE) - DEV Community](https://dev.to/serifcolakel/real-time-data-streaming-with-server-sent-events-sse-1gb2), accessed August 25, 2025
23. [Using server-sent events - MDN - Mozilla](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events), accessed August 25, 2025
24. [SSE vs Streamable HTTP: Why MCP Switched Transport Protocols - Bright Data](https://brightdata.com/blog/ai/sse-vs-streamable-http), accessed August 25, 2025
25. [Testing - Agent Development Kit - Google](https://google.github.io/adk-docs/get-started/testing/), accessed August 25, 2025
26. [ADK Version 1.10.0 Cloud Run Error When Calling the /run_sse Endpoint #2487 - GitHub](https://github.com/google/adk-python/issues/2487), accessed August 25, 2025
27. [REST API - Agent Development Kit - Google](https://google.github.io/adk-docs/api-reference/rest/), accessed August 25, 2025
28. [Bidi-streaming(live) in ADK - Agent Development Kit - Google](https://google.github.io/adk-docs/streaming/), accessed August 25, 2025
29. [Using the Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API), accessed August 25, 2025
30. [Speech recognition in the browser using Web Speech API - AssemblyAI](https://www.assemblyai.com/blog/speech-recognition-javascript-web-speech-api), accessed August 25, 2025
31. [Quickstart - Agent Development Kit - Google](https://google.github.io/adk-docs/get-started/quickstart/), accessed August 25, 2025
32. [Voice driven web apps - Introduction to the Web Speech API | Blog - Chrome for Developers](https://developer.chrome.com/blog/voice-driven-web-apps-introduction-to-the-web-speech-api), accessed August 25, 2025
33. [Get started with Live API | Gemini API | Google AI for Developers](https://ai.google.dev/gemini-api/docs/live), accessed August 28, 2025
34. [Gemini models | Gemini API | Google AI for Developers](https://ai.google.dev/gemini-api/docs/models), accessed August 25, 2025
35. [Your First ADK Agent: Building a Google Tasks To-Do Manager | by Aryan Irani - Medium](https://medium.com/google-cloud/your-first-adk-agent-building-a-google-tasks-to-do-manager-c3d4d2c317cd), accessed August 25, 2025
36. [Making First AI Agent Using Google's ADK | by Jayantjoshi | Jul, 2025 - Medium](https://medium.com/@jayantjoshi0001/making-first-ai-agent-using-googles-adk-36f0a73c3060), accessed August 25, 2025
37. [Quickstart: Build an agent with the Agent Development Kit | Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart), accessed August 25, 2025
38. [ADK Crash Course - From Beginner To Expert - Codelabs](https://codelabs.developers.google.com/onramp/instructions), accessed August 25, 2025
39. [Agent Development Kit - Google](https://google.github.io/adk-docs/), accessed August 25, 2025
40. [Current weather data - OpenWeatherMap](https://openweathermap.org/current), accessed August 28, 2025
41. [Geocoding API - API Ninjas](https://api-ninjas.com/api/geocoding), accessed August 28, 2025
42. [Agent Team - Agent Development Kit - Google](https://google.github.io/adk-docs/tutorials/agent-team/), accessed August 25, 2025
43. [Function tools - Agent Development Kit - Google](https://google.github.io/adk-docs/tools/function-tools/), accessed August 25, 2025
44. [The Google ADK Playbook: Part 2 — Giving Your Agent Custom ...](https://medium.com/@gopi.don/the-google-adk-playbook-part-2-giving-your-agent-custom-tools-fbed4ddef997), accessed August 25, 2025
45. [How to use Google's Text-to-Speech API in Python - Stack Overflow](https://stackoverflow.com/questions/54699541/how-to-use-googles-text-to-speech-api-in-python), accessed August 25, 2025
46. [Using the Text-to-Speech API with Python - Codelabs - Google](https://codelabs.developers.google.com/codelabs/cloud-text-speech-python3), accessed August 25, 2025
47. [How to Use Google Text-to-Speech API with Python on Google Cloud Platform (GCP) (2025)](https://www.youtube.com/watch?v=dOlV_oD_dr8), accessed August 25, 2025
48. [Google ADK for Beginners: Developing AI Agents with Google - YouTube](https://m.youtube.com/watch?v=f5Ihdw32tTw&t=1905s), accessed August 25, 2025
49. [Multi-agents: Sequential Workflow using Google ADK Gemini, Fast API, Streamlit - Create Game - DEV Community](https://dev.to/omerberatsezer/multi-agent-sequential-workflow-using-google-adk-gemini-fast-api-streamlit-create-game-kdk), accessed August 25, 2025
50. [ADK Multi-agentic Content creation tutorial.ipynb - GitHub](https://github.com/ashishbamania/Tutorials-On-Artificial-Intelligence/blob/main/Linkedin%20Content%20Creation%20with%20Google%20ADK/ADK%20Multi-agentic%20Content%20creation%20tutorial.ipynb), accessed August 25, 2025
51. [Support multiple languages with Google Translate | Business Messages](https://developers.google.com/business-communications/business-messages/trainings/tutorials/translate), accessed August 25, 2025
52. [Cloud Translation by Google - Simtech Development](https://simtechdev.com/blog/cloud-translation-by-google/), accessed August 25, 2025
53. [Cloud Translation](https://cloud.google.com/translate), accessed August 25, 2025
54. [Google Cloud Translation AI](https://cloud.google.com/blog/products/ai-machine-learning/google-cloud-translation-ai), accessed August 25, 2025
55. [ADK Course #3 - Build a Sequential Workflow Agent with ADK - YouTube](https://www.youtube.com/watch?v=9nCYEozVqs8), accessed August 25, 2025
56. [How to Control Servo Motors with a Raspberry Pi - DigiKey](https://www.digikey.com/en/maker/tutorials/2021/how-to-control-servo-motors-with-a-raspberry-pi), accessed August 25, 2025
57. [Servo Motor Control via the Raspberry Pi | by David - Medium](https://divadnoslo.medium.com/servo-motor-control-via-the-raspberry-pi-d702c70f52cc), accessed August 25, 2025
58. [Control a Raspberry Pi Remotely | Google Assistant SDK](https://developers.google.com/assistant/sdk/guides/library/python/embed/setup-headless), accessed August 25, 2025
59. [Agents - Agent Development Kit - Google](https://google.github.io/adk-docs/agents/), accessed August 25, 2025
60. [A collection of sample agents built with Agent Development (ADK) - GitHub](https://github.com/google/adk-samples), accessed August 25, 2025
61. [ADK Tutorials! - Agent Development Kit - Google](https://google.github.io/adk-docs/tutorials/), accessed August 25, 2025
