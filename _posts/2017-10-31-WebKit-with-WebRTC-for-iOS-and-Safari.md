---
layout: post
title: WebKit with WebRTC for iOS and Safari 講演から取ったメモ
description: WebKit with WebRTC for iOS and Safari 講演から取ったメモ
category: null
tags: []
ogp: /assets/images/ogp/2017-10-31-WebKit-with-WebRTC-for-iOS-and-Safari_ogp.png
---

本記事は[WebKit with WebRTC for iOS and Safari](https://www.youtube.com/watch?v=4gG5HXVOByY)から取ったメモです。かなり意訳気味にとってるので、何か間違いなどあれば [@iwashi86](https://twitter.com/iwashi86) までお願いします。

- WebRTC 1.0 APIのみサポート
  - Callbackなどはサポートされてない
  - だけど、adapter.jsでレガシーサポートもできる
- Safariのバックエンドはlibwebrtc
  - Chromeと同じバックエンド
- H.264のみ対応、VP8は対応していない
  - VP8は数年でリタイアするだろう、将来的には新しいコーデックも必要となるだろう
  - H.264は効率性の観点で良い。HWAも使えるし
- webkitフレームワーク
  - SafariはRTCPeerConnectionとMediaDevicesも使える
  - AppsはRTCPeerConnectionが使える。MediaDevicesはない。
    - ゲーム開発者にとっては、RTCPeerConnectionだけで便利かもね
- Safariはwebkitはプライバシを重要視している
  - WebRTCはフィンガープリンティングに使われることもあった
    - 本来は必要ない
  - mediaDevicesを複数出すこと自体がフィンガープリンティングに使える
  - getUserMediaで許可を出せば、まぁOKという考え
- Media Capture
  - Cameraは複数Tabを使ったときに、掴んでるのは1つのTab
  - これでUX的には十分
- Videoエレメント 
  - autoplayはあるケースでは使える。たとえばVideoがMuteしてるならOK。
  - playsinline muted なら、ビデオ再生的に問題ない
  - 音声の自動再生は、gUMとってれば自動再生できる
  - または、既に音声が再生されてるならOK
  - どこかクリックしてもらえれば再生される
- テスト
  - WebDriverで、gUMはプロンプト無しで取れる
  - gUMのdenyもテストできる
- WebRTC Logging と Media Logging 機能が開発コンソールにある
  - inspectorモードから見れる
  - するとconsoleに、様々な情報が出るようになる
  - この機能は新しいので、フィードバックがあれば是非欲しい
- WebRTCはかなり複雑なので、シンプルにしていきたい

