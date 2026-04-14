[app]

# (str) Title of your application
title = Khanz Academy

# (str) Package name
package.name = khanzacademy

# (str) Package domain (needed for android/ios packaging)
package.domain = org.khanzacademy

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,json,db

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .git, __pycache__

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# Comma-separated e.g. requirements = python3,kivy
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pillow, PyPDF2

# (str) Custom source folders for requirements
# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/images/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/images/logo.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author == string - One or more author/manager strings
# c.ios.deployment_target = 9.0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin


#   Android specific

# (str) Android NDK version to use
android.ndk = 23b

# (int) Android SDK API to use
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to prevent Buildozer from upgrading the Android SDK
# when building offline. Default: False
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the SDK license agreements will normally need to be accepted through
# the Android SDK tools.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

# (list) Copy these files/dirs to the OEBPS/Text folder
# (a.k.a. the files accessible via context.getExternalFilesDir())
#android.add_src =

# (list) Java classes to add in android.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) Add Java files (to be compiled with main file by gradle)
#android.add_java_files = org/kivy/android/SomeAndroidJavaClass.java

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.gradle_dependencies
# android.enable_androidx = False

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = JavaVersion.VERSION_1_8", "targetCompatibility = JavaVersion.VERSION_1_8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# please enclose in double quotes
# e.g. android.gradle_repositories = "maven { url 'https://kotlin.bintray.com/ktor' }"
#android.gradle_repositories =

# (list) packaging options to add
# see https://google.github.io/android-gradle-dsl/current/com.android.build.gradle.internal.dsl.PackagingOptions.html
# can be necessary to solve conflicts in gradle_dependencies
# e.g. android.add_packaging_options = "exclude 'META-INF/common.kotlin_module'", "exclude 'META-INF/*.kotlin_module'"
#android.add_packaging_options =

# (list) Java classes to add as activities to the manifest.
#android.add_activites = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android64/*.so
#android.add_libs_x86 = libs/android86/*.so
#android.add_libs_mips = libs/androidmips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# temporary directory and added into the build)
#android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml
# using <uses-library> tag
#android.uses_library =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) Android target API level
android.target_api = 33

#
# Android Release (how to get the .apk signed)
#

# (str) Filename of the keystore file in order to sign the release builds
# android.keystore = ~/.keystore

# (str) Alias name in the keystore
# android.keyalias = mykey

# (str) Password for the keystore
# android.keystore_passwd = mysecret

# (str) Password for the key
# android.keyalias_passwd = mysecret

# (str) Filename of the Bluetooth stack binary (if using bluetooth)
#android.btstack_path = /path/to/btstack

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (str) Set the presplash lottie file
#android.presplash_lottie = "path/to/lottie/file.json"

# (bool) Activate incremental build (only with Eclipse build)
#android.incremental = False

# (bool) If True, then automatically sign the apk for release
#android.sign_release = False

# Android permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Another platform-specific option. Extra ios frameworks to link
ios.frameworks = OpenGLES, QuartzCore, CoreGraphics, AVFoundation, CoreText, CFNetwork

# (list) iOS dependencies (must be a list of framework names)
#ios.pods_dependencies =

# (str) iOS codesign identity
#ios.codesign.identity =

# (str) iOS codesign identity (debug)
#ios.codesign.debug = 'iPhone Developer'

# (str) iOS codesign identity (release)
#ios.codesign.release = %(ios.codesign.debug)s
