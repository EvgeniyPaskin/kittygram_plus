import datetime as dt
from rest_framework import serializers
from .models import Cat, Owner, Achievement, AchievementCat, CHOICES


class CatListSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    # Теперь поле примет только значение, упомянутое в списке CHOICES
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner',
                  'achievements', 'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        # Если в исходном запросе не было поля achievements
        if 'achievements' not in self.initial_data:
            # То создаём запись о котике без его достижений
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            # Иначе сначала добавляем котика в БД
            cat = Cat.objects.create(**validated_data)
            # А потом добавляем его достижения в БД
            for achievement in achievements:
                current_achievement, status = Achievement.objects \
                                                         .get_or_create(
                                                          **achievement)
                # И связываем каждое достижение с этим котиком
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
            return cat


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')
