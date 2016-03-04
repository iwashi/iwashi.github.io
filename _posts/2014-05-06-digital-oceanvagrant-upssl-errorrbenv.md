---
layout: post
title: "Digital Oceanのvagrant upでSSL errorが出た時の対応"
description: ""
category: 
tags: []
---

## Digital Oceanをvagrant upするときにSSLで怒られたときの対応

Digital Ocean利用時に、vagrantからdropletsを作成しようとしたときに、以下のエラーが出る場合がある。これはdigital oceanはあまり関係なくて、ruby側がSSLの証明書をうまいこと認識できてないのが問題。

ちなみにrubyはrbenvで入れた``ruby 2.1.1p76 (2014-02-24 revision 45161) [x86_64-darwin13.0]``。

```
$ vagrant up --provider=digital_ocean
 43 # The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
Bringing machine 'default' up with 'digital_ocean' provider...
/Applications/Vagrant/embedded/lib/ruby/1.9.1/net/http.rb:800:in `connect': SSL_connect returned=1 errno=0 state=SSLv3 read server certificate B: certificate verify failed (Faraday::SSLError)
	from /Applications/Vagrant/embedded/lib/ruby/1.9.1/net/http.rb:800:in `block in connect'
	from /Applications/Vagrant/embedded/lib/ruby/1.9.1/timeout.rb:55:in `timeout'
	from /Applications/Vagrant/embedded/lib/ruby/1.9.1/timeout.rb:100:in `timeout'
	... 以下省略 ...
```


### brew install curl-ca-bundleは不正解
そこで、ググると ``brew install curl-ca-bundle``してみなよ、というアドバイスがあるが、そもそもbrewのformulaから既にcurl-ca-bundleは消されているので以下のようにNGがでる。
公式の<https://github.com/smdahlen/vagrant-digitalocean/blob/master/README.md>は古い

参考：<https://github.com/jacknagel/homebrew/commit/5384eb3bc023ced4db69d091a85995514dcec3b2>

```
$ brew install curl-ca-bundle
Error: No available formula for curl-ca-bundle
Searching taps...
```

### 正解は、

```
$ ruby -ropenssl -e "p OpenSSL::X509::DEFAULT_CERT_FILE"
"/usr/local/etc/openssl/cert.pem"
```

で、出てきたcert.pemへのPATHを、以下のように.zshrcへ追加する。

```
export SSL_CERT_FILE=/usr/local/etc/openssl/cert.pem
```

あとは

```
$ vagrant up --provider=digital_ocean
```

で上手くいくはず。


###  おまけ
使い終わったら忘れずに、 ``vagrant destroy``しておこう。無駄に課金されないように。


### おまけ２
`` Cent OS 6.5 x64`` は、rsyncがデフォルトで入っていないので、/Vagrant　がそのままでは同期されない。そこで、

```
$ vagrant ssh
# yum -y install rsync
Ctrl + D で抜けて
$ vagrant reload
```

しておけばOK。