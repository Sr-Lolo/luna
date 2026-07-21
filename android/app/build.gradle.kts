plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val keystoreFile = file("../luna.keystore")

android {
    namespace = "com.luna.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.luna.app"
        minSdk = 26
        targetSdk = 36
        versionCode = (System.currentTimeMillis() / 1000L - 1700000000L).toInt() + 100000
        versionName = "1.8.0"
    }

    signingConfigs {
        create("luna") {
            storeFile = keystoreFile
            storePassword = System.getenv("LUNA_STORE_PASS") ?: "lunaluna"
            keyAlias = System.getenv("LUNA_KEY_ALIAS") ?: "luna"
            keyPassword = System.getenv("LUNA_KEY_PASS") ?: "lunaluna"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("luna")
        }
        debug {
            signingConfig = signingConfigs.getByName("luna")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.webkit:webkit:1.9.0")
    implementation("com.journeyapps:zxing-android-embedded:4.3.0")
    implementation("com.google.zxing:core:3.5.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("com.google.android.material:material:1.11.0")
    implementation("io.coil-kt:coil:2.6.0")
    implementation("io.coil-kt:coil-gif:2.6.0")
}
