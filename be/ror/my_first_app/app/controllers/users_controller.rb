  class UsersController < ApplicationController
    def index
      # 사용자 목록 페이지 로직
     @users = User.all
    end
  end
