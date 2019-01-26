---
layout: post
title: "SkyWay Media Pipeline Factory from the point view of an enginner"
description: "The perspective of SkyWay Media Pipeline Factory is described from the point view of engineer"
category: 
tags: []
---

Jan 23rd 2019, NTT Communications launched [SkyWay Media Pipeline Factory](https://webrtc.ecl.ntt.com/m-pipe/). The official news release is found at [NTT Com’s web page](https://www.ntt.com/en/about-us/press-releases/news/article/2019/0123.html). The article is described for not only engineers but also business people, which leads to lack of some interesting tech aspects. As one of engineers who’s working on WebRTC, I’d like to add two perspectives to the SkyWay Media Pipeline Factory. Note that these perspectives are not official but just personal ones. 

<img src="/assets/images/mpipe.jpg" alt="the official image of SkyWay Media Pipeline Factory" class="img-responsive">

## 1. Managed SkyWay WebRTC Gateway in docker container, containing libwebrtc inside

The core component of SkyWay Media Pipeline Factory is [SkyWay WebRTC Gateway](https://github.com/skyway/skyway-webrtc-gateway). SkyWay WebRTC Gateway is built on the top of [libwebrtc](https://webrtc.googlesource.com/src). 

As you know, libwebrtc itself doesn’t provide signaling function. However, because SkyWay WebRTC Gateway depends on [SkyWay](https://webrtc.ecl.ntt.com/), a WebRTC platform, users of SkyWay WebRTC Gateway don't need to prepare signaling mechanism. Also they don’t need to operate some servers like STUN adn TURN servers. Again this is because SkyWay is already providing them.

Also libwebrtc is basically for browsers. libwebrtc exposes APIs like `SetRemoteDescription` which can be found in the [source code](https://webrtc.googlesource.com/src/+/master/api/peer_connection_interface.h). However, some developers want to use lower level API for implement what they wants with fine-grained way. This trend is similar to what WebRTC NV is evolving. SkyWay WebRTC Gateway provides lower level API; developers can send and receive raw RTP from/to SkyWay WebRTC Gateway and control it via REST API. This usage is kind of similar to [janus-gateway](https://github.com/meetecho/janus-gateway). 

One issue that developers encounter during using SkyWay WebRTC Gateway is it's kind of troublesome for you to operate this. You need to prepare the virtual machine or container if you'd like to deploy server-side component. What SkyWay Media Pipeline Factory is great is it manages SkyWay WebRTC Gateway instead of developers, which means they can focus on what they want to realize.

## 2. Serverless architecture

Another issue when you make use of SkyWay WebRTC Gateway is that you need to operate the process of SkyWay WebRTC Gateway regularly. It may costs you a lot even if the traffic is lower than your expectation.

Because SkyWay Media Pipeline Factory is provided as serverless model, As with FaaS like AWS lambda the payment model will be pay-as-you-go. Note that the status of SkyWay Media Pipeline Factory is trial and everyone can use it for free. Again, note that this is just my guess and my hope. :P

Another advantage of serverless architecture is that you can insert your own component in managed style. Your original logic will be spawned by SkyWay Media Pipeline Factory and lives in container. you just focus on your core value.

## Future...

To the best of my knowledge, there's no similar service to SkyWay Media Pipeline Factory. I really like the concepts because it alleviates the developer's pain.

Personally I hope that the components will be developed by lots of developers, that the ecosystem is created by community, and the service itself will be commercialized service!
