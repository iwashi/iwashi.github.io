---
layout: post
title: "WebRTC MediaServer(SFU/MCU)の情報まとめ"
description: "WebRTC メディアサーバ(SFU/MCU)の情報まとめ"
category: 
tags: []
---

## はじめに

WebRTCの通信形態は大きく分けて、メディアを解釈するサーバを介するもの・介さないもの、の2種類がある。

- メディアを解釈するサーバを介さないもの
  - P2P
  - TURN経由
- メディアを解釈するサーバを介するもの
  - MCU経由★
  - SFU経由★
  - (VoIP-WebRTC Gatewayなどもあるが、ここでは取り上げない)

どれが必要になるかは、WebRTCを利用するアプリケーションのユースケースに依存するので、一概に何が1番良いというものはない。

本記事では、上記のうち、★をつけているメディアサーバ(SFU/MCU)の現状(2016年)について記載する。WebRTCを使う上で、特にMCUやSFUに興味がある方には参考になれば幸いだ。

### 本記事を読むと得られるもの・得られないもの

- 得られるもの
  - WebRTCに関連するMCU/SFUの情報、概要
- 得られないもの
  - 紹介するそれぞれのプロダクトの詳細(プロダクトへのリンクを付けるので、各人で参照いただきたい)
  - MCU/SFUプロダクトに注力するため、CPaaS(Communication PaaS)の情報は載せない

### 対象読者

- WebRTCに関わっている人、特にMCU/SFUに興味がある人
  - 本記事ではWebRTCの基礎的な内容は説明しないので、必要であれば別の情報を参照いただきたい

ということで本題。

<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- iwashico_middle -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4737755123993145"
     data-ad-slot="6593095118"
     data-ad-format="auto"></ins>
<script>fa
(adsbygoogle = window.adsbygoogle || []).push({});
</script>

## TL;DR;

以下の表を見ていただくのが1番早い。ほとんどこれが全て。この表でも満足せず、さらに情報が欲しい人は、それぞれ簡単に解説を加えるので後半も読んでいただきたい。気に入ったものは、該当プロダクトのページを是非チェックして欲しい。

(アルファベット順)

