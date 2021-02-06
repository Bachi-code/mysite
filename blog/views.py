from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
from django.urls import reverse_lazy
from .forms import CommentForm


def index(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'index.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    ordering = ['-date']
    paginate_by = 6


class UserPostListView(ListView):
    model = Post
    template_name = 'user_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date')


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = "post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = "post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True

        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "post_conf_delete.html"
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True

        return False


def about(request):
    return render(request, 'about.html', {'title': 'About'})


def latest(request):
    context = {
        'posts': Post.objects.filter().order_by('-date')[0]
    }
    return render(request, 'latest.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']
    template_name = "add_comment_to_post.html"

    def form_valid(self, form):
        post = Post.objects.get(id=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "comment_conf_delete.html"

    def get_success_url(self, **kwargs):
        return reverse_lazy('post-detail', kwargs={'pk': self.kwargs['pk1']})

    def get_object(self, **kwargs):
        object2 = get_object_or_404(Comment, id=self.kwargs['pk2'])
        return object2

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True

        return False
