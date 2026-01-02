
[app]
title = Wildlife Pro
package.name = wildlifeaudio
package.domain = org.wildlife
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

version = 1.0

# CRITICAL: Includes 'pyjnius' to prevent crashes
requirements = python3,kivy,kivymd,pillow,android,pyjnius

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK

android.api = 33
android.minapi = 21
android.ndk = 25b
android.skip_update = 0
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

# ENGINE INSTALLER
android.add_libs_arm64 = libffmpeg_engine.so

[buildozer]
log_level = 2
warn_on_root = 0
