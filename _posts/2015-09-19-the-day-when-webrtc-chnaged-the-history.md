---
layout: post
title: WebRTCの歴史が変わった日 - ORTC実装の登場
description: ORTC実装の登場によりWebRTCの歴史が変わった日
category: null
tags: []
ogp: /assets/images/ogp/2015-09-19-the-day-when-webrtc-chnaged-the-history_ogp.png
---

ついにマイクロソフトのEdgeチームから、「EdgeでORTCが動作」が公式にアナウンスされた。

[ORTC API is now available in Microsoft Edge](http://blogs.windows.com/msedgedev/2015/09/18/ortc-api-is-now-available-in-microsoft-edge/)

<img src="/assets/imgs/ortc_ms.png" alt="ortc image" class="img-responsive">

既に開発中である旨は以前からアナウンスされていたが、ついに開発者が触れて、デモが見れるレベルにまで到達した。(ORTCがそもそも不明な[過去記事](http://iwashi.co/2015/08/13/ortc-and-webrtc/)を読んでいただければ)

さらに同日マイクロソフトのSkypeチームからも、SkypeでのORTC利用について言及された記事が公開されている。

[Enabling seamless communication experiences for the web with Skype, Skype for Business and Microsoft Edge](https://blogs.office.com/2015/09/18/enabling-seamless-communication-experiences-for-the-web-with-skype-skype-for-business-and-microsoft-edge/)

本ポストでは、上記のブログを読んで気になった点のピックアップおよび、同時に発表されている関連情報をまとめておく。

## ORTC実装で気になったポイント

全体像はマイクロソフトの記事を読んでいただくとして、個人的に気になったポイントはこちら：

- ORTCの各種APIで一部未実装のものもある
  - RTCIceTransportControllerはない
  - RTPListnerがないので、SSRCを自らハンドルしてRTPReceiverに伝えないとダメ
- RTP/RTCP多重化は必須（無いと動かない）
- STUN/TURN/ICEのサポート
  - ICEのaggressive nominationは受信側のみ
- DTLSは1.0ベース(1.2じゃない)
- 映像コーデックはH264UC(Skypeで利用)のみで動作。H264はこれから対応。VP8はもちろん無いけど、Edgeは[VP9をサポートする旨](http://blogs.windows.com/msedgedev/2015/09/08/announcing-vp9-support-coming-to-microsoft-edge/)がすでに発表されてる

## 公式デモ

[ここから](https://dev.modern.ie/testdrive/demos/ortcdemo)確認できる。Edgeが必須なので、試せてない。

## WebRTCとのShim

ORTCは、既存のWebRTCがBlackBox化していたものを、パーツごとに分解して、開発者が組み立てるようにした仕様・実装、とも考えることができる。そのため、ORTCのパーツを組み立てさえすれば、理屈上、WebRTCとの後方互換を保つことが出来る。「理屈の上の話かなぁ」とか思ってたら、既にshim実装してデモを公開している方(WebRTC界隈では有名人の&yetのfippo氏)がいた。

[Shim](https://github.com/fippo/adapter/commit/c7665f54db493a010e57dc94cc50b339f7568037)

ORTCではSDPを明に使わないだけであって、WebRTCと互換するためには自分で書けばいい。なので、上記コードでも書かれている。

[SDPの組み立て](https://github.com/fippo/adapter/commit/c7665f54db493a010e57dc94cc50b339f7568037#diff-07fae4471ea2a21eb6b4dd5eae5de84cR1281)

上記コードのスニペット。実際にChromeとEdgeで相互動作するらしい(未確認)デモがこちら。

[SimpleWebRTC](https://simplewebrtc.com/audio.html)

## JSコード

- ORTCのAPI仕様をざっくり知りたい人は、[ORTC API update](http://www.rtc-conference.com/wp-content/uploads/gravity_forms/2-2f7a537445fa703985ab4d2372ac42ca/2014/10/ORTC_API_Update.pdf)を読むといい。
- 生のJSコードをざっと見たい人は、[webrtcH4cKS: ~ First steps with ORTC](https://webrtchacks.com/first-steps-ortc/)がよくまとまっていてオススメ。

-----

## これからどうなっていくのか？

現行のWebRTCの流れを汲む、WebRTC 1.0に何を入れるのかは決まりつつある。9/9-10にシアトルで開催された[F2Fミーティング](https://www.w3.org/2011/04/webrtc/wiki/September_9_-_10_2015)にて議論されており、10月末に開催されるTPACで合意されると考えられる。

詳細は、ついに募集開始された[次世代Webカンファレンス](http://nextwebconf.connpass.com/event/19699/)で議論したいと考えている。

