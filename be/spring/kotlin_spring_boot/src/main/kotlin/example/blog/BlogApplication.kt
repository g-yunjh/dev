package example.blog

import org.springframework.boot.Banner
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.boot.runApplication

@SpringBootApplication
@EnableConfigurationProperties(BlogProperties::class)
class BlogApplication

fun main(args: Array<String>) {
    runApplication<BlogApplication>(*args) {
        setBannerMode(Banner.Mode.OFF) // 애플리케이션 사용자 정의 (배너 제거)
    }
}
