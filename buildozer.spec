
[app]

# (str) Title of your application
title = Wildlife Pro

# (str) Package name
package.name = wildlifeaudio

# (str) Package domain
package.domain = org.wildlife

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# NOTE: We DO NOT put 'so' here anymore. It is handled by add_libs below.
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# (str) Application versioning
version = 1.0

# (list) Application requirements
# NOTE: Pure python requirements only. No ffmpeg library.
requirements = python3,kivy,kivymd,pillow,android

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK

# --- ANDROID CONFIGURATION ---

# (int) Target Android API
android.api = 33
android.minapi = 21
android.ndk = 25b
android.skip_update = 0
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

# --- THE CORRECT FIX ---
# This installs the engine into the system's native library folder.
# This prevents the "Permission Denied" crash.
android.add_libs_arm64 = libffmpeg_engine.so

[buildozer]
log_level = 2
warn_on_root = 0