|名称|SFU|MCU|録画|録音|OSS|License|備考や特徴とか|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|[Intel Collaboration Suite for WebRTC](https://software.intel.com/en-us/webrtc-sdk)|✔[^1]|✔|✔|✔||N/A|Licodeを内部で利用している[模様](https://github.com/ging/licode/issues/518)|
|[Janus](https://janus.conf.meetecho.com/docs/janus__videoroom_8c.html)|✔|✔|✔|✔|✔|GPL v3|Janus本体はWebRTCゲートウェイ。SFU/MCUなどの各種機能はPlugin形式で追加|
|[Jitsi VideoBridge](https://jitsi.org/Projects/JitsiVideobridge)|✔||✔[^2]|✔|✔|Apache2|Atlassian配下。Talky.ioも利用。執筆時点でSimulcastが使える唯一のSFU。|
|[Kurento](http://www.kurento.org/)|✔|✔|✔|✔|✔|Apache2|[NUBOMEDIA](http://www.nubomedia.eu/)がマネージドKurentoを提供|
|[Licode/Erizo](http://lynckia.com/licode/)|✔|✔|✔|✔|✔|MIT|もともとMCUのみ、SFUは後からオプションとして利用可能に|
|[MediaSoup](http://mediasoup.org/)|✔||||✔|ISC|おそらく最後発のSFU、開発社が触れるNodejsのAPIがあるのが特徴|
|[Medooze](http://www.medooze.com/)||✔|✔|✔|✔|?|SIP連携重視|
|[PowerMedia XMS](http://www.dialogic.com/en/products/media-server-software/xms.aspx)||✔|✔|✔||N/A|有償のみ、[SoftBankが利用](https://www.dialogic.com/en/company/press-releases/2016/2016-02-17-softbank-deploys-large-scale-webrtc-based-conferencing-application-enabled-by-dialogic.aspx)|
|[SORA](http://sora.shiguredo.jp/)|✔||✔|✔||N/A|時雨堂製、有償のみ|
|(参考[^3])OpenTok Mantis|✔|?|✔|✔||N/A|[Tokboxの内部で利用、非公開](http://www.tokbox.com/blog/mantis-next-generation-cloud-technology-for-webrtc/)|
|(参考[^3])SkyLink|✔|✔|✔|✔||N/A|SkyLinkの内部で利用、非公開|
||||||||


[^1]: MCUがメインで、SFUはオプションで利用
[^2]: 録画は別ライブラリ
[^3]: SFU/MCUプロダクトではなく、プラットフォーム側だが独自のメディアサーバのようなので、参考として追記

以降、各種プロダクトについて簡易な解説を加える。


### Intel Collaboration Suite for WebRTC 

Intelが開発しているWebRTCプロダクトスイート。クライアントSDK(JS/Android/iOS/Windows)・サーバSDK・SFU/MCU/SIPゲートウェイなど、ほぼ全て揃えて提供している。フルスクラッチで全て作っているのではなく、MCU/SFUはLicodeベースの模様。GitHubのissueにて、それをほのめかす[コメント](https://github.com/ging/licode/issues/518)が出ている。

ちなみに最近、韓国の通信キャリア大手の[SK Telecomと提携](http://www.zdnet.com/article/intel-and-sk-telecom-team-up-on-webrtc-iot-devices/)して話題になった。

### Janus

Janus本体はWebRTCゲートウェイであり、libsrtpやlibnice(ICEの実装)を組み合わせて開発されている。各種プラグインを取り込むと、拡張可能であり例えばSFUを実現する[プラグイン](https://janus.conf.meetecho.com/docs/janus__videoroom_8c.html)もある。以前の[記事](http://iwashi.co/2016/03/05/slack-webrtc-analysis.html)でも書いたように、Slackで使われている。

実装はC言語。ライセンスはもともとAGPLだったが、GPLv3に途中から変わった。

### Jitsi VideoBridge

Atlassianに買収されて、開発が続いているJavaのSFU。もともとJitsi自体がXMPP系のプロダクトであるため、Jitsi VideoBridge自体もXMPP拡張である[colibri](http://www.xmpp.org/extensions/inbox/colibri.html)を外部IFとして備えている。RESTの[API](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/rest-videobridge.md)も公開されている。

IETF系の標準化へのコミットも多く、Simulcastを実装したプロダクトとしては、知る限り最速。Jitsiの開発リーダのEmil氏は、[Trickle ICE](https://tools.ietf.org/html/draft-ietf-ice-trickle-03)の著者でもある。

なお、Atlassianプロダクトでも利用されており、それ以外にも http://talky.io/ でも利用されている。

## Kurento

もともとMCU向けに開発されているメデイアサーバ。Kurento自体はC++で実装されており、JS/Node/Java向けのSDKが存在する。開発者はSDKを利用してKurentoを操作可能。この辺りは、[Nodeで操るKurentoメディアサーバー ( Kurento + WebRTC + Node.js )](http://www.slideshare.net/mganeko/nodekurento)が非常に詳しい。現在では、MCU機能だけではなくSFU機能も存在している。

NUBOMEDIAというKurentoのマネージサービスもあるので、自分で運用したくない人はこちらも候補になる。

### Licode

もともとMCUのみだったが、SFUにも対応している。Licode自体はC++で実装されている。前述の通り、Intel CS for WebRTCの内部で利用されている模様。

参考: https://www.terena.org/activities/tf-webrtc/meeting1/slides/Lynckia.pdf

### Meedooze

GitHub公開ではなく、SourceForgeにソースコードがあったりしてちょっと古め?かも。詳細は割愛。

### MediaSoup

私が知る限り、最後発のSFU。内部のコアは[libuv](http://libuv.org/)を利用しつつCで実装されているが、外向けのIFがJavaScript(ECMAScript 6)なのが最大の特徴。まだまだ実装されていない機能も多いが、少なくとも[メディア](https://twitter.com/ibc_tw/status/748848525761536000)は動作しているのがTwitterに貼られている。

```
Can handle RTP packets in JavaScript land
```

というのも謳われていて、JavaScriptから生のRTPを触れる特徴がある。

### PowerMedia XMS

Dialogicが開発している、MCUで有償のみの提供。[ドキュメント](https://www.dialogic.com/en/manuals/xms/xms3.1.aspx)をさっと眺めるとわかるが、MCUとしての機能はだいたい全部入り。

MCUというとビデオのレイアウトが固定されて辛いみたいな話もあるが、昔からある課題であり、[RFC5707](https://tools.ietf.org/html/rfc5707)で標準化もされている。PowerMediaXMSにも、RFC5707は実装されているようなので、おそらく制御できる。

なお、日本ではSoftbank社が利用している。(参考: https://www.dialogic.com/en/company/press-releases/2016/2016-02-17-softbank-deploys-large-scale-webrtc-based-conferencing-application-enabled-by-dialogic.aspx)

### SORA

ここまで述べた中で唯一の日本製(時雨堂製)のSFU。

他のSFUと異なり、ビデオルータとしての機能に加えて、スナップショットを利用してリソース抑制する機能など、ユニークな機能が実装されている。その他の詳細機能は[時雨堂 WebRTC SFU Sora 開発ログ](https://gist.github.com/voluntas/e914aa245fc26f3133c2) を参照。

---------

## 最後に

ここまでメディアサーバの話を書いてきたが、WebRTCはメディアサーバ経由だけではなく、もちろんメディアサーバを介さない通信(P2P/TURN)の形態もある。

P2P/フルメッシュは接続人数がスケールしないのが課題ではあるが、ある程度工夫をすると、WebRTCのAPIは、素で叩くと最高品質での通信を試みるので、負荷が高い。そのため、人数を増やしたい場合は、少し工夫を加えるとP2Pでも接続人数をある程度まで増やせる。[Philipp Hancke](https://twitter.com/hcornflower)氏によれば、[8人同時接続](http://hancke.name/webrtc/great-again/#/28)まではフルメッシュで対応できる。また、双方向通信でなければ、さらに人数を増やすことも可能だ。

それでもユースケースを満たせなければ、メディアサーバを利用するのが良いと個人的には考えている。（どうしても、メディアサーバ分のコストがかかってしまう）

ここまで、書いて力尽きたので、その具体的な方法についてはまた別の機会にでも…。
