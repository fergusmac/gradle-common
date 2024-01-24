apply(plugin = "maven-publish")
apply(plugin = "java")


project.repositories {
    mavenCentral()
    mavenLocal()
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