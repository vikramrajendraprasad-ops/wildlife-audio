[app]

# (str) Title of your application
title = Wildlife Pro

# (str) Package name
package.name = wildlifeaudio

# (str) Package domain (needed for android/ios packaging)
package.domain = org.wildlife

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,so

# (str) Application versioning
version = 1.0

# (list) Application requirements
# REMOVED ffmpeg to prevent crash. Added 'android' for permissions.
requirements = python3,kivy,kivymd,pillow,android

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# CRITICAL FIX: Added READ_MEDIA_AUDIO for Android 13+ support
android.permissions = INTERNET,WAKE_LOCK,READ_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# --- ANDROID CONFIGURATION ---

# (int) Target Android API (Stable 33)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android NDK version to use
android.ndk = 25b

# (bool) skip_update (Keep 0/False for GitHub Actions)
android.skip_update = 0

# (bool) Accept license automatically
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# (str) ADD YOUR .SO FILE AS A SYSTEM LIBRARY (CRITICAL!)
# This puts it in the correct /lib/ folder so it can run!
android.add_libs_arm64_v8a = libffmpeg_engine.so

# (bool) enables Android auto backup
android.allow_backup = True

[buildozer]

# (int) Log level (2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
