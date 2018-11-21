from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from boards.models import Board, Topic, Post
from django.contrib.auth.models import User
from boards.forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, id):
    # board = Board.objects.get(pk=id)
    board = get_object_or_404(Board, pk=id)
    topics = board.topics.order_by(
        '-last_updated').annotate(replies=Count('posts')-1)
    return render(request, 'topics.html', {'board': board, 'topics': topics})


@login_required
def new_topic(request, id):
    board = get_object_or_404(Board, pk=id)
    user = User.objects.first()
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )

            return redirect('topic_posts', pk=id, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = Topic.objects.get(board__pk=pk, pk=topic_pk)
    # topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk, board__pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        post = form.save(commit=False)
        post.topic = topic
        post.created_by = request.user
        post.save()
        return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})
