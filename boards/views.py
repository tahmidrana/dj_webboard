from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from boards.models import Board, Topic, Post
from django.contrib.auth.models import User
from boards.forms import NewTopicForm
from django.contrib.auth.decorators import login_required


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, id):
    #board = Board.objects.get(pk=id)
    board = get_object_or_404(Board, pk=id)

    return render(request, 'topics.html', {'board': board})


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

            return redirect('board_topics', id=board.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = Topic.objects.get(board__pk=pk, pk=topic_pk)
    #topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    return render(request, 'topic_posts.html', {'topic': topic})
