---
layout: post
title: WebRTCのSDP typeにおけるpranswerとは
description: WebRTCのSDP typeにおけるpranswerとは
tags: [WebRTC, 解説, 学習記録]
ogp: /assets/images/ogp/2016-04-03-webrtc-pranswer_ogp.png
---

## はじめに

WebRTCではSDPを示すオブジェクトとして、RTCSessionDescriptionが利用される。RTCSessionDescriptionにはいくつかのタイプがあり、通常利用するのが"offer"と"answer"だ。実はあまり知られていないが、UXを向上させるための手段として"pranswer"というタイプもある。

私の知る限り、日本語で言及されている情報は見つからなかったので、本記事にて"pranswer"について解説する。

### 本記事の概要、読むと得られるもの

- "pranswer"とは？なぜ必要なのか？
- JavaScriptからどうやったら使えるのか？

### 対象読者

- WebRTCのクライアントサイドを開発しているエンジニア
- SDPについて多少なりとも知識がある人

では本題。

<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- iwashico_middle -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4737755123993145"
     data-ad-slot="6593095118"
     data-ad-format="auto"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>

## pranswerとは？

まず、pranswerとはProvisional Answerの略だ。Provisionalとは"暫定的な"と捉えると良い。最終的に確定したAnswerの前に用いるAnswerのことを、Provisional Answerと呼ぶ。別にChrome限定の裏メニューでもなんでもなくて、W3Cの仕様にも、IETFの仕様にも規定されている。たとえば、IETF側の仕様である[JSEP](http://tools.ietf.org/html/draft-ietf-rtcweb-jsep-14)から一部の図を抜粋すると以下になる。

```
                       setRemote(OFFER)               setLocal(PRANSWER)
                           /-----\                               /-----\
                           |     |                               |     |
                           v     |                               v     |
            +---------------+    |                +---------------+    |
            |               |----/                |               |----/
            |               | setLocal(PRANSWER)  |               |
            |  Remote-Offer |------------------- >| Local-Pranswer|
            |               |                     |               |
            |               |                     |               |
            +---------------+                     +---------------+
                 ^   |                                   |
                 |   | setLocal(ANSWER)                  |
   setRemote(OFFER)  |                                   |
                 |   V                  setLocal(ANSWER) |
            +---------------+                            |
            |               |                            |
            |               |<---------------------------+
            |    Stable     |
            |               |<---------------------------+
            |               |                            |
            +---------------+          setRemote(ANSWER) |
                 ^   |                                   |
                 |   | setLocal(OFFER)                   |
   setRemote(ANSWER) |                                   |
                 |   V                                   |
            +---------------+                     +---------------+
            |               |                     |               |
            |               | setRemote(PRANSWER) |               |
            |  Local-Offer  |------------------- >|Remote-Pranswer|
            |               |                     |               |
            |               |----\                |               |----\
            +---------------+    |                +---------------+    |
                           ^     |                               ^     |
                           |     |                               |     |
                           \-----/                               \-----/
                       setLocal(OFFER)               setRemote(PRANSWER)
```

PRANSWERの文字がいくつかの箇所で見えると思う。注目すべきは状態遷移で、LocalにしろRemoteにしろPRAnswerを設定した後は、PRAnswerを保持した状態になり、その後PR無しのAnswerをsetするとStableになる点だ。

## これを使うと何が嬉しいのか？（なぜ必要なのか？）

かなりニッチなユースケースだが、こんなアプリを作りこむときに役立つ。

- 前提：1:1のビデオチャットをする
- 処理の流れ
  1. 通信は自動的に応答するのではなくて、受信側に「応答可否」を確認するダイアログが出る
  2. OKであれば「応答」ボタンを押して接続を開始する

このとき、pranswerを使うと[1]の段階で、音声映像のトラフィックは送受信しないものの、DTLSの確立・ICEによるP2P/TURN経由の接続確立を裏で済ませることができる。そして[2]で、実際にユーザが「応答」ボタンを押したときにトラフィックの送受信を開始する。（DTLSおよびICEの処理は完了しているので、接続までの時間が非常に早いのがポイント）

個人的な意見の補足：ここまで頑張って接続時間を早くしようというアプリケーションは少ない気がするが、1つの手として知っておくのには役立つと思われる

## やりかた

`createAnswer()` を読んでSDPのオブジェク卜を取得できたら、中身をちょっとだけ変えてあげるだけで良い。具体的にはこんな感じ：

```js
  peerConnection.createAnswer( (description) => {
    description.sdp = description.sdp.replace(/a=sendrecv/g, 'a=inactive');
    description.type = 'pranswer';
  }, (error) => {});
```

短いコードだがポイントは2点：

1. `a=sendrecv` のように記載される方向属性を `a=inactive` に書き換えてあげること。これによってメディアのトラフィックは送受信されなくなる。
2. typeに `pranswer` を設定してあげること

これでpranswerを利用できる。

## まとめ

本記事では、WebRTCにおけるpranswerの必要性、その利用方法について解説を行った。
