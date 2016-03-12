---
layout: post
title: "WebRTCでTURN接続を試験する方法"
description: "WebRTCでTURN接続を試験する方法"
category: 
tags: []
---

## はじめに

WebRTCを触ってから少し時間が経つと、P2Pの通信だけでなく、より接続確率を高めるためにTURNを利用する人も増えてくると思う。
TURNは自前で建てても良いし（AWSなどの場合は、転送量課金に注意）、Turn as as Service(例えば[XIRSYS](https://xirsys.com/)など)を使ってもいい。また、[SkyWay](https://nttcom.github.io/skyway/features.html)もTURNも提供している。

いずれにせよ、どの手段を使ったとしても、TURNを利用することができる。利用は簡単で、JavaScriptであれば以下のオプションを利用してあげるだけだ。

{% highlight javascript %}
let configuration = {
    iceServers: [
        {urls: "stun:1.2.3.4"},
        {urls: "turn:5.6.7.8", credential: "secret", username: "yourusername"}
    ]
}
{% endhighlight %}

問題となるのは、TURNを実際に利用するためにはどのようにすれば、どのように試験すれば良いのか、という点だ。試験方法は大きく2つある。

## 試験方法その1(TURN単体のテスト)

注："試験方法その1"は、自前でTURNを構築した人向けの方法であり、自前で構築していない場合は、"試験方法その2"から確認いただきたい

Turnの定番実装である、[rfc5766-turn-server](https://github.com/coturn/rfc5766-turn-server)や[coturn](https://github.com/coturn/coturn)は、[turnutils_uclient](https://github.com/coturn/coturn/wiki/turnutils_uclient)というツールを配布している。

これを公式ページ上の手順にしたがってインストールして、ローカルなどからテストしたいTURNサーバに対して、以下のように実行すれば良い。

```
$ turnutils_uclient -t -p PORT_NUM -u 'yourusername' -w 'secret' YOUR.TURNSERVER.DQDN
```

- `-t`はclientとTURNサーバ間をTCPに(デフォルトはUDP)
- `-p`はポート番号指定
- `-u`はユーザ名指定
- `-w`はパスワード指定

これで、TURN単体の動作が上手くいっているか試験できる。

## 試験方法その2(E2Eのテスト)

単体で上手くいっていたとしても、エンドツーエンドで上手くいっているとは限らない。そのため実際にブラウザを2つ並べて試験したくなる。ここでの問題は、何も考えなしに試験をしてしまうと、TURNではなくP2Pで接続されてしまうという点だ。

いくつか試験方法はあるが、今回はMac OSやLinuxで利用できる `pf` コマンドを利用した方法を紹介する。(なお、MacはEl captitanのより前のバージョンでは、`ipfw`が利用できたが、El Capitanからは`pf`のみになっている)

`pf` は一種のファイアウォールのような機能を提供していて、任意の条件のパケットの通過・遮断を制御できる。ここでは、WebRTCの試験向けなので、特定のホスト向けのUDPを全遮断するケースを書いてみる。検証に利用しているのはMac OS(El Captain)だ。

### 1. pf用のコンフィギュレーションを修正する

Macでは、pfの設定ファイルは、`/etc/pf.conf`に保存されている。

```
$ sudo vi /etc/pf.conf

# 以下を最終行に追記 (X.X.X.Xは試験対向のIPアドレス)
block out log proto udp from any to X.X.X.X
```

これによって、X.X.X.X 宛てのUDPパケットは全てブロックされるようになる。結果としてUDPホールパンチングが通らず、P2Pの接続は確立できない。

block行にある`log`は、ブロックしたパケットのログを別の手段で確認するための設定だ。本記事では解説しないが、詳細は[コチラ](http://ftp.tuwien.ac.at/.vhost/www.openbsd.org/xxx/faq/pf/ja/logging.html)を参照いただきたい。

### 2. コンフィギュレーションの反映

さきほどのステップで修正した内容を反映する。操作は `pfctl` コマンドから実施できる。

```
$ sudo pfctl -f /etc/pf.conf
```

もし、何らかのエラーが出ている場合は、コンフィギュレーションを見なおす。

### 3. pfの有効化

さきほどのステップでの反映が済んだら、実際にpfの操作を行う。

```
# 有効化
$ pfctl -e

# 無効化
$ pfctl -d
```

実際にWebRTCでのUDPが遮断されているかチェックするには、P2Pでのメディア/データ接続が確立されている状態で、 `pfctl -e`を実行してみれば良い。音声・映像はその時点で停止するはずだ。（また chrome://webrtc-internals などでは、ICE状態が `disconnected` になっているのが確認できる）

この状態で、適切にTURNが設定されており、かつWebRTCアプリケーションにもIceServersが適切に設定されていれば、TURNによる接続となる。あとは、Chromeであれば `chrome://webrtc-internals`　から、Firefoxであれば `about:webrtc` から、どの候補が通信に利用されているか確かめれば良い。

## まとめ

本記事ではWebRTCにおける、TURN単体のテスト方法、およびE2EでのTURNテスト方法を述べた。
