---
layout: post
title: "Slackにおける音声通話機能のWebRTC観点からの解析"
description: "Slackにおける音声通話機能のWebRTC観点からの解析"
category: 
tags: []
permalink: /:categories/:year/:month/:day/:title.html
---

## はじめに

2016/3/3より、[Slack](http://jp.techcrunch.com/2016/03/03/20160302slack-calls/)に音声通話機能が搭載された。
試しに使ってみたSlackユーザもそれなりにいると思う。

Slack音声通話機能の対応クライアントは、現時点では限定的だ。Slackの設定画面の一文を引用すると

```Currently on Mac and Windows desktop apps and in Chrome; coming soon to mobile!```

の通りで、Chromeまたはデスクトップのネイティブアプリとなる。
音声機能が実装されていてこの種類の対応状況なら、もちろん利用技術はWebRTCと考えるのが素直だ。(しかもWebRTCベースのスタートアップであるScreenHeroを買収していることもあり)
ここで、最も気になるのは内部でWebRTCをどのように利用しているか、という点だ。

すでに、WebRTCエンジニア御用達のWebRTCHacksでは[Dear Slack: why is your WebRTC so weak?](https://webrtchacks.com/dear-slack/)というタイトルで、Philipp Hancke氏(fippo)が記事を書いており、当該記事の中では簡単な説明がある。だが、述べられていない点も多い。

そこで、本記事では、200万人を越えるアクティブユーザを抱えるSlackが、どのようにWebRTCを利用しているのか、いくつかポイントをまとめたいと思う。
実際に、

- DesktopAppとChrome間での音声通話時に、Chromeのwebrtc-internalsからDumpを取得して解析
- ChromeのJavaScriptをななめ読み

して記事を書いており、もちろん不明な点は想定して書いている記述を含むものの、事実ベースの内容の記事になる。

なお、本記事はWebRTCについて、ある程度知識がある人向けに書いているので、基本的な事項は説明しない。
もし、TURNやMCUという言葉が分からなければ、[HTML5 Expert.jpの解説記事](https://html5experts.jp/iwase/12585/)辺りを先に読んで欲しい。
また、途中でSDPも出てくるので、SDPアレルギーな場合は、一部読み飛ばすのが良いと思う。

もし、記載が誤っている点などあれば [@iwashi86](https://twitter.com/iwashi86) までメンション/DMをいただきたい。
(2016/3/6 02:00、[@voluntas](https://twitter.com/voluntas)氏のコメントを受けて、一部修正。)

ということで本題。ポイントをまとめていく。

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

-----

## P2PのWebRTC利用は無し

WebRTCは1:1のメディア・データ通信を実現するのであれば、P2Pトポロジでの通信を提供するのが一般的だ。つまり途中にサーバを介さないのが普通ということだ。
にもかかわらず、Slackは1:1の接続において、必ず中継サーバを経由するようにしている。(これは過去のGoogle Hangoutと同様の形式)
ここでの中継サーバとは具体的に言えば、TURNとMCUのことを示している。

以下に1:1でのトポロジ図を掲載する。

<img src="/assets/images/toplogy_slack.png" alt="slack webrtc topology" class="img-responsive">

たとえ、隣の席で同一のLANにいる人と会話する場合も、この経路になる。
後述するが、TURNはAWS上にデプロイされており、私の利用ケースでは東京リージョンではなく、
シンガポールリージョンのインスタンスへ接続されていた。そのため、 極論を言えばシンガポール経由で隣の席の人と音声通話してもらってると考えて良い。（超無駄）

## どのようにして、強制的にTURNを利用しているのか？

今回のWebRTCのエンドポイントは、[Chrome-MCU]と[MCU-DesktopApp]の2つの組合せになる。
つまり、SDPのオファーアンサーをMCUも生成しているので、そのSDPおよびICE候補を見れば、どのような経路をたどるかはすぐ分かる。

### MCUから届くOfferは？

生のSDPを貼り付けると以下の通り。 '...★1'などの箇所は、私の説明上の追記で後で説明する。

```
type: offer, sdp: v=0
o=- 643193054244 643193054243 IN IP4 127.0.0.1
s=Room with no name..
t=0 0
a=group:BUNDLE audio
a=msid-semantic: WMS janus         ...★1
m=audio 1 RTP/SAVPF 111            ...★2
c=IN IP4 10.21.82.27
a=mid:audio
a=sendonly
a=rtcp-mux
a=ice-ufrag:X/x9
a=ice-pwd:P8XwtXqt3z7yK0VDthjMmT
a=ice-options:trickle              ...★3
a=fingerprint:sha-256 C5:5F:DA:7D:84:47:B1:BF:6B:55:16:62:48:31:3E:D3:F1:7B:25:89:92:4A:4B:4D:4D:D9:D5:AF:EA:D8:15:44
a=setup:actpass
a=connection:new
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1
a=ssrc:711812372 cname:janusaudio
a=ssrc:711812372 msid:janus janusa0
a=ssrc:711812372 mslabel:janus
a=ssrc:711812372 label:janusa0
a=candidate:4 1 udp 2013266431 10.21.82.27 12003 typ host   ...★3
a=candidate:8 1 udp 2013266431 172.31.1.90 12003 typ host   ...★3
a=candidate:4 2 udp 2013266430 10.21.82.27 12004 typ host   ...★3
a=candidate:8 2 udp 2013266430 172.31.1.90 12004 typ host   ...★3
```

まず、★1よりサーバ側のエンドポイントとして[janus](https://github.com/meetecho/janus-gateway)が利用されていることがわかる。
janusはWebRTC *Gateway* であるため、MCUとしても振る舞えるし、IVRや他のVoIPとの相互接続も可能だ。(本記事では多人数会話向けにも利用されると想定して、MCUとして利用している前提で説明する)

そして、★2でそれが確信に変わる。実際にjanus作者のLorenzo Miniero氏も、[ココ](https://webrtchacks.com/dear-slack/#comment-17598)でコメントしている通りで、JanusはRTP/SAVPFを依然として利用し続けている。

★3より、tricleICEには対応しているが、MCU側はtrickleではなく先にICE候補を投げつけてきていることが分かる。これはMCUやSFUで一般的だ。なぜなら、ICE候補が既に分かっているからだ。

ここでのポイントは、★3に登場しているIPアドレスが全てプライベートIPだということだ。(ポート番号として12003/12004があるが、これはjanusのコンフィグなどで指定されているのだと思う)

この時点で、普通のUDPホールパンチでは接続できないことが分かる。（★3は、自宅やオフィスからは100%到達できないアドレスなので）

### ではどうやってICEで接続するのか？

答えはChromeなどonicecandidateで取得できるICE候補を見れば分かる。
通常のICE動作と同様に、host/srflx/relayの3つがとれる。

hostやsrflxはほとんど意味がない。なぜらなば、このトランスポートアドレスでは先ほどの★3のプライベートアドレスに接続できないからだ。
ポイントは最後のrelay(TURN)で、以下のようなアドレスがとれる：

```
sdpMid: audio, sdpMLineIndex: 0, candidate: candidate:4184247995 1 udp 41754367 52.77.208.161 52017 typ relay raddr X.X.X.X rport 50512 generation 0 ufrag MQyVfDIb5jH9WrUh
```

途中にある *52.77.208.161* が重要で、これがSlackがデプロイしているTURNサーバのアドレスだ。
このアドレスを逆引きすると

```
dig -x 52.77.208.161

; <<>> DiG 9.8.3-P1 <<>> -x 52.77.208.161
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 27428
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;161.208.77.52.in-addr.arpa.  IN  PTR

;; ANSWER SECTION:
161.208.77.52.in-addr.arpa. 300 IN  PTR ec2-52-77-208-161.ap-southeast-1.compute.amazonaws.com.
```

ap-southeastリージョン(シンガポールリージョン)のアドレスであることが分かる。
AWSはVPC内部にEC2インスタンスを構築し、同時にプライベートIPを持つことができるので、
そのプライベートIPのアドレスが、前述の★3のプライベートアドレスと通信可能しているはずだ。

SDPや経路からは見えないが、MCU(Janus)も同一リージョンのVPC内部のEC2に構築しているのだと思う。
オンプレでDXで接続という案もあるが、非効率過ぎて現実的じゃない。

### Answerは？

同様にAnswerは以下の通りだ。


```
type: answer, sdp: v=0
o=- 643218903360 643218903359 IN IP4 127.0.0.1
s=Room with no name..
t=0 0
a=group:BUNDLE audio
a=msid-semantic: WMS janus
m=audio 1 RTP/SAVPF 111
c=IN IP4 10.21.82.27
a=mid:audio
a=recvonly      ...★4
a=rtcp-mux
a=ice-ufrag:4c6U
a=ice-pwd:PvqUXiHLeUIO7qgcKeVHhd
a=ice-options:trickle
a=fingerprint:sha-256 C5:5F:DA:7D:84:47:B1:BF:6B:55:16:62:48:31:3E:D3:F1:7B:25:89:92:4A:4B:4D:4D:D9:D5:AF:EA:D8:15:4
a=setup:active
a=connection:new
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1
a=candidate:17 1 udp 2013266431 10.21.82.27 12016 typ host
a=candidate:34 1 udp 2013266431 172.31.1.90 12016 typ host
```

基本は同一であるが、さきほどとはあえて違うところを1つ説明すると、★4の箇所である。
さきほどICEにフォーカスするため説明を省略したが、offerではsendonlyがある。
これの意味するところとして、実はMCUとChrome/DesktopApp間は2本のストリームを貼っている。
1つがsendonlyで、もう1つがrecvonlyだ。（sendrecvではない)
これはjanusが入口と出口を自由にして、プラグインで処理を変えられるようなアーキテクチャであるため、と考えられる。

ここまでの説明を図で示すと以下の通りになる。(さきほどの図の、より正確なバージョンと考えていただけると良い)

<img src="/assets/images/topology_slack2.png" alt="slack webrtc topology" class="img-responsive">

この方式にすると、多人数会議になった場合は、recvonlyのストリーム1本に複数人の音声が乗ることになるはず。（3者以上の通話は未検証）

## シグナリングについて

シグナリングはSlackが以前に買収したScreenHeroのものを利用しているようだ。

{% highlight javascript %}
_getServer("screenhero.rooms.join", ...)
// 略 //
_getServer("screenhero.rooms.create", ...)
{% endhighlight %}

のようなコードがminifyされたコードの中に見えることから分かる。
ルームベースのシグナリングを提供しているようだ。

## TURNについて

- turnのURNは、 `turn:slack-calls9.slack-core.com:22466` などであり、slack-callsX で複数台のTURNサーバが設置されているようだ
- TURNのusername/password(credential)は隠蔽されている。(JSで動的に取得)
- TURNはAWSの一定数のリージョン（少なくともシンガポールと、北カリフォルニアは確認）にデプロイされている
  - 最寄りのTURNは、AWS Route53のLBRやGeoDNSで取得しているのだと想定

WebRTCHacksの[記事](https://webrtchacks.com/dear-slack/)で言及されてない点については以上である。
以降では、WebRTCHacksの記事で多少わかりにくい部分の補足しておく。

## WebRTCHacks記事の補足

### ICE-TCPについて

Slackがサポート対象とするChromeはすでにICE-TCPをサポートしている。
そのため、TURNを利用しなくてもTCPによるメディア・データのパケットを送受信可能である。
これは、特にMCUやSFUのようなグローバルIPを持つようなWebRTCエンドポイントが片方にいる場合に効果的で、
TURNを経由しなくても、UDPがブロックされているような環境でWebRTCを利用可能になる。
しかし、残念ながら先ほどのSDPを見るに、ICE-TCPはMCU側で対応しておらずUDPのみの利用にとどまっている。

### TURN/UDPのみへの対応

TURNの設定についてもTURN/UDPの利用に限定されているようであり、比較的厳しいネットワーク環境に置かれるユーザは、
Slackの音声通話機能を使えない可能性が高い。
本来はTURN/TCPまたはTURN/TLS(特に443で動作させる)を有効にすべきであるがそれも未実施だ。
（これでも100%疎通するわけではない点に注意。厳格な企業プロキシはMITMするため、TLSを一旦解かれてしまうことがある）

### なぜ強制的にTURNを経由させているのか？

想定にはなるが、大きく以下の2点と考えられる。

1. 初期のコール確立までの時間を減らし、UXを向上させるため。なお、FaceTimeやWhatsAppも同様にTURNを強制経由している。(WhatsAppはさらに高度で、最初はTURN経由で途中でP2Pにスイッチ)
2. TURNの機能(特に認証機能、その他だとタイムアウト機構など)を利用するため

-----

## 最後に

Slackは2015年にScreenHeroというWebRTCをベースとするスタートアップを買収しており、
WebRTCの技術者も同様にAcqhireしている。
今後、ビデオ機能も追加されるようなので、その辺りを機にWebRTCの技術も最新のものに追従していって欲しい。
私自身もSlackのヘビーユーザーであり、かつWebRTCの1技術者としてその辺りを期待している。
