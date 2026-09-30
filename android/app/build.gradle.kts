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
        versionCode = 15
        versionName = "0.13.0"

        // Servidor de la cuenta y web (ADR-0026). Se cambian sin tocar el código:
        // ./gradlew assembleDebug -PpldApiUrl=https://otra-api.example -PpldWebUrl=https://... (solo HTTPS)
        val apiUrl = (project.findProperty("pldApiUrl") as String?) ?: "https://pld-api.onrender.com"
        val webUrl = (project.findProperty("pldWebUrl") as String?) ?: "https://marbi8891.github.io/python-learning-dashboard/"
        buildConfigField("String", "API_URL", "\"$apiUrl\"")
        buildConfigField("String", "WEB_URL", "\"$webUrl\"")
    }

    // Una sola fuente de datos: el banco de preguntas y las lecciones de la web (ADR-0011)
    sourceSets["main"].assets.srcDir("../../frontend/data")

    // Firma de release (ADR-0013). La clave nunca está en el repo: la CI la recibe de los
    // secretos de GitHub en variables de entorno. Sin ellas, la release se genera sin firmar.
    val keystore = System.getenv("PLD_KEYSTORE_PATH")?.let(::file)?.takeIf { it.exists() }
    signingConfigs {
        if (keystore != null) {
            create("release") {
                storeFile = keystore
                storePassword = System.getenv("PLD_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("PLD_KEY_ALIAS")
                keyPassword = System.getenv("PLD_KEYSTORE_PASSWORD")
            }
        }
    }

    buildTypes {
        debug {
            // La de depuración convive con la release en el móvil y no la pisa
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
            signingConfig = signingConfigs.findByName("release")
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
    // ViewModel para la práctica (flujo de datos en un solo sentido, ADR-0018)
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20260814")
}
