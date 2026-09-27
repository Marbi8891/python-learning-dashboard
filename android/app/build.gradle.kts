plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "io.github.marbi8891.pld"
    compileSdk = 36

    defaultConfig {
        applicationId = "io.github.marbi8891.pld"
        minSdk = 26
        targetSdk = 36
        versionCode = 2
        versionName = "0.2.0"

        // Configuración en un solo sitio, no repartida por el código
        buildConfigField("String", "WEB_URL", "\"https://marbi8891.github.io/python-learning-dashboard/\"")
    }

    // Una sola fuente de datos: el banco de preguntas y las lecciones de la web (ADR-0011)
    sourceSets["main"].assets.srcDir("../../frontend/data")

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    testOptions {
        // org.json forma parte de Android: en los tests de JVM se usa la implementación de referencia
        unitTests.isReturnDefaultValues = true
    }
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.06.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.10.1")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20250517")
}
