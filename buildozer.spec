[app]

# (str) Title of your application
title = Wildlife Audio

# (str) Package name
package.name = wildlifeaudio

# (str) Package domain (needed for android/ios packaging)
package.domain = org.wildlife

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# --- THE MISSING LINE WAS HERE ---
version = 0.1
# ---------------------------------

# (list) Application requirements
requirements = python3,kivy,kivymd,ffpyplayer,pillow,android

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android NDK version to use
android.ndk = 25b

# (bool) Skip updates to avoid the loop
android.skip_update = 1

# (bool) Accept license automatically
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup
android.allow_backup = True

[buildozer]

# (int) Log level (2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
