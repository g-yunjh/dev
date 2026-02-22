# 1. 심볼 (Symbol) : 이름표
# 문자열("name")과 다르게 메모리를 딱 한 번만 차지합니다.
# 레일즈에서는 키(Key)값으로 문자열 대신 심볼을 씁니다.
puts :status.object_id
puts :status.object_id  # 위와 같은 ID 출력 (메모리 효율적)

# 2. 해시 (Hash) : 딕셔너리
# 옛날 방식 (Rocket syntax) - 잘 안 씀
user_old = { :name => "철수", :age => 30 }

# ★ 최신 방식 (JSON 스타일) - 레일즈에서 매일 보게 될 문법
user = {
  name: "영희",
  age: 25,
  email: "yh@example.com"
}

# 값 꺼내기 (반드시 심볼로 접근해야 함!)
puts user[:name]   # "영희"
puts user["name"]  # nil (문자열로는 못 찾음)

# 3. 해시를 함수의 인자로 넘기기 (옵션 해시)
# 레일즈 메서드들은 이렇게 마지막 인자로 해시를 받는 경우가 많습니다. -> 강제성 떄문에 위치 인자가 필요하긴 함 (필수 값 방어)
def create_link(text, options = {})
  puts "링크생성: #{text}, 클래스: #{options[:class]}, 타겟: #{options[:target]}"
end

# 호출할 때 중괄호 {} 생략 가능 (이게 레일즈 코드처럼 보이는 이유)
create_link "홈으로", class: "btn-primary", target: "_blank"
