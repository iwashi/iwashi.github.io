---
layout: post
title: ORTCについてそろそろ書いてみる
description: ORTC and WebRTC
category: null
tags: []
ogp: /assets/images/ogp/2015-08-13-ortc-and-webrtc_ogp.png
---

## 1. はじめに

WebRTCの動向を追いかけている人であれば、ORTCについて耳にしたことがあると思う。

だが、ORTCの登場背景等について、記載した日本語記事があまりなかったので、
私の知る範囲で、以下にまとめておこうと思う。

(ORTCを当初から追いかけているわけではないので、間違っていたら[@iwashi86](https://twitter.com/iwashi86)までご指摘ください。非常に歓迎です！)

## 1.1. 本記事の対象者

- WebRTCについてある程度知識がある人向け
  - SDP何それ？な人は、[HTML5Rocks](http://www.html5rocks.com/en/tutorials/webrtc/infrastructure/?redirect_from_locale=ja)あたりを読んでから、以降を読むと分かりやすいと思う

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

## 2. なぜORTCが登場したのか？

### 2.1. WebRTC 1.0の世界

既存のWebRTC(まだ、仕様として固まっていないが、以降では分かりやすくWebRTC1.0と呼ぶ)において、
シグナリングプロトコルは規定されていない。これは次の[JSEPのドラフト](http://tools.ietf.org/html/draft-ietf-rtcweb-jsep-11)からも確認できる。

```
    The thinking behind WebRTC call setup has been to fully specify and
    control the media plane, but to leave the signaling plane up to the
    application as much as possible
```


JSEPでは、実際のシグナリング方法は規定していないものの、WebアプリとブラウザのIFは規定されている。
具体的には、そのIFとしてSDPが使われている。


```
       +-----------+                               +-----------+
       |  Web App  |<--- App-Specific Signaling -->|  Web App  |
       +-----------+                               +-----------+
             ^                                            ^
             |  SDP                                       |  SDP
             V                                            V
       +-----------+                                +-----------+
       |  Browser  |<----------- Media ------------>|  Browser  |
       +-----------+                                +-----------+
```

SDPの中身を確認すると、多くのWebデベロッパは辟易するはずだ。
なぜなら、SDPはテキストフォーマットで記述されているものの、その内容はひどく難解だからだ。

#### 一瞬脱線

Webデベロッパにとって、SDPはあまりにも読むのが辛いと思われるので、ミニマムな知識・読み方を、WebRTC Meetup Tokyo#7 で述べた。少しでもSDPの知識を仕入れたい人は参考にしていただきたい。

<iframe src="//www.slideshare.net/slideshow/embed_code/key/4hU60WFXyN1WTk" width="425" height="355" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" allowfullscreen> </iframe> <div style="margin-bottom:5px"> <strong> <a href="//www.slideshare.net/iwashi86/20150311-web-rtcmeetup7sdp" title="SDP for WebRTC - From Basics to Maniacs -" target="_blank">SDP for WebRTC - From Basics to Maniacs -</a> </strong> from <strong><a href="//www.slideshare.net/iwashi86" target="_blank">iwashi86</a></strong> </div>

### 2.2 SDPの修正が面倒

SDPは既にRTCの世界で実績がある点は良かったが、
JavaScriptからさわろうとすると、Parserが必要だったりしてかなり面倒だ。
この点がWebRTC1.0のイケてない点の1つだ。

### 2.3. 不要なネゴシエーション

また、SDPはオファーアンサー型のプロトコルとも言える。
オファーアンサーの動作では、

- オファー側が、「XXとYYが使えるよ」と提案
- アンサー側が、「YYなら使えるよ」と承諾

のようにして、通信に使うプロトコルをネゴシエーションする。
ポイントは、オファーとアンサーの両方が必要なところだ。

これは、別に完全に悪いわけじゃない。
黒電話からはじまった世界のように、互いが発話(sendrecv)するような
1:1のコミュニケーションにおいては、
オファーアンサー型のプロトコルは必須だ。

しかし、WebRTCのユースケースは、双方が発話すると限ったわけではない。
例えば、監視カメラの通信スタックにWebRTCを利用するようなケースを考えて欲しい。
このとき、ユーザが確認したいのは監視カメラの映像だけであり、
ユーザから監視カメラに音声や映像を送りたいわけではない。
(カメラを動かしたりしたいかもしれないが、それはWebRTCじゃなくて別の制御プレーンでやればいい話)

このようなユースケースにおいては、
オファーアンサーのアンサーは冗長だったりする。
なぜならば、ユーザは監視カメラから届くメディア条件さえ分かっていれば、
メディアを解読できるからだ。

### 2.4. 多重化の扱いが面倒、MultiStreamも面倒

SDPで、音声・映像の両方を扱おうとした場合、
拡張無しで扱おうとすると、``m=audio``と``m=video``行を分けて記述し、
異なるポート番号を用いてRTPを送受信する。

しかし、WebRTCでは、NAT越えの容易さ等を考慮して、
音声・映像を多重化して送信する。
そのために、SDPを拡張したRFCがいくつか存在する。例は[sdp bundle](https://datatracker.ietf.org/doc/draft-ietf-mmusic-sdp-bundle-negotiation/)とか。

上記は音声・映像の多重化の話だが、
映像が複数あるようなケースもある。(カメラが2つある場合等)
この場合、どのようにして映像2つ分の情報を表現すれば良いか？
これに関しては仕様・実装ともに割れていて

- [Plan B](https://tools.ietf.org/html/draft-uberti-rtcweb-plan-00)
  - Chromeで実装、でもやがてUnified Planになる
- [Unified Plan](https://tools.ietf.org/html/draft-roach-mmusic-unified-plan-00)
  - Firefoxで実装、こっちが本命

となっている。(これについてはまた別途書きたい)

おまけに、createOffer APIは粒度の細かい操作ができない。
例えば、track単位で扱うことができなかったりする。

### 2.5. Multipartyもやっぱり面倒

[webrtchacks.com](https://webrtchacks.com/why-the-webrtc-api-has-it-wrong-interview-with-webrtc-object-api-ortc-co-author-inaki-baz-3-2/)で言及されているけど、完全に解釈できてないので略。

### 2.6. まとめ

つまり、SDPはイケてない。
Hi-LevelなAPIで抽象化するのは良いが、もっとLow-LevelなAPIでRTCを制御したい。
（Extensible Webな流れと一緒）

## 3. ORTCの世界

前述したような問題点を解消すべくORTCが登場した。
ORTCでは、そもそもAPIの切り方がほとんど異なる。
スタックの全体像は以下の通りだ。

![ORTCの全体像](http://ortc.org/wp-content/uploads/2014/08/ortc-big-picture.png)

これまでブラウザに隠蔽されていたlow-levelな部分が解放されることになり、
JavaScriptとブラウザ内に存在するWebRTCスタックとのやりとりはSDPである必要がなくなる。（APIを直接叩くようになる）
これは、とても大事なことなので言い換えておくと、SDPの呪縛から解放されるということだ。

個々のAPI詳細は[SPEC](http://ortc.org/wp-content/uploads/2015/06/ortc.html)に譲るが、理解のために2つほどAPI例を紹介する。

### 音声・映像の送信例

音声・映像の送受信のAPIとして、RTCRtpSender/Receiverが用意されている。(実は、WebRTC1.0にも取り込まれはじめていて、例えばFirefoxは[こちら](https://bugzilla.mozilla.org/show_bug.cgi?id=1032835)から)

```
interface RTCRtpSender : RTCStatsProvider {
    readonly    attribute MediaStreamTrack track;
    readonly    attribute RTCDtlsTransport transport;
    readonly    attribute RTCDtlsTransport rtcpTransport;
    void                      setTransport (RTCDtlsTransport transport, optional RTCDtlsTransport rtcpTransport);
    Promise                   setTrack (MediaStreamTrack track);
    static RTCRtpCapabilities getCapabilities (optional DOMString kind);
    void                      send (RTCRtpParameters parameters);
    void                      stop ();
                attribute EventHandler?    onerror;
                attribute EventHandler?    onssrcconflict;
};
```

```
interface RTCRtpReceiver : RTCStatsProvider {
    readonly    attribute MediaStreamTrack? track;
    readonly    attribute RTCDtlsTransport  transport;
    readonly    attribute RTCDtlsTransport  rtcpTransport;
    void                      setTransport (RTCDtlsTransport transport, optional RTCDtlsTransport rtcpTransport);
    static RTCRtpCapabilities getCapabilities (optional DOMString kind);
    void                      receive (RTCRtpParameters parameters);
    void                      stop ();
                attribute EventHandler?     onerror;
};
```

これを利用して音声・映像を送信するexampleコードは以下の通りであり、なんとなくORTCニュアンスが読み取っていただけると思う。(draftから引用)

```
function myInitiate(mySignaller, transport, audioTrack, videoTrack) {
  var audioSender = new RTCRtpSender(audioTrack, transport);
  var videoSender = new RTCRtpSender(videoTrack, transport);
  var audioReceiver = new RTCRtpReceiver(transport);
  var videoReceiver = new RTCRtpReceiver(transport);

// Retrieve the audio and video receiver capabilities
  var recvAudioCaps = RTCRtpReceiver.getCapabilities("audio");
  var recvVideoCaps = RTCRtpReceiver.getCapabilities("video");
// Retrieve the audio and video sender capabilities
  var sendAudioCaps = RTCRtpSender.getCapabilities("audio");
  var sendVideoCaps = RTCRtpSender.getCapabilities("video");

  mySignaller.myOfferTracks({
    // The initiator offers its receiver and sender capabilities.
    "recvAudioCaps": recvAudioCaps,
    "recvVideoCaps": recvVideoCaps,
    "sendAudioCaps": sendAudioCaps,
    "sendVideoCaps": sendVideoCaps
  }, function(answer) {
    // The responder answers with its receiver capabilities

    // Derive the send and receive parameters
    var audioSendParams = myCapsToSendParams(sendAudioCaps, answer.recvAudioCaps);
    var videoSendParams = myCapsToSendParams(sendVideoCaps, answer.recvVideoCaps);
    var audioRecvParams = myCapsToRecvParams(recvAudioCaps, answer.sendAudioCaps);
    var videoRecvParams = myCapsToRecvParams(recvVideoCaps, answer.sendVideoCaps);
    audioSender.send(audioSendParams);
    videoSender.send(videoSendParams);
    audioReceiver.receive(audioRecvParams);
    videoReceiver.receive(videoRecvParams);

    // Now we can render/play
    // audioReceiver.track and videoReceiver.track.
  });
}
```

mySignallerがシグナリング経路であり、
オファー側の能力とアンサー側の能力をネゴシエーションしている。
ストリームを増やす場合は、RTCRtpSender/Receiverが増えることになる。

### 特徴的なもう一つのAPI: RTCRtpListener

以下のAPIをご覧いただきたい。

```
interface RTCRtpListener {
    readonly    attribute RTCDtlsTransport transport;
                attribute EventHandler?    onunhandledrtp;
};
```

onunhandledrtpという属性がある。
これは、受信者が解釈できないRTPを受信したときに発火するもので、
上手く使えば、余計なシグナリングを減らすことができる。

## 4. ORTCの注意点

ORTCの注意点・誤解されそうな点・疑問にあがりそうな点をいくつか述べる。

### 4.1. SDPはしばらく死なない

過渡期には、WebRTC 1.0とORTCが併存することになる。
WebRTC1.0のブラウザは当然のことながら、SDPしか話すことができないため、
何らかの対処をしなければ、ORTCとWebRTC1.0の相互接続性が失われてしまう。　

では、どうすればよいか？
ORTCはよりLow-LevelなAPIを提供しているため、ORTCで提供される
JSON形式の各種パラメータはSDPに変換することができる。

このSDPへの変換はJS側のshimで実現しても良いし、
B2BUAのような動作をするシグナリングサーバで実現しても良い。

### 4.2. オファーアンサーが無くなるわけではない

前述の例で示したとおり、送受信が発生するようなケースでは、
お互いのコーデック等のネゴシエーションは必須になる。
そのため、オファーアンサーが完全に無くなるわけではない。

### 4.3. WebRTC 1.0向けのライブラリ(ex. peerjs)はどうなるの？

ORTC時代になったら書き換えないといけない。

### 4.4. プロトコルスタックって変わるの？

ICEもDTLSもSRTP/SRTCPも変わらない。WebRTCを深く理解したい場合は、各種プロトコルの仕様を理解すること。

### 4.5. 開発は楽になるの？

ORTCではより低レイヤのAPIが提供されるため、生のAPIをさわろうとすると
今のWebRTCより大変になる。(今のWebRTCですら生のAPIを使うのは結構大変)
例えば、WebデベロッパがDTLSのトランスポートを扱わないといけない。

将来的には、WebRTC1.0の時代同様に、
いくつものライブラリが出てくるようになると思う。

## 5. まとめ

- ORTCはWebRTC1.0の苦しい点を解決しようとしている
  - 例えばSDPの呪縛からの解放
- ORTCのAPIはより低レイヤになる

## 6. 参考

- [ORTCの提唱者が最近、ClueConで発表した資料](https://docs.google.com/presentation/d/1Pvqvv9kM77Xid3cFjx2pY0pQJlKpEJfPx2VaNtSnnVE/edit?usp=sharing)
- [ORTC API for WebRTC, W3C CG](http://ortc.org/wp-content/uploads/2015/06/ortc.html)
