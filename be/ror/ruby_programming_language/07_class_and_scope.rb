# 부모 클래스 (레일즈의 ApplicationRecord 같은 존재)
class Animal
  def breathe
    puts "숨을 쉽니다."
  end
end

# 상속 (< 기호 사용)
class Dog < Animal
  # Getter, Setter 자동 생성 (매우 중요!)
  attr_accessor :name

  def initialize(name)
    # @가 붙으면 '인스턴스 변수'입니다.
    # 클래스 내부 어디서든(다른 메서드에서도) 사용 가능합니다.
    # 레일즈에서는 컨트롤러의 @변수가 뷰(View)로 자동 전달됩니다.
    @name = name
  end

  def bark
    # @name은 initialize에서 설정했지만 여기서도 쓸 수 있음
    puts "#{@name}가 멍멍 짖습니다!"
  end
end

poppy = Dog.new("뽀삐")
poppy.breathe   # 부모 메서드 사용
poppy.bark      # 본인 메서드 사용
poppy.name = "초코" # attr_accessor 덕분에 밖에서도 수정 가능
poppy.bark
