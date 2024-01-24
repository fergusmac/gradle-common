apply(plugin = "maven-publish")
apply(plugin = "java")

val logback_version = "1.4.11"

project.repositories {
    mavenCentral()
    mavenLocal()
}

dependencies {
    implementation("ch.qos.logback:logback-classic:$logback_version")
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