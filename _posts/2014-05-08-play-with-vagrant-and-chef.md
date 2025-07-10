---
layout: post
title: Play with Vagrant and Chef
description: ''
category: null
tags: []
ogp: /assets/images/ogp/2014-05-08-play-with-vagrant-and-chef_ogp.png
---

# VagrantとChefをさわっているときのメモ

VagrantとChefでの手順や対応等を以下でメモする。

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

## vagrant up時にguest additionsの警告

Vagrant up時に以下の警告がでたときは

```
$ vagrant up
[default] The guest additions on this VM do not match the installed version of
VirtualBox! In most cases this is fine, but in rare cases it can
cause things such as shared folders to not work properly. If you see
shared folder errors, please update the guest additions within the
virtual machine and reload your VM.
```

Guest Additionsが古かったりするので、自動更新してくれるPluginを入れて対応する。

```
$ vagrant plugin install vagrant-vbguest
$ vagrant vbguest
```

ちなみに、

```
Installing the Window System drivers[FAILED]
(Could not find the X.Org or XFree86 Window System.)
An error occurred during installation of VirtualBox Guest Additions 4.3.2. Some functionality may not work as intended.
```

は、Xを使うことがなければ、考えなくてオーケー。

## vagrantとsahara

```
// 前準備(VirtualBoxとVagrantのインストール済みの前提)
$ vagrant plugin install sahara
$ vagrant plugin install vagrant-vbguest

// Localマシーンにて
$ vagrant box add centos6.3_64 https://s3.amazonaws.com/itmat-public/centos-6.3-chef-10.14.2.box
Downloading or copying the box...
Extracting box...te: 655k/s, Estimated time remaining: 0:00:01))
Successfully added box 'centos6.3_64' with provider 'virtualbox'!

$ vim Vagrantfile
# config.vm.network :private_network, ip: "192.168.33.10"
をコメントイン
config.vm.network :private_network, ip: "192.168.33.10"

$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
[default] Importing base box 'centos6.3_64'...
[default] Matching MAC address for NAT networking...
[default] Setting the name of the VM...
[default] Clearing any previously set forwarded ports...
[default] Creating shared folders metadata...
[default] Clearing any previously set network interfaces...
[default] Preparing network interfaces based on configuration...
[default] Forwarding ports...
[default] -- 22 => 2222 (adapter 1)
[default] Booting VM...
[default] Waiting for machine to boot. This may take a few minutes...
[default] Machine booted and ready!
GuestAdditions versions on your host (4.3.10) and guest (4.1.22) do not match.
Loaded plugins: fastestmirror, presto
Determining fastest mirrors
 * base: www.ftp.ne.jp
 * extras: www.ftp.ne.jp
 * updates: www.ftp.ne.jp
Setting up Install Process
Package 1:make-3.81-20.el6.x86_64 already installed and latest version
Resolving Dependencies
--> Running transaction check
---> Package gcc.x86_64 0:4.4.6-4.el6 will be updated
--> Processing Dependency: gcc = 4.4.6-4.el6 for package: gcc-c++-4.4.6-4.el6.x86_64
---> Package gcc.x86_64 0:4.4.7-4.el6 will be an update
--> Processing Dependency: libgomp = 4.4.7-4.el6 for package: gcc-4.4.7-4.el6.x86_64
--> Processing Dependency: cpp = 4.4.7-4.el6 for package: gcc-4.4.7-4.el6.x86_64
--> Processing Dependency: libgcc >= 4.4.7-4.el6 for package: gcc-4.4.7-4.el6.x86_64
---> Package perl.x86_64 4:5.10.1-127.el6 will be updated
--> Processing Dependency: perl = 4:5.10.1-127.el6 for package: 1:perl-Module-Pluggable-3.90-127.el6.x86_64
--> Processing Dependency: perl = 4:5.10.1-127.el6 for package: 1:perl-Pod-Simple-3.13-127.el6.x86_64
--> Processing Dependency: perl = 4:5.10.1-127.el6 for package: 4:perl-libs-5.10.1-127.el6.x86_64
--> Processing Dependency: perl = 4:5.10.1-127.el6 for package: 3:perl-version-0.77-127.el6.x86_64
--> Processing Dependency: perl = 4:5.10.1-127.el6 for package: 1:perl-Pod-Escapes-1.04-127.el6.x86_64
---> Package perl.x86_64 4:5.10.1-136.el6 will be an update
--> Running transaction check
---> Package cpp.x86_64 0:4.4.6-4.el6 will be updated
---> Package cpp.x86_64 0:4.4.7-4.el6 will be an update
---> Package gcc-c++.x86_64 0:4.4.6-4.el6 will be updated
---> Package gcc-c++.x86_64 0:4.4.7-4.el6 will be an update
--> Processing Dependency: libstdc++-devel = 4.4.7-4.el6 for package: gcc-c++-4.4.7-4.el6.x86_64
--> Processing Dependency: libstdc++ = 4.4.7-4.el6 for package: gcc-c++-4.4.7-4.el6.x86_64
---> Package libgcc.x86_64 0:4.4.6-4.el6 will be updated
---> Package libgcc.x86_64 0:4.4.7-4.el6 will be an update
---> Package libgomp.x86_64 0:4.4.6-4.el6 will be updated
---> Package libgomp.x86_64 0:4.4.7-4.el6 will be an update
---> Package perl-Module-Pluggable.x86_64 1:3.90-127.el6 will be updated
---> Package perl-Module-Pluggable.x86_64 1:3.90-136.el6 will be an update
---> Package perl-Pod-Escapes.x86_64 1:1.04-127.el6 will be updated
---> Package perl-Pod-Escapes.x86_64 1:1.04-136.el6 will be an update
---> Package perl-Pod-Simple.x86_64 1:3.13-127.el6 will be updated
---> Package perl-Pod-Simple.x86_64 1:3.13-136.el6 will be an update
---> Package perl-libs.x86_64 4:5.10.1-127.el6 will be updated
---> Package perl-libs.x86_64 4:5.10.1-136.el6 will be an update
---> Package perl-version.x86_64 3:0.77-127.el6 will be updated
---> Package perl-version.x86_64 3:0.77-136.el6 will be an update
--> Running transaction check
---> Package libstdc++.x86_64 0:4.4.6-4.el6 will be updated
---> Package libstdc++.x86_64 0:4.4.7-4.el6 will be an update
---> Package libstdc++-devel.x86_64 0:4.4.6-4.el6 will be updated
---> Package libstdc++-devel.x86_64 0:4.4.7-4.el6 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

================================================================================
 Package                    Arch        Version                 Repository
                                                                           Size
================================================================================
Updating:
 gcc                        x86_64      4.4.7-4.el6             base       10 M
 perl                       x86_64      4:5.10.1-136.el6        base       10 M
Updating for dependencies:
 cpp                        x86_64      4.4.7-4.el6             base      3.7 M
 gcc-c++                    x86_64      4.4.7-4.el6             base      4.7 M
 libgcc                     x86_64      4.4.7-4.el6             base      101 k
 libgomp                    x86_64      4.4.7-4.el6             base      118 k
 libstdc++                  x86_64      4.4.7-4.el6             base      293 k
 libstdc++-devel            x86_64      4.4.7-4.el6             base      1.6 M
 perl-Module-Pluggable      x86_64      1:3.90-136.el6          base       40 k
 perl-Pod-Escapes           x86_64      1:1.04-136.el6          base       32 k
 perl-Pod-Simple            x86_64      1:3.13-136.el6          base      212 k
 perl-libs                  x86_64      4:5.10.1-136.el6        base      578 k
 perl-version               x86_64      3:0.77-136.el6          base       51 k

Transaction Summary
================================================================================
Upgrade      13 Package(s)

Total download size: 32 M
Downloading Packages:
Setting up and reading Presto delta metadata
Processing delta metadata
Package(s) data still to download: 32 M
--------------------------------------------------------------------------------
Total                                           2.7 MB/s |  32 MB     00:11
Running rpm_check_debug
Running Transaction Test
Transaction Test Succeeded
Running Transaction
  Updating   : libgcc-4.4.7-4.el6.x86_64                                   1/26
  Updating   : libstdc++-4.4.7-4.el6.x86_64                                2/26
  Updating   : libstdc++-devel-4.4.7-4.el6.x86_64                          3/26
  Updating   : 1:perl-Pod-Escapes-1.04-136.el6.x86_64                      4/26
  Updating   : 3:perl-version-0.77-136.el6.x86_64                          5/26
  Updating   : 1:perl-Pod-Simple-3.13-136.el6.x86_64                       6/26
  Updating   : 4:perl-libs-5.10.1-136.el6.x86_64                           7/26
  Updating   : 1:perl-Module-Pluggable-3.90-136.el6.x86_64                 8/26
  Updating   : 4:perl-5.10.1-136.el6.x86_64                                9/26
  Updating   : libgomp-4.4.7-4.el6.x86_64                                 10/26
  Updating   : cpp-4.4.7-4.el6.x86_64                                     11/26
  Updating   : gcc-4.4.7-4.el6.x86_64                                     12/26
  Updating   : gcc-c++-4.4.7-4.el6.x86_64                                 13/26
  Cleanup    : gcc-c++-4.4.6-4.el6.x86_64                                 14/26
  Cleanup    : libstdc++-devel-4.4.6-4.el6.x86_64                         15/26
  Cleanup    : 1:perl-Pod-Escapes-1.04-127.el6.x86_64                     16/26
  Cleanup    : 1:perl-Pod-Simple-3.13-127.el6.x86_64                      17/26
  Cleanup    : 3:perl-version-0.77-127.el6.x86_64                         18/26
  Cleanup    : 4:perl-libs-5.10.1-127.el6.x86_64                          19/26
  Cleanup    : 4:perl-5.10.1-127.el6.x86_64                               20/26
  Cleanup    : 1:perl-Module-Pluggable-3.90-127.el6.x86_64                21/26
  Cleanup    : gcc-4.4.6-4.el6.x86_64                                     22/26
  Cleanup    : libstdc++-4.4.6-4.el6.x86_64                               23/26
  Cleanup    : libgcc-4.4.6-4.el6.x86_64                                  24/26
  Cleanup    : cpp-4.4.6-4.el6.x86_64                                     25/26
  Cleanup    : libgomp-4.4.6-4.el6.x86_64                                 26/26
  Verifying  : 1:perl-Module-Pluggable-3.90-136.el6.x86_64                 1/26
  Verifying  : 4:perl-5.10.1-136.el6.x86_64                                2/26
  Verifying  : gcc-4.4.7-4.el6.x86_64                                      3/26
  Verifying  : libstdc++-4.4.7-4.el6.x86_64                                4/26
  Verifying  : libstdc++-devel-4.4.7-4.el6.x86_64                          5/26
  Verifying  : cpp-4.4.7-4.el6.x86_64                                      6/26
  Verifying  : 1:perl-Pod-Simple-3.13-136.el6.x86_64                       7/26
  Verifying  : gcc-c++-4.4.7-4.el6.x86_64                                  8/26
  Verifying  : libgomp-4.4.7-4.el6.x86_64                                  9/26
  Verifying  : 3:perl-version-0.77-136.el6.x86_64                         10/26
  Verifying  : 1:perl-Pod-Escapes-1.04-136.el6.x86_64                     11/26
  Verifying  : 4:perl-libs-5.10.1-136.el6.x86_64                          12/26
  Verifying  : libgcc-4.4.7-4.el6.x86_64                                  13/26
  Verifying  : 1:perl-Pod-Simple-3.13-127.el6.x86_64                      14/26
  Verifying  : 3:perl-version-0.77-127.el6.x86_64                         15/26
  Verifying  : cpp-4.4.6-4.el6.x86_64                                     16/26
  Verifying  : 4:perl-5.10.1-127.el6.x86_64                               17/26
  Verifying  : 1:perl-Pod-Escapes-1.04-127.el6.x86_64                     18/26
  Verifying  : gcc-c++-4.4.6-4.el6.x86_64                                 19/26
  Verifying  : libstdc++-devel-4.4.6-4.el6.x86_64                         20/26
  Verifying  : libstdc++-4.4.6-4.el6.x86_64                               21/26
  Verifying  : 1:perl-Module-Pluggable-3.90-127.el6.x86_64                22/26
  Verifying  : gcc-4.4.6-4.el6.x86_64                                     23/26
  Verifying  : 4:perl-libs-5.10.1-127.el6.x86_64                          24/26
  Verifying  : libgomp-4.4.6-4.el6.x86_64                                 25/26
  Verifying  : libgcc-4.4.6-4.el6.x86_64                                  26/26

Updated:
  gcc.x86_64 0:4.4.7-4.el6             perl.x86_64 4:5.10.1-136.el6

Dependency Updated:
  cpp.x86_64 0:4.4.7-4.el6
  gcc-c++.x86_64 0:4.4.7-4.el6
  libgcc.x86_64 0:4.4.7-4.el6
  libgomp.x86_64 0:4.4.7-4.el6
  libstdc++.x86_64 0:4.4.7-4.el6
  libstdc++-devel.x86_64 0:4.4.7-4.el6
  perl-Module-Pluggable.x86_64 1:3.90-136.el6
  perl-Pod-Escapes.x86_64 1:1.04-136.el6
  perl-Pod-Simple.x86_64 1:3.13-136.el6
  perl-libs.x86_64 4:5.10.1-136.el6
  perl-version.x86_64 3:0.77-136.el6

Complete!
Copy iso file /Applications/VirtualBox.app/Contents/MacOS/VBoxGuestAdditions.iso into the box /tmp/VBoxGuestAdditions.iso
Installing Virtualbox Guest Additions 4.3.10 - guest version is 4.1.22
Verifying archive integrity... All good.
Uncompressing VirtualBox 4.3.10 Guest Additions for Linux............
VirtualBox Guest Additions installer
Removing installed version 4.1.22 of VirtualBox Guest Additions...
Copying additional installer modules ...
Installing additional modules ...
Removing existing VirtualBox non-DKMS kernel modules[  OK  ]
Building the VirtualBox Guest Additions kernel modules
Building the main Guest Additions module[  OK  ]
Building the shared folder support module[  OK  ]
Building the OpenGL support module[  OK  ]
Doing non-kernel setup of the Guest Additions[  OK  ]
You should restart your guest to make sure the new modules are actually used

Installing the Window System drivers
Could not find the X.Org or XFree86 Window System, skipping.
An error occurred during installation of VirtualBox Guest Additions 4.3.10. Some functionality may not work as intended.
In most cases it is OK that the "Window System drivers" installation failed.
Restarting VM to apply changes...
[default] Attempting graceful shutdown of VM...
[default] Booting VM...
[default] Waiting for machine to boot. This may take a few minutes...
[default] Machine booted and ready!
[default] Configuring and enabling network interfaces...
[default] Mounting shared folders...
[default] -- /vagrant

// ssh設定の書き出し。以後、 ssh hogesv でアクセスOK。
$ vagrant ssh-config --host hogesv >> ~/.ssh/config
```

## rvmでchef
chef-soloをサーバ上で実行する際に、rvmを使っていると以下のエラーが出ることがある。
上手いことgemを認識していないので、``rvm reset``で再認識させてあげよう。

```
$ sudo chef-solo -c solo.rb -j ./localhost.json
/home/vagrant/.rvm/rubies/ruby-1.9.3-p545/lib/ruby/site_ruby/1.9.1/rubygems/dependency.rb:298:in `to_specs': Could not find 'chef' (>= 0) among 12 total gem(s) (Gem::LoadError)
	from /home/vagrant/.rvm/rubies/ruby-1.9.3-p545/lib/ruby/site_ruby/1.9.1/rubygems/dependency.rb:309:in `to_spec'
	from /home/vagrant/.rvm/rubies/ruby-1.9.3-p545/lib/ruby/site_ruby/1.9.1/rubygems/core_ext/kernel_gem.rb:53:in `gem'
	from /home/vagrant/.rvm/gems/ruby-1.9.3-p545/bin/chef-solo:22:in `<main>'
	from /home/vagrant/.rvm/gems/ruby-1.9.3-p545/bin/ruby_executable_hooks:15:in `eval'

$ rvm reset
```
