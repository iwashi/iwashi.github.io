---
layout: post
title: "googTransportTypeの注意点"
description: "googTransportTypeの注意点"
category: 
tags: []
---

WebRTCのデバッグで、非常に簡単に使えて便利なものがChromeの"chrome://webrtc-internals"だ。少し見方に癖があるかもしれないが、多彩な情報が取得できるので、開発時に非常に役に立つ。

便利な一方で、読み方に少々気をつけないといけない点もあるので、本記事はその1つを紹介する。

## googTransportType とは

chrome://webrtc-internals の画面右側には接続しているコネクション情報が出力されている。実際にメディア・データ送受信に利用しているコネクションは太字で表示される。

その中の項目の1つに googTransportType というものがある。

![googTransportType](/assets/images/20170217_chromewebrtcinternal.png)

トランスポートタイプ、という言葉から分かるように、どのトランスポートプロトコルを利用しているを、表す項目だ。上記の例では、`udp`が記載されている。

## TURN利用時は？

P2PでUDP接続される場合は、googTransportTypeは`udp`となるのが自然かと思う。（そしてその通り表示される）

P2Pで接続できずに、TURN経由、特にTURN-TCPを利用した場合に、googTransportTypeの値はどうなるか？

直感だと、`tcp`が来そうな気もするが、実際にはTCPではなく、`udp`が表示される([参考](https://bugs.chromium.org/p/webrtc/issues/detail?id=2985))。これがややトリッキーで、誤解を招きやすい点なので注意して欲しい。

補足：TURN-UDP/TCP/TLSのどれであっても、googTransportTypeの内容は `udp` になる。PeerA - [UDP/TCP/TLS] - [TURN] - [★UDP] - [PeerB] という構成で★の箇所の内容が、googTransportTypeに表示される。

## では、いつ`tcp`が表示されるのか？

RFC6544で規定される[ICE-TCP](https://tools.ietf.org/html/rfc6544)で、接続が確立した場合のみに表示される。ICE-TCPは、P2Pで使われることはまずなく、SFU/MCUのように、ホールパンチングで強引に穴を空ける必要のないサーバを利用する場合に使われる。

## TURN-TCP経由での確立を確認する方法は？

私の知るかぎり、現行のChrome M56時点でchrome://webrtc-internalsのみで確認する方法は存在しない。（iceServersにTURN-TCPだけ追加して、TURN経由にするように指定すれば別)

最も簡単な方法は、Wiresharkやtcpdumpなどで、TCP経路でTURNサーバ宛てにメディアが流れているのを確認してしまうことだと思う。もし、chrome://webrtc-internalsで確認する方法があれば、[@iwashi86](https://twitter.com/iwashi86)まで教えて欲しい。
