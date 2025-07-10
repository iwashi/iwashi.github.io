---
layout: post
title: WebRTCにて(S)RTCPが必要な理由
description: WebRTCにて(S)RTCPが必要な理由
category: null
tags: []
ogp: /assets/images/ogp/2014-12-12-why-do-we-need-rtcp-in-webrtc_ogp.png
---

This post is a No.12 article of WebRTC Advent Calendar 2014
この記事は、WebRTC 2014 アドベントカレンダーの12日目の記事です。

-----

### TL;DR

- RTCPで通信状況（統計情報）を送受信側で伝え合って、音声・映像の品質にフィードバック
- 特にWebRTCでは、RTCPを暗号化したSRTCPを利用

----

### はじめに

[WebRTC Meetup Tokyo #3](https://atnd.org/events/53504)で、WebRTCを支えているプロトコルについて、簡単なLTをしました。
LTの中でDTLS、RTP、SCTPについて喋ったのですが、LTという時間の都合上、説明を端折ったところがあるので、本記事ではその補足をします。

ちなみに、資料は以下にあります：

<iframe src="//www.slideshare.net/slideshow/embed_code/37569990" width="425" height="355" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" allowfullscreen> </iframe> <div style="margin-bottom:5px"> <strong> <a href="//www.slideshare.net/iwashi86/20140801-web-rtcmeetup3r3" title="WebRTCを支えるマイナーなプロトコルSRTP/DTLS/SCTPを分かった気になる" target="_blank">WebRTCを支えるマイナーなプロトコルSRTP/DTLS/SCTPを分かった気になる</a> </strong> from <strong><a href="//www.slideshare.net/iwashi86" target="_blank">iwashi86</a></strong> </div>

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

### RTPは再送を諦めているだけじゃない
Slide27枚目で、パケットロスが起きた場合の対応として、「再送をGiveUp」すると説明していますが、RTPにおけるパケットロスは実は大切な役割を果たしています。それは何なのかというと、UDPのヘッダを思い返してみるとわかります。

UDPはIPの薄いラッパで、以下のヘッダしかありません：

- Source Port
- Destination Port
- Length
- Checksum

上記の状態しか保持していない状態で、音声・映像ストリームのパケットロスが起きると、大事なことが１つ分からないのです。それは、**パケットロスが起きたこと自体が分からない**ということ。UDPはTCPと異なり、シーケンス番号を保持していないためです。

パケットロスの発生有無がわからないと、何が問題かということ、送信側でどの程度の品質の音声・映像を流していいか分からないのです。ネットワークが混雑しているのならば、ビットレートを落として送るべきですが、そもそもネットワークの混雑を知らないと、それも出来ません。


### RTPにはシーケンス番号がある
UDP単体だとダメだったんですが、RTPにはシーケンス番号があります(以下のフォーマット参照)。そのため、パケットロスが起きたことを検知できます。

```
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |V=2|P|X|  CC   |M|     PT      |       sequence number         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                           timestamp                           |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           synchronization source (SSRC) identifier            |
   +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
   |            contributing source (CSRC) identifiers             |
   |                             ....                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### ちなみにタイムスタンプもあるんだけど？
タイムスタンプがあるから、パケットロスを簡単に検知できるんじゃないの？という声もありそうですが、それは出来ません。なぜなら、無音・無映像状態の時は音声・映像を流さなくても良い、つまりパケットを送らなくても良いためです。（トラフィック的に流しても無駄ですよね）


### でもRTP自体だけでも足りない
前述の通り、RTPにはシーケンス番号がありますが、RTP単独でもダメです。というのも、RTPはあくまで音声・映像のメディアを送受信するプロトコルであって、RTPの制御（コントロール）を担っているわけではないためです。そこで、RTPに加えてRTCP(Real-time Transport Control Protocol)というプロトコルが使われています。


### RTCPには何が入っている？
RTCPでは、いくつかのパケットタイプ（RTCPで伝え合うメッセージのフォーマットみたいなもの）が規定されています。その中でも代表的なのが、SR(Sender Report)とRR(Receiver Report)です。

SRには、送信側と受信側の情報を含めます。例えば、これまでに送ったパケットの数や、タイムスタンプを含めます:

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
header |V=2|P|    RC   |   PT=SR=200   |             length            |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         SSRC of sender                        |
       +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
sender |              NTP timestamp, most significant word             |
info   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |             NTP timestamp, least significant word             |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         RTP timestamp                         |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                     sender's packet count                     |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                      sender's octet count                     |
       +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
report |                 SSRC_1 (SSRC of first source)                 |
                                    以下略
```

RRには、受信側の情報を含めます。例えば、欠落したパケットの数や、ジッタの推定値を含めます:

```
        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
header |V=2|P|    RC   |   PT=RR=201   |             length            |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                     SSRC of packet sender                     |
       +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
report |                 SSRC_1 (SSRC of first source)                 |
block  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  1    | fraction lost |       cumulative number of packets lost       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |           extended highest sequence number received           |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                      interarrival jitter                      |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         last SR (LSR)                         |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                   delay since last SR (DLSR)                  |
       +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
report |                 SSRC_2 (SSRC of second source)                |
block  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  2    :                               ...                             :
       +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
       |                  profile-specific extensions                  |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                                    以下略
```

### 忘れちゃいけない暗号化
WebRTCは、メディアの暗号化が必須です。RTCPも例にもれず、暗号化対象であり、その場合はRTCPじゃなくてSRTCPになります。詳細は[RFC5764](http://tools.ietf.org/html/rfc5764)辺りを参考にしてください。


### まとめ
RTPだけじゃ物足りないので、RTCPで通信状況（統計情報）を送受信側で伝え合って、音声・映像の品質にフィードバックしています。
特にWebRTCでは、RTCPを暗号化して、SRTCPが使われてます。

以上、WebRTCの裏側で動いているマイナーなプロトコルの紹介でした。
