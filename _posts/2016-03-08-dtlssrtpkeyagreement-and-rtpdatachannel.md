---
layout: post
title: "DtlsSrtpKeyAgreement および RtpDataChannel についての記録"
description: ""
category: 
tags: []
---

## この文書 is 何？

- すでに使われていない RtpDataChannel と DtlsSrtpKeyAgreement について忘れ去る前に歴史の経緯を記録しておく文書
  - 将来どこかでこのパラメータを見かけて、「なんだったっけ？」と思ったら見返すためのドキュメント
- なお両パラメータとも、すでにobsoleteなのでコーディングで書く必要はない

## RtpDataChannel とは？

WebRTCは歴史的に、メディアチャネル側の実装が先に進んだ。データチャネルの思想自体は最初からあったものの、DTLS-SCTPを利用すると最初から決定されているわけではなかった。その当時に、最初に実装されたのがRTPを用いたデータチャネル実装である。この実装を利用するのを明示的に指定するためのオプションが `RtpDataChannel` であり、 `RTCPeerConnection` のオプションに渡す。オプションは、以下のように指定して用いる：

```js
{
  RtpDataChannel: true
}
```

## DtlsSrtpKeyAgreement とは？

WebRTCのP2P間での暗号方式は、SDES/SRTPおよびDTLS/SRTPが候補にあり、IETF87にてDTLS/SRTPが決定された。SDESよりDTLS/SRTPが良い理由を簡単に述べると、DTLS/SRTPは鍵情報がSDPに乗らない点がある。結果として、DTLS-SRTP利用時に仮に、シグナリング情報が暗号化されておらず漏れた場合としても、被害が抑えられるという可能性が高い(*1)。

DTLS/SRTPを優先的に使うか指定するためのオプションが標題の `DtlsSrtpKeyAgreement` である。`RTCPeerConnection` のオプションであり、以下のように用いる：

```js
{
  DtlsSrtpKeyAgreement:true
}
```

*1: シグナリングサーバでMan in the Middleされた場合は、完全に全て漏れるのでDTLS-SRTPにも限界がある。その課題解決のためにZRTPがある。
