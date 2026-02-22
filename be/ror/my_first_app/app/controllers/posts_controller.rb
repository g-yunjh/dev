   # app/controllers/posts_controller.rb
   class PostsController < ApplicationController
       # 게시글 목록을 보여주는 액션
     def index
        @posts = Post.all
     end

     # 특정 게시글 상세 정보를 보여주는 액션
     def show
       @post = Post.find(params[:id])
     end

     # 새로운 게시글 작성 폼을 보여주는 액션
     def new
         @post = Post.new
     end
       # 새로운 게시글 생성하는 액션
      def create
           @post = Post.new(params[:post].permit(:title,:content))
             if @post.save
               redirect_to @post
             else
               render 'new'
             end
       end

       # 특정 게시글 수정 폼을 보여주는 액션
     def edit
         @post = Post.find(params[:id])
     end
      # 특정 게시글 수정하는 액션
       def update
           @post = Post.find(params[:id])
           if @post.update(params[:post].permit(:title, :content))
               redirect_to @post
           else
               render 'edit'
           end
       end
       # 특정 게시글 삭제하는 액션
       def destroy
         @post = Post.find(params[:id])
         @post.destroy
         redirect_to posts_path
       end
   end
