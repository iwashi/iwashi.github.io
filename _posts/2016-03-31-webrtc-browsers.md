---
layout: post
title: 2016/3末時点のWebRTCブラウザ対応状況まとめ
description: 2016/3末時点のWebRTCブラウザ対応状況まとめ
category: null
tags: []
ogp: /assets/images/ogp/2016-03-31-webrtc-browsers_ogp.png
---

## はじめに

WebRTCは様々なブラウザでサポートが進んでいる。これらの対応状況について世の中に多くの情報があるが、アップデートされていない情報も多いため、最新の情報を追うのはなかなか骨が折れる。そこで、本記事では2016年3末時点での対応状況をまとめていく。

### 本記事を読むと得られるもの・得られないもの

- 得られるもの
  - 2016年3末時点での各ブラウザにおけるWebRTCの対応状況
- 得られないもの
  - ソースコードレベルの実装詳細

### 対象読者

- WebRTCに関わっているエンジニア、WebRTCの動向に興味がある人
- WebRTCを多少なりとも知っている人

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

## Google Chrome

WebRTCの提唱をはじめたGoogleだけあって、WebRTCの黎明期から様々な機能を提供している。現在も活発に開発が進んでおり、[Chrome/FirefoxにおけるWebRTCのマイルストーン](http://qiita.com/goforbroke/items/d871ccdf4bb91674d3ea)の記事に項目がまとまっている。

### 映像コーデック

これらの中でも特筆すべきは、H.264コーデックのサポートだ。WebRTCの映像コーデックは、IETFの場でプロレスのような議論があり、最終的にVP8とH.264の両方の実装がmandatoryであるという結論になった。Chromeもそれに準じており、当初はVP8のみのサポートであったものの、最新の開発版ChromeにてH.264がフラグ付きで利用可能になった。ただし、ソフトウェアコーデックのみのサポートである。H.264を利用できるようになると何が嬉しいかというと、特にiOSのようにH264のHWエンコーダ・デコーダがある端末は処理負荷を非常に下げられる点がある。

また、コーデックで言えばVP9の対応も開始している。VP9はVP8に比べ、消費帯域が少ないが、処理コストは高く微妙にレイテンシが上がる、という特性がある。詳細は[この動画](https://www.youtube.com/watch?v=ziGjqMFtz5g)内部で説明されているので参照されたい。

### WebRTC API

[W3C側のドキュメント](https://w3c.github.io/webrtc-pc/)にて、ORTC由来のAPIが多く規定されはじめている。ただし、ブラウザでの実装はまだまだ進んでおらず、特にChromeで利用できるものはほとんどない。（後述するFirefoxのが進んでいる）

## Firefox

Chrome同様にWebRTCを利用できるブラウザである。WebRTCの実装面でいえば、より標準(IETF、W3C)に近い形で実装が進んでいるのがFirefoxだ。たとえば、RTPSenderというAPIなどが既に実装されており、Chromeより進んでいる。

Firefoxで特筆すべきは、Simulcastへの対応だ。すでに[リリースノート](https://wiki.mozilla.org/Media/WebRTC/ReleaseNotes/47)にも多く登場しており、 pref設定によってDev版のFirefoxで利用できる。詳細は[
WebRTC in Firefox - Kranky Geek, Bangalore](https://speakerdeck.com/kaustavdm/webrtc-in-firefox-kranky-geek-bangalore)を参照願いたい。

## Microsoft Edge

Windowsの新ブラウザであるEdgeは、WebRTCに先行してORTC版の機能を実装している。ORTCは、[以前の記事](http://iwashi.co/2015/09/19/the-day-when-webrtc-chnaged-the-history)で書いたように、WebRTCの各要素を低レイヤで切り出した仕様であり、ORTCの部品を組合せることによって、WebRTC1.0の仕様(現在のChrome/Firefoxのサポートする仕様)と相互通信できる。

そのEdgeに関して、個人的に驚くべきニュースだったのは、[WebRTC 1.0](https://wpdev.uservoice.com/forums/257854-microsoft-edge-developer/suggestions/6508336-webrtc-webrtc-v1-0-api?tracking_code=5a4923d8ab9f11759e40c4044dd36d91)の開発をはじめたことだ。当初はORTCを組み合わせたshimのような部品を利用しなければ、Chrome/Firefoxと通信できなかった。しかし、開発が完了すればSDPを利用できることになり、shim無しでChrome/Firefoxと相互接続可能になる。

ただし、MS Edgeのサポートする映像コーデックはChromeやFirefoxの提供するH.264とやや違っており、映像通信はまだできない。

## IE

[プラグイン](https://temasys.atlassian.net/wiki/display/TWPP/WebRTC+Plugins)を利用すればWebRTCを使える。

## Safari

IE同様に、[プラグイン](https://temasys.atlassian.net/wiki/display/TWPP/WebRTC+Plugins)を利用すればWebRTCを使えるが、Safariにはかなり光がある。[How to Test / Evaluate WebRTC in Safari ?](http://webrtcbydralex.com/index.php/2016/02/29/webrtc-in-safari-a-follow-up/)で説明されているように、すでに一部のWebRTC APIは姿を見せ始めている。たとえばgetUserMediaはnightly版で存在するものの、Permission画面が出ないため使えない。

ちなみに、SafariはWebkitにApple製のGUIをかぶせて、機能を削ったものであり、webkit自体にはWebRTCの実装がかなり進んでいる。あとはApple次第。ちなみに、[Safari Technology Preview](http://japanese.engadget.com/2016/03/31/safari-technology-preview-mac-app-store/)が始まったので、これで早く使えないかな、と期待している。

## まとめ

2016/3末時点での各ブラウザにおけるWebRTCの対応についてまとめた。おそらく1年後に書いたら、まるっと内容が変わってるだろう。。。
