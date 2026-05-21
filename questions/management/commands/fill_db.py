import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count
from faker import Faker
from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker('ru_RU')

BATCH_SIZE = 5000


def log(msg):
    print(msg, flush=True)


class Command(BaseCommand):
    help = 'Наполнение базы данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']

        log('Создание пользователей...')
        users = self._create_users(ratio)

        log('Создание тегов...')
        tags = self._create_tags(ratio)

        log('Создание вопросов...')
        questions = self._create_questions(ratio, users, tags)

        log('Создание ответов...')
        self._create_answers(ratio, users, questions)

        log('Создание лайков...')
        self._create_likes(ratio, users, questions)

        log('Пересчёт рейтингов...')
        self._recalculate_ratings()

        self.stdout.write(self.style.SUCCESS(f'Готово (ratio={ratio})'))

    def _create_users(self, ratio):
        existing_count = User.objects.count()
        to_create = ratio - existing_count
        if to_create <= 0:
            return list(User.objects.values_list('id', flat=True))

        usernames = set(User.objects.values_list('username', flat=True))
        users = []
        for i in range(to_create):
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
            if (i + 1) % 1000 == 0:
                log(f'  пользователи: {i + 1} из {to_create}')

        for i in range(0, len(users), BATCH_SIZE):
            User.objects.bulk_create(users[i:i + BATCH_SIZE], ignore_conflicts=True)

        all_user_ids = list(User.objects.values_list('id', flat=True))

        existing_profile_ids = set(Profile.objects.values_list('user_id', flat=True))
        profiles = [Profile(user_id=uid) for uid in all_user_ids if uid not in existing_profile_ids]
        for i in range(0, len(profiles), BATCH_SIZE):
            Profile.objects.bulk_create(profiles[i:i + BATCH_SIZE], ignore_conflicts=True)

        return all_user_ids

    def _create_tags(self, ratio):
        existing_tags = set(Tag.objects.values_list('name', flat=True))
        to_create = ratio - len(existing_tags)
        if to_create <= 0:
            return list(Tag.objects.values_list('id', flat=True))

        new_tags = []
        for _ in range(to_create):
            name = fake.word().lower() + str(random.randint(100, 9999))
            while name in existing_tags or not name.replace('-', '').isalnum():
                name = fake.word().lower() + str(random.randint(100, 9999))
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

        questions = []
        for i in range(to_create):
            questions.append(Question(
                title=fake.sentence(nb_words=8)[:255],
                content=fake.text(max_nb_chars=1000),
                author_id=random.choice(user_ids),
            ))
            if (i + 1) % 10000 == 0:
                log(f'  вопросы: {i + 1} из {to_create}')

        created_ids = []
        for i in range(0, len(questions), BATCH_SIZE):
            batch = Question.objects.bulk_create(questions[i:i + BATCH_SIZE])
            created_ids.extend(q.id for q in batch)

        ThroughModel = Question.tags.through
        through_objects = []
        for qid in created_ids:
            for tid in random.sample(tag_ids, min(3, len(tag_ids))):
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

        answers = []
        for i in range(to_create):
            answers.append(Answer(
                question_id=random.choice(question_ids),
                author_id=random.choice(user_ids),
                content=fake.text(max_nb_chars=500),
                is_correct=random.random() < 0.1,
            ))
            if (i + 1) % 10000 == 0:
                log(f'  ответы: {i + 1} из {to_create}')

        answer_counts = {}
        for i in range(0, len(answers), BATCH_SIZE):
            batch = Answer.objects.bulk_create(answers[i:i + BATCH_SIZE])
            for a in batch:
                answer_counts[a.question_id] = answer_counts.get(a.question_id, 0) + 1

        questions_to_update = [Question(id=qid, answers_count=cnt) for qid, cnt in answer_counts.items()]
        for i in range(0, len(questions_to_update), BATCH_SIZE):
            Question.objects.bulk_update(questions_to_update[i:i + BATCH_SIZE], ['answers_count'])

    def _create_likes(self, ratio, user_ids, question_ids):
        total = ratio * 200
        half = total // 2

        existing_qlikes = set(QuestionLike.objects.values_list('question_id', 'user_id'))
        qlikes = []
        attempts = 0
        while len(qlikes) < half and attempts < half * 3:
            attempts += 1
            pair = (random.choice(question_ids), random.choice(user_ids))
            if pair not in existing_qlikes:
                existing_qlikes.add(pair)
                qlikes.append(QuestionLike(question_id=pair[0], user_id=pair[1]))
            if (len(qlikes)) % 10000 == 0 and len(qlikes) > 0:
                log(f'  лайки вопросов: {len(qlikes)} из {half}')

        for i in range(0, len(qlikes), BATCH_SIZE):
            QuestionLike.objects.bulk_create(qlikes[i:i + BATCH_SIZE], ignore_conflicts=True)

        answer_ids = list(Answer.objects.values_list('id', flat=True))
        if not answer_ids:
            return

        existing_alikes = set(AnswerLike.objects.values_list('answer_id', 'user_id'))
        alikes = []
        attempts = 0
        while len(alikes) < half and attempts < half * 3:
            attempts += 1
            pair = (random.choice(answer_ids), random.choice(user_ids))
            if pair not in existing_alikes:
                existing_alikes.add(pair)
                alikes.append(AnswerLike(answer_id=pair[0], user_id=pair[1]))
            if (len(alikes)) % 10000 == 0 and len(alikes) > 0:
                log(f'  лайки ответов: {len(alikes)} из {half}')

        for i in range(0, len(alikes), BATCH_SIZE):
            AnswerLike.objects.bulk_create(alikes[i:i + BATCH_SIZE], ignore_conflicts=True)

    def _recalculate_ratings(self):
        questions = list(
            Question.objects.annotate(like_count=Count('likes', distinct=True))
        )
        for q in questions:
            q.rating = q.like_count
        for i in range(0, len(questions), BATCH_SIZE):
            Question.objects.bulk_update(questions[i:i + BATCH_SIZE], ['rating'])
        log(f'  рейтинги вопросов пересчитаны: {len(questions)}')

        answers = list(
            Answer.objects.annotate(like_count=Count('likes', distinct=True))
        )
        for a in answers:
            a.rating = a.like_count
        for i in range(0, len(answers), BATCH_SIZE):
            Answer.objects.bulk_update(answers[i:i + BATCH_SIZE], ['rating'])
        log(f'  рейтинги ответов пересчитаны: {len(answers)}')
