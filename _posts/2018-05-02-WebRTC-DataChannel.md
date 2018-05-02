---
layout: post
title: "WebRTC Data Channelについて - W3CとIETF側から"
description: "WebRTC Data Channelについて、W3CとIETF側からの解説を少ししてみた記事"
category: 
tags: []
---

WebRTCも誕生から5年以上経っており、Web上の記事も多く増えてきた。WebRTCには、大きくMedia ChannelとData Channelがあるが、後者のData Channelの日本語記事は非常に少ない。

日本語の記事の中では、[@udonchan氏の記事](https://qiita.com/udonchan/items/7f5ffa9e8982ae1636c3)が最も正確に書かれているが、2014年から時間が経ったこともあり、やや変更が加わっている部分(e.g. SCTPのPPIDは57まで定義されている点など)もある。その他の日本語記事は、やや記述が不正確なところもあるので、あまりオススメしない。

本記事では、WebRTC Data Channelについて知っておいた方が良いこと、および一次情報への参照をまとめておこうと思う。(本記事自体は、主観がそれなりに含まれるので、参考程度にしつつあとは一次情報や実機で確かめてもらえれば)

## W3C APIについて

仕様は以下の2つが役立つ。

- [W3C API仕様](https://w3c.github.io/webrtc-pc/#peer-to-peer-data-api)
- [MDN](https://developer.mozilla.org/en-US/docs/Web/API/RTCDataChannel)

W3C APIは、 1)ブラウザ実装者向けの視点で書かれているため、2)ブラウザの実装と乖離している部分も多いため、という2点の理由から流し読みするぐらいで良い。ただし、[Data ChannelのExample](https://w3c.github.io/webrtc-pc/#peer-to-peer-data-example)は、async/await記法を使われていて、シンプルに書かれているので、ミニマムな実装イメージを掴むのに役立つ。

実装により近く、分かりやすいのはMDNのドキュメントで、各種APIやイベントハンドラを知るのに良い。この辺でイメージを掴んだ上で、ご自身が対象とするブラウザで簡単なコードを書いて検証するのが良い。ブラウザごとに差分が多い(たとえば、MS EdgeはData Channelのサポートがそもそも存在しない)ので、実機検証は必須だ。

### createDataChannel() についての補足

音声や映像を使う場合と異なり、Data ChannelではaddTrack()するメディアが存在しない。このまま、SDP OfferをcreateOffer()から作成しても、ほぼ空っぽのSDPが生成されてしまう。そこで、RTCPeerConnectionに対して、Data Channelで通信したい意図を伝えるために、RTCPeerConnectionに対して、createDataChannel()を呼ぶ必要がある。

createDataChannel()は、第一引数でラベルを指定できる。これは、1:1の接続を確立したとき、および複数のData Channelを確立したときに、Data Channel間を見分けるために活用できる。これは、[ココ](https://w3c.github.io/webrtc-pc/#dfn-datachannellabel)に規定されている。指定したラベルは、 ondatachannelイベント発火時に、拾えるのでユーザ側のアプリケーションで自由に使うことができる

また、createDataChannel()は第二引数で[いくつかのオプション](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/createDataChannel#RTCDataChannelInit_dictionary)を取れる。たとえば、順番を制御有無を指定するための ordered オプションや、最大再送回数を指定するための maxRetransmits を指定できる。WebRTCのDataChannelは、SCTP over UDPで制御されるので、SCTPで定義される能力を活用して、このあたりは実現されている。なお、全て省略するとTCPと同様のReliableモードで動作する。

createDataChannel()を呼んだ後に、createOffer()を呼ぶと m=application が設定されたSDPが生成される。WebRTCのお作法的には、SDPを交換するタイミングは peerConnctin.onnegotiationneeded で拾うべきであり、実際にイベント発火もするので、onnegotiationneededハンドラの中で、createOffer()してあげるのがお行儀の良い作りだ。

createOffer()を呼ぶと、SDPが生成される。このとき、実際に多く利用されるブラウザであろう Chrome M66 と FF 59 のSDPはそれぞれ違っているので、Data Channelに関する大事な部分を以下に貼っておく。以下の生データを見ればわかるが、SDPの形式がやや異なる。I-D的にいえば、どちらも古くて `a=sctpmap` は既に存在していない。現行のI-Dだと `a=sctp-port:5000` と書くのが正しい。(ただしあくまで、RFCの議論の話で、WebRTCの利用者の視点からすればは大して重要ではない)

#### ChromeのSDP

```
m=application 9 DTLS/SCTP 5000
a=sctpmap:5000 webrtc-datachannel 1024
```

#### FirefoxのSDP

```
m=application 51982 DTLS/SCTP 5000
a=sctpmap:5000 webrtc-datachannel 256
a=max-message-size:1073741823
```

### 2つ目のData Channelを貼りたい場合のSDP交換は必要か?

アプリケーションによっては、Data Channelを複数貼りたい場合がある。たとえば、1つのData Channelはファイルの送受信専用として、もう1つはテキストチャット用といったケースだ。

ここで疑問になるのは、1つ目のData Channelが確立されている状態で、2つ目のData Channelを確立した場合に、再度SDPのNegotiationが必要なのかどうか？といった点だ。具体的にコードで示すと以下のようになる。

```
// たとえばあるメッセージ契機で、2つ目を貼るとすると...
dataChannel.onmessage = () => {
    
    // 任意の処理をゴニョゴニョして…

    // 2つ目のDataChannelを確立する
    peerConnection.createDataChannel('2nd data channel');
};
```

先程の問の回答としては、「SDPの再交換は不要」だ。全てのData Channelの接続(SCTP/DTLSのアソシエーション)は、同一のポートで多重化されているので、SDP自体への変更は存在しない。したがって、SDPの再交換は不要となる。本内容は[JSEP](https://tools.ietf.org/html/draft-ietf-rtcweb-jsep-24#section-4.1.5)にも規定されている。

内部的には、後述するDCEPでのハンドシェイクが起きている（はず）。

## IETF側の仕様について

本記事末尾にRFC/I-Dへのリンクをコメント付きでまとめておくので、詳細はそちらを見ていただくとして、その中からかいつまんで、いくつか書く。

### DCEPについて

WebRTC Data Channelは、SCTP over DTLS上で実現されている。ただしそれだけではなく、実際にはSCTPの4way handshake(TCPの3wayと違う点に注意。ちなみにTear DownもTCPの4wayじゃなくて3way)に続いて、Data Channel用の2way handshakeが実施されている。

具体的には、接続開始側が DATA_CHANNEL_OPEN を送りつけて、応答側が DATA_CHANNEL_ACK を返して、Data Channelの接続を確立する。DATA_CHANNEL_OPEN のパケットフォーマットは以下の通り。

```
      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |  Message Type |  Channel Type |            Priority           |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                    Reliability Parameter                      |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |         Label Length          |       Protocol Length         |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     \                                                               /
     |                             Label                             |
     /                                                               \
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     \                                                               /
     |                            Protocol                           |
     /                                                               \
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

下から2つ目にあるLabelなどは、W3C API側で叩いてるlabelと同じ。

### 実はDCEPを使わないケースもある

(個人的には、必要性を感じないが、仕様を見てびっくりしないように、一応さっくり書いておくと…)

Data Channelの確立のために、さきほどDCEPを用いる話を書いた。DCEPは、実際に流れる経路と同じ(ICE->DTLS->SCTPが確立した経路と同じ)上で、ハンドシェイクが起こるのでいわゆるin-bandネゴシエーションと呼ばれる。一方で、out-of-bandでやる方法もある。

すなわち、createOffer()から始まるシグナリングのように、シグナリングサーバを経由させて、SDPとして交換する方式にもある。この辺は[I-D: SDP-based Data Channel Negotiation](https://tools.ietf.org/html/draft-ietf-mmusic-data-channel-sdpneg-17)に記載されており、たとえばSDPの例として以下が上げられている。

```
   a=dcmap:0
   a=dcmap:1 subprotocol="BFCP";max-time=60000;priority=512
   a=dcmap:2 subprotocol="MSRP";ordered=true;label="MSRP"
   a=dcmap:3 label="Label 1";ordered=false;max-retr=5;priority=128
   a=dcmap:4 label="foo%09bar";ordered=true;max-time=15000
```

W3C側APIのRTCDataChannelを見ていて、negotiated(trueに設定時)のくだりが出てきたら、「あぁ、out-of-bandのことか」と理解しておくと、仕様がちょっと読みやすくなる。

### RFC I/Dの参考

- [draft-ietf-rtcweb-data-channel-13.txt](https://tools.ietf.org/html/draft-ietf-rtcweb-data-channel-13)
    - WebRTC Data Channelの概要や要件をまとめているドキュメント
    - 他のRFCやI-Dへのリンクもまとまっているので、全体像を掴むのに良い
- [Datagram Transport Layer Security (DTLS) Encapsulation of SCTP Packets](https://tools.ietf.org/html/rfc8261)
    - SCTP over DTLS について記載されたもの
- [Session Description Protocol (SDP) Offer/Answer Procedures For Stream Control Transmission Protocol (SCTP) over Datagram Transport Layer Security (DTLS) Transport](https://tools.ietf.org/html/draft-ietf-mmusic-sctp-sdp-26)
    - Data Channelを取り巻くSDP周りについて規定されているもの
- [WebRTC Data Channel Establishment Protocol](https://tools.ietf.org/html/draft-ietf-rtcweb-data-protocol-09)
    - DCEP(Data Channel Establishment Protocol)についてまとめたもの
    - SCTP-over-DTLS で動作している、WebRTC Data Channelのプロトコルについて記載がある
- [SDP-based Data Channel Negotiation](https://tools.ietf.org/html/draft-ietf-mmusic-data-channel-sdpneg-17)
    - DECPじゃなくて、out-of-bandでネゴシエーションして、Data Channel確立したい場合の話
