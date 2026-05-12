from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'content', 'is_correct', 'rating', 'created_at')
    readonly_fields = ('created_at',)
    raw_id_fields = ('author',)
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'answers_count', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'tags')
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'answers_count')
    inlines = [AnswerInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'is_correct', 'rating', 'created_at')
    search_fields = ('content', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at')
    raw_id_fields = ('question', 'author')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'question')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('question', 'user')
    search_fields = ('user__username', 'question__title')
    list_filter = ()
    raw_id_fields = ('question', 'user')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user')
    search_fields = ('user__username',)
    list_filter = ()
    raw_id_fields = ('answer', 'user')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'answer')
