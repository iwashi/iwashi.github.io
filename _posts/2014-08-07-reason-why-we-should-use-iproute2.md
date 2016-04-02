---
layout: post
title: "net-tools(ifconfig等)からiproute2へ移行する3つの理由"
description: "なぜnet-tools(ifconfig等)をやめてiproute2を使うのか。その理由についての説明記事。"
category: 
tags: []
---

RHEL7やCentOS7では、多くのエンジニアが使っていたであろうifconfig等のコマンドが利用不可になる。
これは、net-toolsというパッケージが非推奨という扱いであり、デフォルトで含まれなくなるためだ。
(実際にnet-toolsは長い間、開発が止まっている)
今後、同様の操作をする場合は、iproute2パッケージに含まれるコマンドを利用することになる。

もちろん、nettoolsが無くなっちゃうからiproute2を使う、という後ろ向きな理由もあるが、
もっと前向きな理由もあるはず。そこで、

##### そもそも、なぜiproute2に移行しなくてはいけないのか？

について、気になって色々と調べてみたので、本記事では調べて分かった、
移行に前向きになる理由3つを以下にまとめてみる。

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

#### 1. 高機能だから
ネットワーク周りの高機能な操作、例えばネットワークトラフィックを制御しようとすると、
net-toolsでは対応できない。iproute2では、これが実現可能となる。
具体的には、[tc](http://www.linuxmanpages.com/man8/tc.8.php)コマンドで対応可能となる。

また、ルーティングテーブルを複数保持するような複雑なルーティングを実現したい場合は、
net-toolsでは対応できないため、iproute2が必要となる。

(個人的感想：といっても、ほとんどのエンジニアには不必要なコマンドな気がする。。。)

#### 2. 速いから
net-toolsのコマンドであるifconfigは、例えば/procから情報を収集して、情報を出力している。
一方で、iproute2は[Netlink API](http://linuxjm.sourceforge.jp/html/LDP_man-pages/man7/netlink.7.html)を利用しており、
ソケットライクな方式にて、カーネルとネットワーク関連の情報をやりとりする。

具体例として、[この記事](http://techblog.rosedu.org/ifconfig-vs-iproute.html)によると、ミリ秒単位の世界では速度差があるようだ。

(個人的感想：といっても、体感的には変わらないからあんまり気にしなくても。。。)

#### 3. 慣れたら便利だから
net-toolsでは、ネットワーク周りの操作をするときに、複数のコマンドを覚えておく必要があった。
例えば、ifconfig, route, arp 等の別々のコマンドが必要となる。

一方で、iproute2では、ipコマンドを覚えておけば、後は直感的な操作で対応できる。
例えば、

- ルーティングテーブルを見たい -> ip route show
- IPアドレスを確認したい -> ip addr show

と打てば良い。実際のコマンドの文字列を見ると、やりたいことと沿っていると思う。また、より便利なことに上記のコマンドは短縮できる。つまり、

- ルーティングテーブルを見たい -> ip r s
- IPアドレスを確認したい -> ip a s

と、短縮コマンドが使えるのだ。（この辺りは、CiscoのIOSを使ったことがあれば、ピンとくるかも）

上記のように直感的なコマンド形式が使える、かつ短縮コマンドが使える点から、iproute2が良い。

(個人的感想：といっても、どうせtab補完とか、historyから呼び出すからあんまり変わらないかも。。。)

-----

### まとめ
高機能で、速くて、便利だから、iproute2を使うべき。

(個人的感想：なんだかんだいつか慣れるもんだ)

-----

### 参考

- [https://blog.timheckman.net/2011/12/22/why-you-should-replace-ifconfig/](https://blog.timheckman.net/2011/12/22/why-you-should-replace-ifconfig/)
- [http://techblog.rosedu.org/ifconfig-vs-iproute.html](http://techblog.rosedu.org/ifconfig-vs-iproute.html)

