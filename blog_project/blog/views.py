from django.shortcuts import render,get_object_or_404
from blog.models import Post
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from blog.forms import CommentForm
from taggit.models import Tag

# Create your views here.
def Post_View(request,tag_slug=None):
    post_list=Post.objects.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        post_list=post_list.filter(tags__in=[tag])
    paginator=Paginator(post_list,3)
    page_number=request.GET.get('page')
    try:
        post_list=paginator.page(page_number)
    except PageNotAnInteger:
        post_list=paginator.page(1)
    except EmptyPage:
        post_list=paginator.page(paginator.num_pages)
    return render(request,'blog/post_list.html',{'post_list':post_list,'tag':tag})

#by using class based view
'''class PostView(ListView):
    model=Post
    pagiate_by=1
'''
def Post_Detail_View(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post,status='published',
                           publish__year=year,
                           publish__month=month,
                           publish__day=day
                           )
    comments=post.comments.filter(active=True)
    csubmit=False
    if request.method=='POST':
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.post=post
            new_comment.save()
            csubmit=True

    else:
        form=CommentForm()
    return render(request,'blog/post_detail.html',{'form':form,'post':post,'csubmit':csubmit})


from django.core.mail import send_mail
from blog.forms import EmailSendForm

def MailSendView(request,id):
    post=get_object_or_404(Post,id=id,status='published')
    sent=False
    if request.method=='POST':
        form=EmailSendForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            subject="{}({}) recommands you to read'{}'".format(cd['name'],cd['email'],post.title)
            post_url=request.build_absolute_uri(post.get_absolute_url())
            message="Read posts at: \n{}\n\n{}\'s comments:\n{}".format('url',cd['name'],cd['comments'])
            send_mail('subject','message','sridhar@blog.com',[cd['to']])
            sent=True
    else:
        form=EmailSendForm()
    return render(request,'blog/sharebymail.html',{'form':form,'post':post,'sent':sent})

