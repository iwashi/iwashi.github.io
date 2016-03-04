---
layout: post
title: "cloudmonkeyでunknonw url type httpsが出るときの対応"
description: "cloudmonkeyでunknonw url type httpsが出るときの対応方針の説明"
category: 
tags: []
---

## cloudmonkeyでunknonw url type httpsが出るときの対応

Yosemiteにした後に、ひさびさにCloudmonkeyを起動したら、以下の通り怒られた。

```
cloudmonkey
☁ Apache CloudStack 🐵 cloudmonkey 5.1.0. Type help or ? to list commands.

> list networks
unknown url type: https

```

これはpythonのバージョンだったり、OpenSSLだったりが原因。brew使いなら

```
$ brew upgrade python
```

を実行すれば途中でopenSSLも落ちてくるので万事解決。
