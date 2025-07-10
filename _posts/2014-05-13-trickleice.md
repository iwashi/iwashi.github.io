---
layout: post
title: TrickleICEとは - WebRTCの要素技術 -
description: TrickelICEについて解説する記事
category: null
tags: []
ogp: /assets/images/ogp/2014-05-13-trickleice_ogp.png
---

WebRTCで用いられる要素技術の一つとして、TrickleICEがある。本ポストではTrickleICEについてわかりやすく解説する。
イメージを掴んでもらえるよう平易説明するので、正確さを重視される場合は、[RFC](http://tools.ietf.org/html/draft-ivov-mmusic-trickle-ice-01)を参照いただきたい。

## 本記事のサマリ：TrickleICEとは？
TrickleICEを一言で表すと、
　「ICEの候補をインクリメンタルに探して、
　　見つかったICE候補を接続先ピアと交換して、
　　すぐに接続を試行する仕組み」
である。

以下に、背景を含め詳細を解説する。

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

------

### 最低限のおさらい（STUN/TURN)
WebRTCで通信をするブラウザは、NAT配下に隠れていることが多い。
そのため、ブラウザ間で直接通信するためには、プライベートアドレスではなく、
グローバルアドレスの情報を利用する必要があり、何らかの仕組みを活用する必要がある。

その仕組みとして用意されているのが、STUNとTURNであり、それぞれ以下の役割を果たす。

- STUN : NAT外部のIP＆Portを調べて、ブラウザに教えてあげる
- TURN : （どうしても直接通信できない場合に）中継サーバを利用して、ブラウザ間で通信させてあげる

STUNの情報のみで、直接通信できてしまえば良いのだけど、
NATのタイプによっては、どうしても通信できないケースがあり、
その場合にTURNが登場する。

TURNを利用する場合は、中継が必要になることから接続数が増えるにつれて処理が重くなる点、
また第三者に勝手に利用されないようにする点、等に注意されたい。

### 最低限のおさらい２：ICE
上記のSTUNとTURNを踏まえて、ICEを表すと非常に簡単で

`ICE = STUN + TURN`

となる。

つまり、「STUNで頑張って、ダメな場合はTURNを使う」ように、
通信する手段を探してくれる仕組みがICEだ。


### ICEが全てを解決してくれる、そう思っていた時代が僕にもありました
実はICE単体で使っていると、イケてないポイントがある。
それは「（ブラウザ間で接続するまでの）速度が遅いこと」だ。


----
<img src="/assets/images/medium_6735333641.jpg" alt="ice image" class="img-responsive">
photo credit: <a href="http://www.flickr.com/photos/kalexanderson/6735333641/">Kalexanderson</a> via <a href="http://photopin.com">photopin</a> <a href="http://creativecommons.org/licenses/by-nc-sa/2.0/">cc</a>

----

### なんで遅いの？
ICEは接続時に、他ピアと接続する候補を収集する。
例えば、以下のような候補が考えられる。

- 同じNAT内にいる場合にプライベートアドレスを使って通信する候補 (ex. 192.168.1.100と192.168.1.200)
- STUNで取得したグローバルアドレスを使って通信する候補(ex. 100.0.0.1と200.0.0.1)
- 直接接続ができなくてTURNを使うケース　(ex. 123.123.123.123のTURNサーバを使う)

単なるICE(RFCだとvanilla ICEと呼ばれる)では、
これら全ての候補を全て収集した後に、「さあ、どれで通信しようか？」
と接続するピア間でお話し合いをするイメージである。

これらの候補が、数ミリ秒等で集められれば良いが、
STUNは原理的にタイムアウトを期待して、NATを判別することもあり、
数ミリ秒どころか1000倍のオーダで、数秒以上かかることもある。

結果として、単なるICEを用いると、ブラウザ間で接続を開始するまでかなり時間がかかってしまう。

## 満を持してTrickleICE
上記で説明した問題の解法がTrickleICEだ。
TrickleICEの概念自体は非常にシンプルで

- ICEの候補が見つかったらすぐに相手と交換する
- 相手と交換できたら、その情報を使ってすぐに接続試行する

となる。この、ICE候補が見つかったらすぐに、というのがポイントで、
具体的には処理を非同期で書ける点だ。上記のコードサンプルで示すと、

```
pc.onicecandidate = function(evt) {
  // pcはRTCPeerConnectionの前提
  // ここに何らかのシグナリングチャネルで、他方にevt.candidateを送る。
}
```

のように、onicecandidateにコールバック関数を設定しておいて、
ICEの候補が見つかったら、処理を進めるように書く。
結果として、全てのICE候補を待つ必要がないので、
ブラウザ間の接続が早くなるというわけだ。

### TrickleICEの先へ（HalfTrickle)
TrickeICEが全ての環境で活用可能とは限らない。（＝単なるICEのみをサポートする環境もある）
そこで、後方互換性が必要となるが、そのときに出てくるのがHalfTrickleだ。

HalfTrickleの考え方も非常にシンプルで、具体的には次の通り：

- 発信側は単なるICEと同様に、ICE候補を最初に全て集めてから、着信側に送る
- 着信側はTrickleICEをサポートしているので、インクリメンタルに動く

着信側は、インクリメンタルにICE候補を見つける都度に、接続を試みるので、
単なるICEのみで接続試行する場合に比べると、おおよそ半分のレイテンシになる。

ちなみに、FullTrickleというのもあって、これは単なるICE。

## もう一度サマリ
本ポストではTrickeICEを解説した。
今ならポスト冒頭で記載した

```
TrickleICEを一言で表すと、「ICEの候補をインクリメンタルに探して、見つかったICE候補を接続先ピアと交換して、すぐに接続を試行する仕組み」である。
```

も理解いただけるかと思う。

#### 単語の意味の補足
ちなみに、trickleの英語の意味は、「少しずつ進む/流れる」みたいな意味なので、ICEが少しずつ進む　のように解釈するとわかりやすい。

#### 参考
全て英語だが、以下のリンクは参考になる。

- <http://tools.ietf.org/html/draft-ivov-mmusic-trickle-ice-01>
- <http://webrtchacks.com/trickle-ice/>
- <http://chimera.labs.oreilly.com/books/1230000000545/ch18.html#_interactive_connectivity_establishment_ice>
- <ftp://143.225.229.133/ietf85/8885006/1352180905970/04-%20Trickle%20ICE.pdf>

-----

### 誤記等の指摘は
[@iwashi86](https://twitter.com/iwashi86)までご連絡いただけますようお願いいたします。
 