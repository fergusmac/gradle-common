apply(plugin = "maven-publish")
apply(plugin = "java")

val logback_version = "1.4.11"
val oshai_logging_version = "5.1.0"
val kdatetime_version = "0.4.1"

project.repositories {
    mavenCentral()
    mavenLocal()
}



dependencies {
    "implementation"("ch.qos.logback:logback-classic:$logback_version")
    "implementation"("io.github.oshai:kotlin-logging-jvm:$oshai_logging_version")
    "implementation"("org.jetbrains.kotlinx:kotlinx-datetime:$kdatetime_version")
}

project.configure<org.gradle.api.publish.PublishingExtension> {
    publications {
        register("mavenJava", org.gradle.api.publish.maven.MavenPublication::class) {
            from(components["java"])
        }
    }
    repositories {
        mavenLocal()
    }
}

project.tasks.named("publishToMavenLocal").configure {
    dependsOn("assemble")
}

project.tasks.withType<Test> {
    useJUnitPlatform()
}


project.group = "fergusm"