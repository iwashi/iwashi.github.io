---
layout: post
title: LLM推論に関する技術メモ
description: LLM推論に関する技術のメモ記事です。APIを利用するのではなく、どちらかいうと内部の技術に焦点を当てています。
category: null
tags: []
ogp: /assets/images/ogp/2025-07-20-llm-inference_ogp.png
---

## はじめに

BentoMLによる[LLM Inference Handbook](https://bentoml.com/llm/)という、LLMの推論をまとめたハンドブックがある。本記事ではハンドブックや他の情報も参照しつつ、自分のメモ用としてLM推論に関する技術をまとめていく。

## LLMの推論と内部理解の必要性

LLM推論とは、GPT-4、Llama 4、DeepSeek-V3などの学習済みLLMを使用して、ユーザーの入力から意味のある出力を生成することを指している。その推論には、たくさんの技術が抽象化・隠蔽されている。APIを利用している場合は、ほぼ意識せず活用できる。しかし、APIを何らかの理由で利用できない場合や、Open WeightなLLMを利用したい場合はこれらの技術を理解する必要がある。

実際、最適化されていない設定では、GPU時間で10倍のコストがかかることもある。ユーザー面であっても、最適化がされていなければ、応答速度が遅くなり、UXが悪化する。

## トークン化

トークンは、LLMがテキストを処理するために使用する言語の最小単位である。トークンは、利用するトークナイザー(Tokenizer)によって、単語、サブワード（単語の一部）などに変換される。

各LLMでは、独自のトークナイザーが使われているため、その内部のアルゴリズムも異なる。例えば、GPT-4oであれば `この記事は iwashi.co に掲載されています。` という文字列は、 `[117391, 5205, 43847, 28926, 10914, 147965, 137149, 196993, 788]` というトークン列に変換される。合計のトークン数は9である。

ちなみにで、gemini 2.5 flashの場合は13トークンになる。この結果から、GPT-4o と gemini 2.5 ではトークナイザーが異なるため、そのままトークンIDを使いまわせないことがわかる。

## 推論の2フェーズ

GPT-4oのようなtransformerベースのモデルの場合、推論プロセス全体が2つに分かれていることを理解しておくと良い。

### プレフィルフェーズ

1つ目のフェーズは、プレフィルである。動作は次のとおりだ。

- （プレフィルの前に）ユーザーが送信したプロンプトを、トークナイザーがトークンのシーケンスに変換する
- ここからプレフィルが始まる
- まず先のトークン（あるいはTokenID）は、LLMが理解できる埋め込みベクトルに変換される。
- 次にそのベクトルは複数のtransformer層を通過する。その際の各層にはSelf Attention機構が含まれている。
    - ここで、各トークンのクエリ（Q）、キー（K）、バリュー（V）ベクトルが計算される。
    - 計算されたベクトルは、トークンが互いにどのように注意を向けるかを決定し、文脈的な意味を保持している
- モデルがプロンプトを処理する際、全層のすべてのトークンのキーとバリューベクトルを保存するKVキャッシュを構築する。
    - このキャッシュが、デコード中の高速検索のための内部メモリとして機能する

重要なのは、プレフィル段階では最初から全てのプロンプトがわかっている点にある（ユーザーがプロンプトを全て書いているのだから当然）。そのため、LLMは高度に並列化された行列演算、特にアテンション計算を通じて、すべてのトークンを同時に処理可能である。これはGPUの得意領域であり、compute-bound な処理になる。その結果、GPUの使用率が飽和する。（ただし、実際の使用率は、シーケンスの長さ、バッチサイズ、ハードウェアの仕様などの要因によって異なる）

このプレフィル、意識しておくべきメトリクスはTime to First Token（TTFT：最初のトークンまでの時間）である。プロンプトを送信してから、最初のトークンが生成されるまでのレイテンシを押さえておく。UXに直結する。

### デコードフェーズ

プレフィルの次に来るのがデコードフェーズである。この段階では、新しいトークンがシーケンシャルに1つずつ生成される。自己回帰的に、前のトークン列から次のトークンを生成して、さらに生成したトークンを使って次に生成する、という動作を繰り返すフェーズとなる。

最後に、生成されたトークンのシーケンスは人間が読めるテキストに復号される。

プレフィルフェーズと比較した時のデコードフェーズの違いは、よりmemory-boundになる点になる。理由は、徐々に大きくなるKVキャッシュから頻繁に読み取りが発生するため。

仮にKVキャッシュを使わないと、全ての計算をやり直す必要がある。たとえば、「今日は良い天気」をプロンプトで入れた時の計算は

- まず、「今日」「は」などのKとVをそれぞれ計算する
- その情報を使って、次の単語を生成する
- さらに、その次の単語を計算するために、再度「今日」「は」などのすべてのKやVを計算する必要がある。

しかし、KVキャッシュがあれば、最後の再計算は不要になる。[^1]

[^1]: Kazuki679740569 さまに[ご指摘](https://x.com/Kazuki679740569/status/1947259412780880103)いただき、記載を修正しています。 

このKVキャッシュの仕組みは、上記のように冗長な計算を回避することで高速化を図る。しかし、キャッシュは生成されたシーケンスの長さとともに増大するため、メモリ消費の増加というコストを支払う必要はある。

デコードフェーズで監視すべき重要な指標は、Inter-Token Latency（ITL：トークン間レイテンシ）である。ITLは、シーケンス内の連続するトークンの生成間の平均時間をを示す。これはTime Per Output Token（TPOT：出力トークンあたりの時間）と呼ばれる。

ここまで説明したプレフィルとデコードは、シンプルなLLMサービングシステムだと、同じハードウェアで実行される。ただし、お互いの特性の違いから、並列に実行できない。その結果トークンレイテンシが長くなってしまう。そのため、プレフィルとデコードを分離する戦略が色々と探求されている。

## API型 vs セルフホスト

LLMを使ったアプリケーションを作る場合は、マネージドAPI型とセルフホスト型の2つに分かれる。それぞれにPros/Consがある。

### API型

OpenAI、Anthropic、GoogleなどのAPI型サービスは、インフラ管理を完全に抽象化しており、ユーザーは従量課金でLLMを利用できる。GPT-4やClaudeのような独自モデルだけでなく、Together AIやFireworksなどのプラットフォームでは、DeepSeek-R1やLlama 4などのオープンソースモデルもAPIとして提供されている。

API型の主な利点は次のとおり。

- APIキーと数行のコードですぐに開始可能
    - その結果、プロトタイプ向けのデモやツール作成に最適
- GPU調達やスケーリングの面倒さを回避（委譲）できる

### セルフホスト型

セルフホスト型は、クラウドGPUやプライベートVPC、オンプレミスで独自のLLMインフラを構築・管理する方式である。モデルのデプロイ、最適化、スケーリングを完全にコントロールできる。

セルフホストの主な利点は次のとおり。

- データプライバシーとコンプライアンス。機密データ（医療記録、財務情報など）を安全に保てる
- 高度なカスタマイズ性
    - レイテンシとスループットのトレードオフ調整
    - プレフィル・デコード分離
    - KVキャッシュ最適化
    - 独自データを利用したファインチューニングによる優位性確保（の可能性）
- 外部APIのレート制限や突然のポリシー変更の影響を受けない

### 比較

どちらを選ぶかは、そのユースケースによって異なる。

| 項目 | サーバーレスAPI | セルフホスト型推論 |
|------|----------------|------------------|
| 使いやすさ | ✅ 良い（シンプルなAPI呼び出し） | ⚠️ 悪い（LLMのデプロイとメンテナンスが必要） |
| データプライバシーとコンプライアンス | ⚠️ 限定的 | ✅ 完全に制御可能 |
| カスタマイズ性 | ⚠️ 限定的 | ✅ 完全な柔軟性 |
| 大規模時のコスト | ⚠️ 高い（使用量ベース、大幅に上昇する可能性） | ✅ 潜在的に低い（予測可能、インフラを最適化できる可能性） |
| ハードウェア管理 | ✅ 抽象化されている | ⚠️ GPUのセットアップとメンテナンスが必要 |

### コスト面での考慮

API型では、トークンあたりのコストは固定だが、使用量に比例して総コストが増大する。プロトタイピングには適しているが、本番環境では高額になることもある。

セルフホスト型では、初期のインフラ構築コストは高いが、スケールするにつれてトークンあたりコストは大幅に低下する。特に推論最適化技術（vLLMやSGLangなど）と組み合わせることで、コスト効率が向上する。

### いつセルフホスト型を使うべきか？

基本的には、API型で始める方が良い。まずプロトタイプを作って、ユースケースやニーズを検証すべきであるため。ただし、パフォーマンス要件や、プライバシー、他者との差別化の重要性が高まるにつれて、セルフホスト型が考慮に入ってくる。

## 意識しておくべきGPUメモリ計算

LLMをサーブする場合に重要なのがGPUのメモリサイズだ。 LLMに関しては以下の2点を意識すると良い。

- モデルサイズ（パラメータ数）。パラメータ数が大きいほど、必要なGPUメモリが異なる。
- bit精度。FP16、FP8などのこと。bit精度が低いほどメモリフットプリントが小さくなるが、出力精度がイマイチになることもある。

必要なメモリサイズはざっくり以下のように計算すると良い。

```
メモリ (GB) = P × (Q ÷ 8) × (1 + オーバーヘッド)

- P：パラメータ数（単位は10億）
- Q：ビット精度（例：16、32）、8で割ることでビットをバイトに変換
- オーバーヘッド（％）：推論中の追加メモリまたは一時的な使用量（例：KVキャッシュ、アクティベーションバッファ、オプティマイザの状態）
```

例えば、20％のオーバーヘッドでFP16の70Bモデルをロードするには、次のように計算すれば良い。

```
必要なGPUメモリサイズ = 70 x (16/8) x 1.2 = 168GB
```

そのため、H100(80GB) x 1枚には当然載らない。そのため、複数GPUでの分散推論が必要となる。あるいは、INT8 や INT4へと量子化する方法もある。

## LLM の量子化

量子化（Quantization）は、高精度フォーマット（FP32）などから、FP8やINT8へと変換して、必要なメモリを削減する & 推論を高速化する技術である。精度とサイズとの間にトレードオフは存在するが、適切に量子化できれば影響は最小限に抑えられる。

### 量子化フォーマット

ざっと以下で捉えておくと良い。

| フォーマット | FP32比サイズ | 精度低下 | 使用例 | メモリ | 備考 |
|------------|-------------|---------|--------|--------|------|
| FP32 | 100% | なし | 訓練 | 高 | 完全精度だが遅い |
| FP16 | 50% | 最小限 | 訓練＆推論 | 中 | ほとんどのLLMの標準 |
| FP8 | 25% | 低 | 訓練＆推論 | 低 | まだ発展途上 |
| int8 | 25% | 低 | 推論 | 低 | 優れた万能トレードオフ |
| int4 | 12.5% | 中程度 | 推論 | かなり低 | GPTQ/AWQなどの手法が必要 |

### いつ量子化を使うべきか

量子化が適している場合は次のとおり。

- 限られたGPUメモリ（例：24GB以下）を持つハードウェアにデプロイする場合
- 推論レイテンシを小さくしたい場合
- LLMのサービングコストを節約したい場合
- 同時実行する数を増やしたい場合
- 小さな精度のトレードオフを許容できる場合

一方で、量子化が適さない場合は次のとおり。

- 可能な限り最高の精度が必要な場合（例：センシティブまたは安全性が重要なタスク）
- モデルがすでに小さい場合
- デプロイ先のハードウェアが量子化フォーマットをサポートしていない場合

### 量子化手法

以下は広く採用されている量子化手法には次のようなものがある。

#### AWQ（Activation-aware Weight Quantization）

AWQは、すべての重みが同等に重要なわけではないという前提に基づいている。実際、重みの約1%が顕著に重要であり、そこに着目する。

実際には、次のようなイメージで量子化する。

- 学習済みのモデルを使って、実際のデータに対する各層の活性化（出力）がどのような値の範囲を取るのか、その統計情報（例えば、最大値や平均値など）を「オフラインで」収集する
- 次に、収集した活性化統計に基づいて、どの重みチャネルがモデルの性能に最も大きな影響を与えるか（つまり、量子化による劣化の影響を最も受けやすいか）を特定する
- 特定された「重要な重みチャネル」に対して、収集した活性化統計を考慮した「スケーリング」を行う
    - スケーリングでは、モデル全体の出力結果を変えないような計算が用いられる
- スケーリングされた重みを、より少ないビット数で表現するように量子化する

#### SmoothQuant

SmoothQuantは、量子化で厄介な「外れ値」問題の対処に焦点を当てている。

次のようなイメージで量子化を行う。

- オフラインで、少量のデータを用いてモデルを実行する。ここで、各層の活性化の統計情報（特に最大値や分布）を収集する
    - これにより、どのチャネルで活性化の外れ値が出やすいかを特定する
- その結果を用いて、最終的な出力結果が変わらないように、重みを変換する

#### GPTQ

まず、PTQとは post-training quantization の略であり、事後学習量子化のことを示す。GPTQはPTQの1種である。

GPTQのコアは、各重みを1つずつ量子化していく際に、その量子化によって生じる誤差を、まだ量子化されていない他の重みを調整することで「補償」していくという点にある。

GPTQの面白い点は、3-4bitなどのかなり小さい精度での量子化を目指している点にある。その結果、例えば175Bのような巨大モデルであってもA100 x 1枚などで動作可能になる。

## 推論フレームワーク

モデルはそれ単体で動くのではなく、以下のような推論フレームワークと併用して使われる。イメージとしては、LLMが「脳みそ」だとすれば、推論フレームワークがそれを実行に移す「体」のような感じ。ただし、体を単に動かすだけじゃなくて、推論速度を高めるための技術や、同時リクエストへの対応など、さまざまな点で拡張されている。

代表的なものを以下に示す。

- vLLM
    - LLMのサービングに最適化された高性能推論エンジン。GPUリソースの効率的な使用と高速なデコーディング能力で知られている
- SGLang
    - LLMとVision LLM向けの高速サービングフレームワーク
- LMDeploy 
    - 高速なデコーディング速度と同時リクエストの効率的な処理に焦点を当てた推論バックエンド
    - 様々な量子化技術がサポートされている
- TensorRT-LLM
    - NVIDIAのTensorRT（高性能深層学習推論ライブラリ）を活用した推論バックエンド
    - NVIDIA製なので、当然のことながらNVIDIA GPU上で大規模モデルを実行するために最適化されている
- Hugging Face TGI
    - LLMのデプロイとサービング用のツールキット
    - Hugging Faceの本番環境で、Hugging Chat、Inference API、Inference Endpointを動かすために使用されている

よりコンシューマに近い環境では、次も候補になる。

- llama.cpp
    - 外部依存関係のない純粋なC/C++で実装された、LLM用の軽量推論ランタイム
    - 名前にllamaとついているが、Llamaモデル以外にも、Qwen、DeepSeek、Mistralなど多くのアーキテクチャをサポートしている
- MLC-LLM
    - LLM用のMLコンパイラおよび高性能デプロイメントエンジン
    - Apache TVMの上で動く。そのため、モデルをサービングする前にコンパイルと重みの変換が必要
    - ハードウェアのサポート対象は幅広い
- Ollama
    - llama.cppの上に構築されたユーザーフレンドリーなローカル推論ツール
    - シンプルさと使いやすさを重視して設計されており、最小限のセットアップですむ。例えばmacbook上でもすぐ動く
    - vLLMやSGLangのようなランタイムとは異なり、同時リクエストはサポートされていない
        - この違いは重要
        - なぜならば、Paged Attentionや、Prefixキャッシュ、動的バッチ（複数のリクエストをまとめて処理する技術）などの多くの推論最適化手法は、複数のリクエストを並列で処理する場合にのみ効果的であるため

結局どれを選べばいいか？　という問いにあたるかもしれないが、全てのシナリオにハマるような単一のランタイム・ツールは存在しない。もし、複数リクエストを扱いたいならvLLMやSGLangが候補になるが、サクッと動かしたいならOllamaで良い。

## 推論メトリクス

すでにいくつか出てきたが、ここでは意識しておくべきメトリクスを整理しておく。

- Time to First Token(TTFT)
    - リクエストを送信してから最初のトークンが生成されるまでの時間。モデルがどれだけ早く応答を生成できるかを表現している
    - UXに関連しており、LLMを分類機のように利用したい場合は、これが小さいほどUXが高まる
- Time per Output Token(TPOT)
    - インタートークンレイテンシ（Inter-Token Latency: ITL）とも呼ばれる
    - 後続のトークンが生成される間の時間のこと
    - TPOTが低いほど、モデルはトークンをより速く生成でき、1秒あたりのトークン数（Tokens per Second: TPS）が高くなる
    - UXに直結する。TTFTがいくら小さくても、TPOTが遅いとUXはかなり厳しい
- Token Generation Time
    - 最初のトークンを受信してから最後のトークンを受信するまでの時間
- Total Latency(E2EL)
    - リクエストを送信してからユーザー側で最終トークンを受信するまでの時間
    - 合計レイテンシは、TTFT + Token Generation Time で計算される

それぞれの時間は短いに越したことはないが、モバイルやWebのアプリと同様で、許容されるレイテンシーはユースケースによって異なる。例えば、リアルタイム対話が必要ならTTFTやTPOTは小さい方がいい。一方で、ドキュメント要約やDeepResearchであれば、即時性よりも正確性が重要になるだろう。

これらの数字は、単一の数値ではなく、平均値、中央値、パーセンタイルなどの指標で追うと良い。この辺のWebアプリの考え方と似ている。平均値だけを追うと、外れ値によって歪みが出る。その意味では中央値は、外れ値に対して耐性がある。

LLMのパフォーマンスベンチマークでは、平均TTFT、中央値TPOT、P99 E2ELなどのメトリクスがよく使われる。

### スループット

LLM自体の実行速度を表すものとしてスループットがある。代表的なものに、Requests per Second (RPS：1秒あたりのリクエスト数)と、Tokens per Second (TPS：1秒あたりのトークン数)がある。

- Requests per Second(RPS)
    - LLMが1秒間に正常に完了できるリクエスト数
    - 1秒あたりのリクエスト数 = 完了したリクエストの総数 / あるタイムフレーム（秒）
- Tokens per Second(TPS)
    - 入力TPS：モデルが1秒間に処理する入力トークンの数
    - 出力TPS：モデルが1秒間に生成する出力トークンの数

## バッチング

GPUは高度に並列化された計算処理のために設計されているため、1秒間に数兆回、あるいは数千兆回もの浮動小数点演算（FLOPs）を実行できる。だがLLMは、チップのメモリ帯域幅の大部分がモデルパラメータの読み込みに費やされるため、これらのGPUの性能を十分に活用できないことがよくある。

バッチんぐはそのボトルネック軽減に役立つ。どうやるかというと、名前の通りまとめて処理する。本番環境では、サービスに複数のリクエストが同時にやってくることがある。各リクエストを個別に処理する代わりに、それらをまとめてバッチとして処理することで、読み込まれた同じモデルパラメータを複数のリクエストで共有する。その結果、スループットを大幅に高められる。

そのバッチングにはいくつかタイプがある。

### 静的バッチング（Static Batching）

サーバーは固定数のリクエストが到着するまで待機し、それらを単一のバッチとしてまとめて処理する。実装が簡単だが、欠点もある。

バッチ内の最初のリクエストは最後のリクエストを待つことを強いられる。その結果、不必要な遅延が発生する。理想的な世界では、これがワークするかもしれないが、
バッチ内のすべてのリクエストが同じように作られているわけではない。実際、LLMの推論では、一部のリクエストは非常に短い応答を生成する一方で、他のリクエストは長い段階的な推論を含む可能性がある。

### 動的バッチング（Dyanmic Batching）

静的バッチングに対応しようとしたもの。

動的バッチングでは、受信リクエストをバッチに収集するが、固定のバッチサイズにこだわらない。その代わりに、一定の時間枠（タイムウィンドウ）を設定し、その時間内に到着したリクエストをまとめて処理する。もし時間枠が経過する前にバッチがサイズの上限に達した場合は、その時点ですぐに処理を開始する。シャトルバスみたいなものを考えるとわかりやすい。乗車する顧客が少なければ定刻通り待つが、満席になったらすぐに出発するようなイメージ。

もちろん欠点がないわけではない。処理開始時にバッチが満杯でない場合もあるため、必ずしもGPUの効率を最大化できるわけではない。また、静的バッチングと同様に、バッチ内で最も時間のかかるリクエストがバッチ全体の終了時間を決定してしまう。その結果、短いリクエストは依然として不必要に待たされることになる。

### 継続的バッチング (Continuous Batching)

LLMの推論では、出力される文章（シーケンス）の長さはリクエストごとに大きく異なる。あるユーザーは簡単な質問をし、また別のユーザーは複雑で長い出力を求めるかもしれない。静的バッチングや動的バッチングでは、短いリクエストが最も長いリクエストの完了を待たざるを得ず、その間GPUのリソースは十分に活用されずに空いてしまう。

この非効率性を解決するのが、継続的バッチング（またはインフライトバッチングとも呼ばれる）である。

継続的バッチングは、バッチ全体が完了するのを待ってから結果を返す、ということはしない。その代わりに、バッチ内の各リクエストが独立して完了することを許容し、処理が終わったものから即座に新しいリクエストと入れ替える。これは、レストランの席のように、空いたらすぐに新しいお客様を案内するようなイメージ。

ここまで挙げてきたvLLM、SGLang、TensorRT-LLM、LMDeploy、Hugging Face TGIなどの主要な推論フレームワークはすべて、継続的バッチング（または同様のメカニズム）に対応している。

## Paged Attention

LLMにおけるアテンション機構を実装する際の、メモリを効率的に使うアプローチである。

LLMが応答を生成している時、生成する各トークンごとに過去の情報（つまりKVキャッシュ）を記憶しておく必要がある。通常、KVキャッシュは1つの巨大な連続したブロックとして保存されるため、メモリの大きな部分を占有してしまう。これは、完全に使い切らない場合でも大きなブロックを予約する必要があるため、メモリのフラグメンテーションやメモリの無駄使いにつながる可能性がある。

Paged Attentionでは、大きな塊を、本のページのような小さなブロック（ページ）に分割する。さらに、このブロックはルックアップテーブルを利用する。（OSの仮想記憶管理とコンセプトは一緒）

PagedAttentionは最初にvLLMによって実装されたが、以降、Hugging Face TGIやTensorRT-LLMなどの他のプロジェクトもPagedAttentionを採用・実装している。

## 投機的デコーディング

高速な「ドラフト（下書き）」モデルと「ターゲットモデル（正確さが求められる）」を組み合わせることで、自己回帰的なトークン生成を高速化する推論最適化手法のこと。

これが有用なのは以下の2つの前提に基づいている。

- 文章の中には、予測が非常に簡単なトークンと、難しいトークンが混在している。簡単な部分は、小さなモデルでも十分に予測可能
- LLMが文章を一つずつ生成していくプロセスにおいて、実は計算能力よりも、メモリからデータを読み書きする速度（メモリ帯域幅）がボトルネックになっている。そのため、GPUなどには、使われずに遊んでいる能力が余っている（投機的デコーディングは、この余剰能力を有効活用したい）

動作は次のようになる。

- ドラフトモデルが入力シーケンスの後の次のKトークンを予測する
- ターゲットモデルがこれらのKトークンを並列で検証し、自分も同じトークンを予測するかを確認する
- ターゲットモデルは、自分が同意するこれらのKトークンの最長のプレフィックス（先頭部分）を受け入れる
- h個のトークンを受け入れた場合、(h+1)番目のトークンを自分で生成する
- このプロセスが繰り返される
    - ドラフトモデルは、この新しく拡張されたシーケンスに基づいて次のKトークンを提案する

ただし、投機的デコーディングには独自のコストがある。ドラフトモデルとターゲットモデルの両方をメモリにロードする必要があるため、全体的なVRAM使用量が増加してしまう。

より実装含めた詳細は、同僚が書いた[先読みを用いたLLMの文章生成の高速化](https://engineers.ntt.com/entry/2023/11/14/081349)があるので、そちらを参照されたい。

## プレフィルとデコードの分離（Prefill-Decode Disaggregation）

冒頭で述べたように、LLMの推論ではフェーズが2つある。だいぶ前なので、ざっくりおさらいを書いておく。

- プレフィル
    - 全体のシーケンスを並列で処理し、アテンション層からのキーベクトルとバリューベクトルをKVキャッシュに保存する
    - すべてのトークンを一度に処理するため、計算負荷はあるが、GPUメモリへの要求はそれほど高くない
- デコード
    - 先に構築したKVキャッシュを再利用しながら、出力トークンを1つずつ生成する
    - プレフィルとは異なり、デコードは高速なメモリアクセスが必要だが、計算負荷は低い

この2つのステップを一緒に実行するのは、単純である。

しかし現実には、複数のリクエスト、しかもニーズの異なるリクエストが同時に到着することがよくある。だが、一度に実行できるフェーズは1つだけである。GPUが計算負荷の高いプレフィルタスクで占有されているとき、デコードタスクは待機しなければならず、これによりITL（Inter-Token Latency：トークン間レイテンシ）が増加する。逆の場合も同様である。

そこで、プレフィルとデコードを分離したい。2つの異なるタスクを分離して、お互いの邪魔をしないようにしたい。そうすれば、次の利点が得られる。

- プレフィルとデコードを異なるハードウェア上で独立してスケジューリングしてスケールできる
    - たとえば、マルチターン会話やエージェント型ワークフローなどが多い場合、KVキャッシュの多くを再利用できる
    - その結果、プレフィルの計算負荷が下がり、デコードにより多くのリソースを割り当てられる
- お互いのフェーズが干渉しなくなるため、効率的に並列で実行できる。（スループットが上がる）
- TTFTとITLを最適化するために、プレフィルとデコードのそれぞれに対して異なる最適化技術（テンソル並列化やパイプライン並列化など）を実装できる

SGLang、vLLM、Dynamo、llm-dなどのオープンソースフレームワークやプロジェクトが、この分離に積極的に取り組んでいる。

ただし、もちろん銀の弾丸ではない。ワークロードが小さかったり、GPUが最適化されていなければ、パフォーマンスは逆に悪化する。また、プロンプトが短い場合や、デコード側で高いプレフィックスキャッシュヒット率が得られる場合は、デコードワーカー上でローカルにプレフィルを実行する方が、多くの場合、より高速でシンプルになる。さらに、当然のことながら、プレフィルワーカーとデコードワーカーの間でKVキャッシュを迅速かつ確実に移動させる必要がある。高速で低遅延な通信プロトコルをサポートするソリューションが不可欠になる。このデータ転送にかかるコストが高いと、かえって全体でパフォーマンスが下がってしまうかもしれない。

## KVキャッシュAwareな負荷分散

従来のWebアプリでは、負荷分散は通常かなりシンプルである。リクエストは小さく、レスポンスは迅速で、どのバックエンドインスタンスでもどのリクエストでも同じように処理できる。ロードバランサーは、ラウンドロビンのような単純な戦略を使ってトラフィックを均等に分散できる。

しかし、LLM推論ではこれが全然異なる。主な理由は、プレフィル段階で使うKVキャッシュである。

従来のロードバランサーは、LLMワーカーを同一のブラックボックスとして扱う。各ワーカー内部で何が起きているかを把握していない。つまり、以下のような情報が見えていない。

- KVキャッシュによってどれだけのGPUメモリが消費されているか
- リクエストキューがどれだけ長いか

ロードバランサーが、上記を意識（Aware）できていなければ、次の問題につながる。

- キャッシュ再利用の機会損失
    - 類似したプレフィックスを持つ新しいリクエストが、既存のキャッシュされた計算結果を活用できない
- レイテンシの増加
    - 間違ったレプリカにルーティングされた会話は、KVキャッシュを失い、コストの高い再計算が必要になる
- 負荷の不均衡
    - 一部のワーカーが多くの長い会話を処理する一方で、他のワーカーはアイドル状態のままになる

そこで、解決に取り組んでいるものもある。例えば、エンドポイントピッカーを使用して、各ワーカーのKVキャッシュ利用率、キューの長さ、LoRAアダプターに関する情報を収集し、より良い推論のためにリクエストを最適なレプリカにルーティングする。

## プレフィックスキャッシング

「KVキャッシュ」という用語は、元々は単一の推論リクエスト内でのキャッシングを指す言葉であった。以前にも述べた通り、LLMはデコードの際、それまでに出力したトークンを基に次の新しいトークンを生成するという自己回帰的な（autoregressive）動作をする。つまり、自身のKVキャッシュを再利用している。このKVキャッシュがなければ、モデルはデコードの各ステップで過去のトークンに関するすべての計算をやり直す必要があり、これはリソースの膨大な無駄遣いになる。

このキャッシングの概念を複数のリクエストをまたいで拡張した場合、それをより正確に表現するのが「プレフィックスキャッシング（prefix caching）」あるいは「プロンプトキャッシング（prompt caching）」である。

この考え方はシンプルだ。ある問い合わせ（クエリ）のKVキャッシュを保存しておくことで、**同じ冒頭部分（プレフィックス）**を共有する新しいクエリが来た際に、プロンプトのその部分の再計算をスキップする。キャッシュされた結果を直接再利用することで、計算負荷を削減し、推論を高速化する。

例えば、次のようなシステムプロンプトを持つチャットボットを考えてみる。

```
あなたは有能なAIライターです。プロフェッショナルな態度で文章を作成してください。
```

このプロンプトは、会話の相手が変わっても、同じである。毎回この部分を再計算する代わりに、そのKVキャッシュを一度だけ保存しておけば良い。そして、ユーザーから新しいメッセージが届いた際には、この保存されたプレフィックスキャッシュを再利用し、プロンプトの新しい部分（ユーザーのメッセージ）だけを処理すれば十分だ。

### プレフィックスキャッシュを認識したルーティング

しかし実際にプレフィックスキャッシングを適用するには、課題もある。

- 新しいリクエストを、適切なプレフィックスをすでにキャッシュしているワーカーに、どのようにしてルーティング（転送）するか？
- ルーターは、各ワーカーのキャッシュに何が入っているかを、どのようにして知るのか？

そこで、OSSのプロジェクトが独自のアプローチを採用している。

- ワーカーが報告するプレフィックスの状態を意識する
    - Dynamoでは、ワーカーが自身がキャッシュしているプレフィックスを積極的に報告する
    - ルーターはこのリアルタイムのデータを使ってルーティングする
- ルーターが予測するキャッシュの状態
    - SGLangでは、過去のリクエスト履歴に基づき、各ワーカーに対応する近似的な基数木（radix tree）をルーター側で維持する
    - これにより、ルーターはワーカーから常に最新情報を受け取らなくても、どのワーカーが必要なプレフィックスを持っている可能性が最も高いかを予測できる
- ハイブリッドな取り組み
    - Gateway API Inference Extensionプロジェクトは、EPP（エンドポイントピッカー）上でルーティングアルゴリズムを実装するために、複数の戦略を用いる
        - Prefix affinity consistent hashing（プレフィックスの類似性に基づいたコンシステントハッシュ法）
            - 似たプレフィックスを持つリクエストを同じワーカーにグループ化する
        - ルーター上の近似プレフィックスキャッシュ
            - ルーターが、すべてのバックエンドサーバー上のプレフィックスキャッシュの近似的なルックアップキャッシュを保持する
        - ルーター上の正確なプレフィックスキャッシュ
            - モデルサーバーから報告されたKVキャッシュ情報を収集する
- llm-dは、Inference Schedulerというコンポーネントを使用してフィルタリングとスコアリングアルゴリズムを実装し、キャッシュの可用性、プリフィル/デコードステータス、SLA、負荷などの要因の組み合わせに基づいてルーティングを決めている

## 並列

推論であれ、学習であれ、巨大な情報量を扱うLLMではさまざまな並列化手法が利用される。以下で簡単に紹介する。

### データ並列

データ並列は計算を高速化するための一般的な手法である。

このアプローチでは、モデルの重みを複数のGPUデバイス間で複製し、グローバルなバッチの入力データをより小さなマイクロバッチに分割する。各デバイスは自分に割り当てられたマイクロバッチのみを処理し、このプロセスがすべてのデバイスで並行して実行される。

```
元のバッチ：[━━━━━━━━━━━━━━━━] (16サンプル)
            ↓ 4つのGPUに分割
分割後：
GPU1: [━━━━] (4サンプル)
GPU2: [━━━━] (4サンプル)
GPU3: [━━━━] (4サンプル)
GPU4: [━━━━] (4サンプル)
```

### テンソル並列

テンソル並列は、モデルの個々の層をより小さなブロックにスライスする手法である。スライスされたブロックは独立した異なるデバイス間で並行計算される。例えば、行列乗算であれば、行列の異なるスライスを複数のGPUで同時に処理できる。

このアプローチのメリットは、高速化だけではなく、単一デバイスのメモリに収まらないLLMの推論を可能にする点にある。ただし、デバイス間で追加の通信が発生するため、この通信オーバーヘッドとパフォーマンス向上のバランスを取る必要がある。

### パイプライン並列

パイプライン並列は、モデルの層を連続したいくつかの塊（チャンク）に分割し、それぞれを別々のデバイスに割り当てる。データはこれらのチャンクを「組み立てライン」のように流れ、あるデバイスの出力が次のデバイスの入力となる。例えば、4分割のパイプライン並列では、各デバイスがモデル全体の層の4分の1ずつを処理する。

しかし、各デバイスは前のデバイスの出力に依存するため、一部のデバイスが待機状態になる時間（バブルとも呼ばれる）が発生し、リソースの非効率な利用につながる。この待機時間を削減するために、入力バッチをさらに小さなマイクロバッチに分割する手法がよく用いられる。各マイクロバッチが次々とパイプラインを流れることで、GPUの利用率は向上するが、アイドル時間を完全にゼロにすることはできない。

なお、注意点として、パイプラインの各ステージ間で通信が発生するため、リクエストごとの合計レイテンシは増加する可能性がある。

### 補足：テンソル並列とパイプライン並列の違い

テンソル並列とパイプライン並列は、分割の仕方が根本的に異なる。テンソル並列は、層を複数に分割する。

```
元の層：[━━━━━━━━━━━━━━━━]
分割後：[━━━━][━━━━][━━━━][━━━━]
        GPU1  GPU2  GPU3  GPU4
```

一方で、パイプライン並列では、工程を分割する。

```
元のモデル：層1→層2→層3→層4→層5→層6→層7→層8→層9→層10→層11→層12
分割後：   [層1-4]    →    [層5-8]    →    [層9-12]
           GPU1            GPU2            GPU3
```

rebuild の hak さんの真似ると、パイプライン並列は説明しやすくて、

- 職人A（GPU1）: ひたすらシャリを握る
- 職人B（GPU2）: シャリにワサビを乗せる
- 職人C（GPU3）: ネタを乗せる
- 職人D（GPU4）: 最後に皿に盛り付けて出す

のように工程で割るイメージ。

### エキスパート並列

エキスパート並列は、MoE（Mixture of Experts）モデルで使われる特殊な並列処理戦略である。

MoEモデルでは、入力されるトークンごとに、モデルの中の一部の「エキスパート」（専門家のような小さなニューラルネットワーク）のみが活性化される。エキスパート並列では、すべてのエキスパートを各デバイスに複製するのではなく、エキスパート自体を異なるデバイスに分割して配置する。

つまり、各GPUは、すべてではなく一部のエキスパートの重み全体を保持する。これにより、各GPUは、そのGPU上に格納されているエキスパートに割り当てられたトークンのみを処理するようになる。

### ハイブリッド並列

ここまで述べた並列手法は、1つだけ使うのではなく複数使われることがある。ハイブリッド並列はまさに組み合わせた手法となる。

典型的なハイブリッド手法は次のようになる。

- もし、8つのGPUがある場合、最初の4つのGPUにテンソル並列（TP=4）を適用し、残りのGPUにデータ並列（DP=2）を使う

ただし、これは可能な組み合わせの一つに過ぎず、それぞれに利点と欠点がある。上記の例では、テンソル並列はGPU間、特に推論中の通信オーバーヘッドを発生させる。そのため、高いTP度を使用することが必ずしもより良いパフォーマンスに繋がるとは限らない。

他にも、テンソル並列を減らしてデータ並列を増やす構成もある。例えば、TP=2、DP=4に設定する。これにより、GPU間の通信が削減され、推論時のレイテンシの低減にもつながる（可能性がある）。

ただし、落とし穴もある。モデルの重みはGPUメモリの大部分を消費する。特に大きなモデルの場合はそうである。テンソル並列を少なくすると、モデルを共有するGPUが少なくなる。そのため、KVキャッシュのための領域が少なくなる。これにより、プレフィックスキャッシングなどの推論最適化が悪化する可能性がある。

これらのトレードオフは、テンソル並列とデータ並列に固有のものではない。ハイブリッド並列計画を設計する際には、特定のモデルサイズ、ハードウェア設定、推論要件に基づいて異なる構成をベンチマークすることが重要である。銀の弾丸は存在しない。最適な戦略は、チューニングと実験を通じて見つけ出される。

## インフラ面での高速スケーリング

本番環境でLLMの推論は、モデルのトレーニングとは全くの別物である。学習が予測可能でバッチングを基本とするのに対し、推論はリアルタイムのユーザー需要に基づいて実施される。多くの場合、トラフィックは突発的であり予測が難しく、レイテンシーの増加やダウンタイムが許されない。

トラフィックの急増時には迅速にスケールアップ/アウトし、アイドル時にはコスト削減のためにゼロまでスケールダウンする必要がある。クラウドと同じく、弾力性が重要になる。

### コールドスタート問題

スケーリングの重要な問題が、コールドスタート問題である。

LLMをコンテナでデプロイするのであれば、あるKubernetesノードが特定のデプロイメントを一度も実行したことがない場合にこの問題が発生する。コンテナイメージがローカルにキャッシュされておらず、すべてのイメージレイヤーをゼロからプルして初期化しなければならない。

実際には、さらに細分化して次のように問題が表出する。

- クラウドを利用している場合、クラウドプロバイダーが新しいインスタンスを割り当て、それをKubernetesクラスタに接続するまでにかかる時間がかかる。インスタンスの種類や空き状況によっては、30秒から数分、Nvidia A100やH100のような需要の高いGPUの場合は数時間かかることさえある
- 同様に、LLMのイメージは、多数の依存関係とカスタムライブラリのため、一般的なPythonジョブイメージよりもはるかに大きく複雑となる。クラウドプロバイダーが複数ギガビット帯域の帯域をスペック上は記載していても、実際のイメージダウンロード速度ははるかに遅いことが多い。その結果、イメージのプルには3〜5分かかることがある
- モデルのロードに必要な時間は、そのサイズに大きく依存する。LLMは数十億のパラメータがあるため、レイテンシが増加する。
    - Hugging Faceのようなプラットフォームは、高スループットのマルチパートダウンロードに最適化されていないため、大きなモデルファイルの取得に時間がかかる
    - 推論を開始する前に、モデルファイルを完全にダウンロードしてディスクに書き込む必要がある。これにより追加のI/O操作が発生し、起動が遅延する

じゃあ、どうするかというと、たとえば次のような方法がある。

- オブジェクトストレージの利用
    - マルチパート並列処理により帯域幅をフル活用できる
- FUSEの利用
    - CPU boundな展開処理とディスクI/Oを完全回避
    - ちなみに、FUSEは、Filesystem in Userspaceであり、カーネル空間ではなくユーザー空間でファイルシステムを実装できるLinuxカーネルモジュールのこと
- ゼロコピーGPUロード
    - モデルウェイトをコンテナイメージから分離
    - リモートストレージから直接GPU VRAMへストリーミングする

モデルの重みをコンテナに書き込むかどうかで分岐があるが、そもそもコンテナストレージよりもオブジェクトストレージの方が早い。

### メトリクス

スケール要否を判断するメトリクスには以下がある。

- CPU利用率
    - シンプルで閾値も明確だが、Pythonベースのワークロードの実際の負荷を反映しているわけではない
- GPU利用率
    - 理論上はCPUより関連性の高いメトリクスだが、実際には不正確
    - `nvml` のようなツールは、サンプリング期間中にほんのわずかでもカーネルが実行されればGPUを「使用中」として報告してしまう
    - その結果、早すぎるスケールアップや、キャパシティに対する誤った安心感につながることがある
- QPS (1秒あたりのクエリ数、query per second)
    - 従来のWebサービスで広く使われているが、LLM推論ではあまり役に立たない
        - なぜならば生成AIへのリクエストは、入力の長さや生成されるトークン数によって、サイズや計算コストが大きく異なるため
    - その結果、QPSには一貫性がなく、オートスケーリングの調整には不向き
- 同時実行数
    - キューの中に入っているか、あるいは処理中のアクティブなリクエスト数を表すこのメトリクスは、システム負荷を反映する理想的な指標となる
    - 同時実行数はバッチサイズに基づいて簡単に設定できる
        - 実際のシステム需要と直接相関するため、正確なスケーリングに使える
    - ただし、同時実行数が機能するためには、フレームワークが自動的に同時実行数をメトリクスとして計測しており、かつデプロイしているプラットフォームへのスケーリングシグナルとして情報を与える必要がある

## 推論インフラの構築・運用コスト

LLM推論インフラの構築は、単なる技術的なタスクではない。多大なコストと時間がかかる。本気が必要。

### どれぐらい複雑か？

LLMの推論は、標準的なクラウドネイティブの技術スタックよりも遥かに多くが必要となる。例えば、以下を意識する必要がある。

- 高性能GPUのプロビジョニング
- CUDAのバージョン互換性やドライバの依存関係の管理
- オートスケーリング、同時実行数制御、スケールトゥゼロ（アイドル時にリソースをゼロにする挙動）の設定
- GPUモニタリング、リクエストのトレーシング、障害検知のためのObservabilityツールのセットアップ
- ストリーミング、キャッシング、ルーティングといったモデル固有の挙動への対応

これらのステップは、どれ一つとして簡単なものではない。こういった要求を汎用のインフラに無理やり当てはめようとしても、パフォーマンスの低下と開発期間の長期化を招くだけ。

たとえチームがそれをやり遂げたとしても、インフラのセットアップに費やした毎週の時間は、モデルを改善したり、製品価値を提供したりするために使われなかった時間になる。高いパフォーマンスを求められるAIチームにとって、この機会損失は、インフラの請求書と同じくらい現実的なコストになる。

### MLツールとフレームワークの柔軟性の制限

多くのAI技術スタックは、モデルのランタイム（PyTorch, vLLM, 特定のTransformerなど）のバージョンを固定する。その主な理由は、コンテナイメージをキャッシュし、インフラ関連コンポーネントとの互換性を確保するためだ。これはクラスタへのデプロイを簡素化する一方で、新しいモデルやフレームワークをテスト・デプロイしたい場合に、柔軟性が失われる。

つまり、以下の制約が生じる。

- 新しいモデルやフレームワークのバージョンを簡単にテスト・デプロイできない
- 自社のスタックがコミュニティやベンダーのアップデートから乖離するにつれて、より多くの技術的負債を抱え込むことになる
- LLMのデプロイ速度が低下し、チームが競争上の不利な立場に置かれる

### 複雑なAIシステムへの対応

LLMは、それ単体では価値を生み出さない。多くの場合、以下のような要素も必要になる。

- ユーザー入力を整形・変換するための前処理
- モデルの出力をフロントエンドで使えるようにフォーマットする後処理
- モデルをロジック、パイプライン、制御フローでラップする推論コード
- バリデーション、ルール、内部データ連携を処理するビジネスロジック
- データベースや、特徴量を一元的に管理、共有、提供するための専門的なデータ基盤に接続するためのコネクター
- RAGやアンサンブルパイプラインのための複数モデルの組み合わせ
- 他のチームが使いやすい形でサービスを公開するためのカスタムAPI

実際、ほとんどのLLMデプロイツールは、上記を考慮して作られていない。モデルの重みを読み込み、基本的なAPIを公開するように設計されているだけである。

そのため、一定以上に複雑なことをしようとすると、「グルーコード」やアドホックな対応策、あるいはロジックを複数のサービスに分割するといった対応が必要になる。その結果、次のような事態に陥る。

- 使える機能を提供するだけで、エンジニアリング工数がたくさんかかる
- 開発者体験が悪化する
- ツールがユースケース固有のカスタマイズに対応していない場合、新規価値が作れない

### 人材の希少性

LLMインフラは、深い専門知識を必要とする。

企業は、GPU、Kubernetes、MLフレームワーク、そして分散システムをすべて一人の役割として理解しているエンジニアを必要するが、このような専門家は希少である。人件費も通常は高額になる。（従来のDevOpsエンジニアよりも高い）

## LLMのオブザーバビリティ

LLMの推論を本番環境で運用するには、単にモデルが応答を返すだけでは不十分である。システムがすべてのレベルでどのように動作しているかを、完全に可視化する必要がある。オブザーバビリティがなければ、レイテンシーの問題、スケーリングの課題、あるいはGPUの低利用率といった問題を、雑に測することになる。

効果的なオブザーバビリティを実現するには、LLMの推論ワークロード特有の要求に合わせてカスタマイズされた、適切なメトリクス、ダッシュボード、ログ、イベントストリームが必要になる。

- コンテナ & デプロイメント
    - Podのステータス
        - 障害が発生した、スタックした、あるいは再起動中のPodを、可用性に影響が出る前に検知
    - レプリカ数
        - オートスケーリングの挙動に関連。スケーリングの遅延や上限に関する問題のトラブルシューティングに役立つ
- アプリのパフォーマンス
    - 秒間リクエスト数（RPS）
        - 流入するトラフィックとシステムの負荷を測定し
    - リクエストのレイテンシー
        - 応答の遅延やボトルネックの特定に役立つ
    - 処理中のリクエスト数
        - 同時実行数を示す。アプリが需要に追いついているかを把握するのに有用
    - エラー率
        - 失敗した、または無効な応答の割合。SLA監視に
    - キューの待機時間
        - 利用可能なレプリカを待つことによって生じる遅延の把握に
- クラスターリソース
    - リソースのクオータとリミット
        - リソース使用量の上限をトラックする。リクエスト/リミット値の調整や、過剰/過小なリソース割り当ての回避に
- LLM固有のメトリクス
    - Token per Second
        - モデルのスループットとパフォーマンス効率を反映
    - TTFT
        - UXに影響。ストリーミングやチャットのような体験では極めて重要
    - Token Generation Time
        - 完全な応答を生成するまでのエンドツーエンドのパフォーマンスを測定
- GPUメトリクス
    - GPU使用率
        - GPUがどれだけビジー状態かを示す。低すぎる場合は、リソースの未使用やバッチングが非効率である可能性を示唆している
    - GPUメモリ使用量
        - キャパシティプランニングや、OOMエラーの回避に有用

## InferenceOps

InferenceOpsとは、LLMの継続的デプロイメント・更新・管理をサポートする実践とワークフローのことを示す。

まず、すべての本番LLMアプリケーションは、明確で再現性のあるデプロイプロセスから始めるべき。後々の緊急対応を避け、チームのどのエンジニアでも安全に変更をリリースできるようにするために役立つ。

さらに、従来のアプリケーションと同様に、モデルも自動的にパッケージ化、テスト、デプロイされるべき。モデルのリリース戦略も従来戦略が使える。つまり、カナリアリリースやブルーグリーンデプロイができる。

ある程度、自動パイプラインを作れたとしても、数個のモデルで機能する方法は、モデルが数十、数百に増えると、たちまち破綻する。特に、チーム、クラウド環境、ユースケースが多岐にわたる場合はなおさら。そこで、モデルレジストリやライフサイクルを一元把握できるようにする。

## まとめ

かなり長くなってしまったけど、これぐらいを意識しておくと、LLMの推論を効果的にサーブできそう。