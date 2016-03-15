---
layout: post
title: "続：Slackにおける音声通話機能のWebRTC観点からの解析 - 多人数会議"
description: "続：Slackにおける音声通話機能のWebRTC観点からの解析 - 多人数会議"
category: 
tags: []
---

## はじめに

以前の[記事](http://iwashi.co/2016/03/05/slack-webrtc-analysis.html)にて、SlackにおけるWebRTCの利用についての解析結果を掲載した。
前回の記事は、Slackが1:1の通話において、どのようにしてWebRTCを利用しているかという点にフォーカスしており、
SlackはTURNを強制的に利用し、Janus経由でエンドツーエンドの音声接続を提供していることを明らかにした。

本記事では、引き続きSlackの音声通話機能についての解析を述べる。
本記事の主なスコープは、Slack音声通話機能の多人数会議(マルチパーティコール)の解析である。

なお、前回同様にWebRTCの基礎知識を持った人を想定して記事を書くので、基礎的な知識の解説は実施しない。必要な場合は、前回同様に[HTML5 Expert.jpの解説記事](https://html5experts.jp/iwase/12585/)辺りを先に読んで欲しい。

では本題に進む。

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

## 検証における条件は以下の通り

- 検証条件
  - 3名で音声通話を実施
     - 1名はChrome on MacがまずRoomを作成(発信)
     - 残り2名はDesktopApp on MacからRoomに接続
- 検証方法
  - 音声通話中に `chrome://webrtc-internals` からDump取得およびログ確認
  - 同画面からSDPを確認
  - Wiresharkからパケットキャプチャを確認

## 解析結果：SlackのMCUではなくSFUとして動作

結論から述べると、Slackで利用している[janus](https://github.com/meetecho/janus-gateway)は、
MCUではなくSFUとして動作していることが分かった。

> 補足: JanusはWebRTC Gatewayであり、プラグインの組合せにより様々なモードで動作可能だ。実際、[Janus公式ドキュメント](https://janus.conf.meetecho.com/docs/janus__videoroom_8c.html)にも掲載されているように、SFU向けのプラグインも提供されている。（本プラグインが、Slackでも利用されているかどうかは不明）

これを図に表すと以下の通りになる。MCU利用時のトポロジは左側であり、SFU利用時のトポロジは右側である。Slackはこの2つのうち赤い点線で囲まれる右側のトポロジとなる。

<img src="/assets/images/slack_sfu.png" alt="slack webrtc topology" class="img-responsive">

サーバサイドで音声合成するMCUでの利用ではないため、人数が増えれば増えるほど下りのストリームは増加する。

## なぜこれが分かるか？

実際にSlack側から送付されるSDPを確認すれば良い。今回の検証は3者間での通話を試しており、Slack側から送信されるメディアストリームに関する2種類のSDPを以下に示す。★がついているのは説明上の追記。

### SDP1つ目(setRemoteDescriptionしているSDP)

```
type: offer, sdp: v=0
o=- 1934855961425 1934855961425 IN IP4 127.0.0.1
s=Room with no name..
t=0 0
a=group:BUNDLE audio
a=msid-semantic: WMS janus
m=audio 1 RTP/SAVPF 111
c=IN IP4 10.21.119.210
a=mid:audio
a=sendonly       ・・・★1
a=rtcp-mux
a=ice-ufrag:TSS3
a=ice-pwd:nNIA1e4IPKi80wTmQXELfH
a=ice-options:trickle
a=fingerprint:sha-256 C5:5F:DA:7D:84:47:B1:BF:6B:55:16:62:48:31:3E:D3:F1:7B:25:89:92:4A:4B:4D:4D:D9:D5:AF:EA:D8:15:44
a=setup:actpass
a=connection:new
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1
a=ssrc:1847733899 cname:janusaudio
a=ssrc:1847733899 msid:janus janusa0
a=ssrc:1847733899 mslabel:janus
a=ssrc:1847733899 label:janusa0
a=candidate:6 1 udp 2013266431 10.21.119.210 12005 typ host
a=candidate:12 1 udp 2013266431 172.31.0.210 12005 typ host
a=candidate:6 2 udp 2013266430 10.21.119.210 12006 typ host
a=candidate:12 2 udp 2013266430 172.31.0.210 12006 typ host
```

### SDP2つ目(setRemoteDescriptionしているSDP)

```
type: offer, sdp: v=0
o=- 1934856623162 1934856623161 IN IP4 127.0.0.1
s=Room with no name..
t=0 0
a=group:BUNDLE audio
a=msid-semantic: WMS janus
m=audio 1 RTP/SAVPF 111 ・・・★2
c=IN IP4 10.21.119.210
a=mid:audio
a=sendonly      ・・・★1
a=rtcp-mux
a=ice-ufrag:tFU7
a=ice-pwd:sQ1tpfAOrpm1okszeBmy39
a=ice-options:trickle
a=fingerprint:sha-256 C5:5F:DA:7D:84:47:B1:BF:6B:55:16:62:48:31:3E:D3:F1:7B:25:89:92:4A:4B:4D:4D:D9:D5:AF:EA:D8:15:44
a=setup:actpass
a=connection:new
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=rtpmap:111 opus/48000/2
a=fmtp:111 minptime=10; useinbandfec=1; usedtx=1
a=ssrc:3006424101 cname:janusaudio
a=ssrc:3006424101 msid:janus janusa0
a=ssrc:3006424101 mslabel:janus
a=ssrc:3006424101 label:janusa0
a=candidate:15 1 udp 2013266431 10.21.119.210 12014 typ host
a=candidate:30 1 udp 2013266431 172.31.0.210 12014 typ host
a=candidate:15 2 udp 2013266430 10.21.119.210 12015 typ host
a=candidate:30 2 udp 2013266430 172.31.0.210 12015 typ host
```

以上のSDPを2つ見ると、★1の箇所よりSend Only(片方向)のストリームが届いているのを確認できる。SDPが2つあるため、下り方向のストリームが2本できるという意味になる。これによりMCUではないことが分かる。

なお、★2に関しては参考情報で、Janus作者のLorenzo Miniero氏が「[もう直したよ](https://twitter.com/elminiero/status/708295367041925120)」と発言しているので、Slack側が新しいJanusを導入したら、RTP/SAVPFは修正されるはずだ。

ここまでSDPを確認してきたが、これらのSDPの確認から重要なことがもう1つ分かる。

## SlackはMultiStreamを利用していない

WebRTCで複数のストリームを配信する場合、いくつかの方法がある：

1. マルチキャスト
  - a. 複数のPeerConnectionがそれぞれメディアストリームを1つ持つ
  - b. 1つのPeerConnectionに複数メディアストリーム
2. サイマルキャスト (本記事では扱わない)
3. SVCエンコーディング (本記事では扱わない)

[1.a] はWebRTCの初期実装から利用可能な技術であり、[1.b] にはPlanBとUnified Planの2種類の実装がある。（補足：最近はChromiumが[Unifid Planの実装をはじめた](https://bugs.chromium.org/p/chromium/issues/detail?id=465349#c24)ようなので、今後はChromeおよびFirefoxの両者がUnified Planに収束していく）

今回のSlackのSFUは、比較的原始的な[1.a]の方式を利用している。PeerConnectionのオーバヘッドもあるし、複数ストリームの追加削除もあまり柔軟ではない。

## WebRTC-internalsにおけるコネクションの接続状況

コネクションを1つ抜粋して示すと以下の通りになる。

<img src="/assets/images/slack_internals.png" alt="slack webrtc topology" class="img-responsive" width="50%">

googLocalCandidateTypeや、googRemoteCandidateTypeよりP2Pで接続されているように見えるが、アドレス帯はjanusが持っているプライベートIPであり、ここで表示されているのはJanus間の接続となる。ChromeやSlack Desktop Appから、これらのアドレス帯域に対してTURN接続しているというのは[以前の記事](http://iwashi.co/2016/03/05/slack-webrtc-analysis.html)で説明したとおりだ。

(ちなみに個人的に1つだけ疑問であった、googLocalAddressに記載される10.21.119.21:59582はどの情報から取れているか把握できていない、という点はPeerReflexiveなのでUDPホールパンチング中に解決されるアドレスだと後から気づいた)

## TURNで利用しているソフトウェアについて

Coturnではなく、[RFC5766 TURN Server](http://rfc5766-turn-server.googlecode.com/svn-history/r1805/branches/v3.2/src/ns_turn_defs.h)を利用しているようだ。しかもRFC 5766 TURN Serverの中でも。やや古いバージョンを利用している。をこれは、Wireshark上で返ってくるTURNのレスポンスを見るとわかる：

<img src="/assets/images/turn_response_slack.png" alt="slack webrtc topology" class="img-responsive">

ちなみに、RFC5766 TURN Serverの最新バージョンは、GitHUb上の[ソース](https://github.com/coturn/rfc5766-turn-server/blob/v3.2/src/ns_turn_defs.h)によれば、2016/3/15時点で"3.2.5.9"だ。

## 最後に

本記事では、Slackの多人数通話を中心に、WebRTC観点からの解析を行った。SlackはSFU形式でWebRTCを利用してはいるものの、WebRTCの最新技術に追従しきれているわけではないようだ。

また、映像機能が追加されたタイミングでも、解析してみたい。
