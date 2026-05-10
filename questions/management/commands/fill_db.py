import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker('ru_RU')

BATCH_SIZE = 5000


class Command(BaseCommand):
    help = 'Наполнение базы данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **options):
        ratio = options['ratio']

        self.stdout.write('Создание пользователей...')
        users = self._create_users(ratio)

        self.stdout.write('Создание тегов...')
        tags = self._create_tags(ratio)

        self.stdout.write('Создание вопросов...')
        questions = self._create_questions(ratio, users, tags)

        self.stdout.write('Создание ответов...')
        self._create_answers(ratio, users, questions)

        self.stdout.write('Создание лайков...')
        self._create_likes(ratio, users, questions)

        self.stdout.write(self.style.SUCCESS(f'База данных успешно заполнена (ratio={ratio})'))

    def _create_users(self, ratio):
        existing_count = User.objects.count()
        users_to_create = ratio - existing_count
        if users_to_create <= 0:
            return list(User.objects.values_list('id', flat=True))

        users = []
        usernames = set(User.objects.values_list('username', flat=True))
        for _ in range(users_to_create):
            username = fake.user_name() + str(random.randint(1000, 9999))
            while username in usernames:
                username = fake.user_name() + str(random.randint(1000, 9999))
            usernames.add(username)
            users.append(User(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            ))

        for i in range(0, len(users), BATCH_SIZE):
            User.objects.bulk_create(users[i:i + BATCH_SIZE], ignore_conflicts=True)

        all_user_ids = list(User.objects.values_list('id', flat=True))

        existing_profile_ids = set(Profile.objects.values_list('user_id', flat=True))
        profiles = [
            Profile(user_id=uid)
            for uid in all_user_ids
            if uid not in existing_profile_ids
        ]
        for i in range(0, len(profiles), BATCH_SIZE):
            Profile.objects.bulk_create(profiles[i:i + BATCH_SIZE], ignore_conflicts=True)

        return all_user_ids

    def _create_tags(self, ratio):
        existing_tags = set(Tag.objects.values_list('name', flat=True))
        tags_to_create = ratio - len(existing_tags)
        if tags_to_create <= 0:
            return list(Tag.objects.values_list('id', flat=True))

        new_tags = []
        for _ in range(tags_to_create):
            name = fake.word() + str(random.randint(100, 9999))
            while name in existing_tags:
                name = fake.word() + str(random.randint(100, 9999))
            existing_tags.add(name)
            new_tags.append(Tag(name=name))

        for i in range(0, len(new_tags), BATCH_SIZE):
            Tag.objects.bulk_create(new_tags[i:i + BATCH_SIZE], ignore_conflicts=True)

        return list(Tag.objects.values_list('id', flat=True))

    def _create_questions(self, ratio, user_ids, tag_ids):
        target = ratio * 10
        existing = Question.objects.count()
        to_create = target - existing
        if to_create <= 0:
            return list(Question.objects.values_list('id', flat=True))

        questions = [
            Question(
                title=fake.sentence(nb_words=8)[:255],
                content=fake.text(max_nb_chars=1000),
                author_id=random.choice(user_ids),
                rating=random.randint(-10, 100),
            )
            for _ in range(to_create)
        ]

        created_ids = []
        for i in range(0, len(questions), BATCH_SIZE):
            batch = Question.objects.bulk_create(questions[i:i + BATCH_SIZE])
            created_ids.extend(q.id for q in batch)

        ThroughModel = Question.tags.through
        through_objects = []
        seen = set()
        for qid in created_ids:
            chosen = random.sample(tag_ids, min(3, len(tag_ids)))
            for tid in chosen:
                key = (qid, tid)
                if key not in seen:
                    seen.add(key)
                    through_objects.append(ThroughModel(question_id=qid, tag_id=tid))

        for i in range(0, len(through_objects), BATCH_SIZE):
            ThroughModel.objects.bulk_create(through_objects[i:i + BATCH_SIZE], ignore_conflicts=True)

        return list(Question.objects.values_list('id', flat=True))

    def _create_answers(self, ratio, user_ids, question_ids):
        target = ratio * 100
        existing = Answer.objects.count()
        to_create = target - existing
        if to_create <= 0:
            return

        answers = [
            Answer(
                question_id=random.choice(question_ids),
                author_id=random.choice(user_ids),
                content=fake.text(max_nb_chars=500),
                rating=random.randint(-5, 50),
                is_correct=random.random() < 0.1,
            )
            for _ in range(to_create)
        ]

        question_answer_counts = {}
        for i in range(0, len(answers), BATCH_SIZE):
            batch = Answer.objects.bulk_create(answers[i:i + BATCH_SIZE])
            for a in batch:
                question_answer_counts[a.question_id] = question_answer_counts.get(a.question_id, 0) + 1

        questions_to_update = []
        for qid, cnt in question_answer_counts.items():
            q = Question(id=qid)
            q.answers_count = cnt
            questions_to_update.append(q)

        for i in range(0, len(questions_to_update), BATCH_SIZE):
            Question.objects.bulk_update(questions_to_update[i:i + BATCH_SIZE], ['answers_count'])

    def _create_likes(self, ratio, user_ids, question_ids):
        total_likes = ratio * 200
        half = total_likes // 2

        answer_ids = list(Answer.objects.values_list('id', flat=True))

        existing_qlikes = set(QuestionLike.objects.values_list('question_id', 'user_id'))
        qlikes = []
        attempts = 0
        while len(qlikes) < half and attempts < half * 3:
            attempts += 1
            qid = random.choice(question_ids)
            uid = random.choice(user_ids)
            if (qid, uid) not in existing_qlikes:
                existing_qlikes.add((qid, uid))
                qlikes.append(QuestionLike(question_id=qid, user_id=uid))

        for i in range(0, len(qlikes), BATCH_SIZE):
            QuestionLike.objects.bulk_create(qlikes[i:i + BATCH_SIZE], ignore_conflicts=True)

        if not answer_ids:
            return

        existing_alikes = set(AnswerLike.objects.values_list('answer_id', 'user_id'))
        alikes = []
        attempts = 0
        while len(alikes) < half and attempts < half * 3:
            attempts += 1
            aid = random.choice(answer_ids)
            uid = random.choice(user_ids)
            if (aid, uid) not in existing_alikes:
                existing_alikes.add((aid, uid))
                alikes.append(AnswerLike(answer_id=aid, user_id=uid))

        for i in range(0, len(alikes), BATCH_SIZE):
            AnswerLike.objects.bulk_create(alikes[i:i + BATCH_SIZE], ignore_conflicts=True)
