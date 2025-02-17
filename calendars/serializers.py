from rest_framework import serializers

from .models import Calendar, Subscription


class CalendarCreateSerializer(serializers.ModelSerializer):
    """
    캘린더 생성용 Serializer (초대 코드 포함)
    """

    class Meta:
        model = Calendar
        fields = [
            # "calendar_id",
            "name",
            "description",
            "is_public",
            "color",
            "admins",
        ]
        # exclude = ['calendar_id']  # 생성 시 캘린더 ID 제외

    def to_representation(self, instance):
        """
        사용자 권한에 따라 invitation_code를 동적으로 제외
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # 관리자 권한이 없는 경우 초대 코드 제거
        if request and not instance.has_admin_permission(request.user):
            representation.pop("invitation_code", None)

        return representation

    def create(self, validated_data):
        # 요청 사용자로 creator 설정
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


class CalendarSearchResultSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ["name", "creator_nickname", "is_subscribed"]

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return Subscription.objects.filter(user=user, calendar=obj).exists()


class CalendarDetailSerializer(serializers.ModelSerializer):
    """
    캘린더 조회용 Serializer (초대 코드 제외)
    """

    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)

    class Meta:
        model = Calendar
        fields = [
            "calendar_id",
            "name",
            "description",
            "is_public",
            "color",
            "created_at",
            "creator",
            "creator_nickname",
            "invitation_code",
            "admins",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    구독 데이터를 직렬화하는 Serializer
    """

    calendar_id = serializers.IntegerField(write_only=True)  # 구독 생성 시 사용
    name = serializers.CharField(source="calendar.name", read_only=True)
    description = serializers.CharField(source="calendar.description", read_only=True)
    is_public = serializers.BooleanField(source="calendar.is_public", read_only=True)
    color = serializers.CharField(source="calendar.color", read_only=True)
    creator = serializers.IntegerField(source="calendar.creator.id", read_only=True)
    creator_nickname = serializers.CharField(
        source="calendar.creator.nickname", read_only=True
    )
    invitation_code = serializers.CharField(
        source="calendar.invitation_code", read_only=True
    )
    admins = serializers.PrimaryKeyRelatedField(
        source="calendar.admins", many=True, read_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "calendar_id",  # calendar_id 필드 추가
            "name",
            "description",
            "is_public",
            "color",
            "created_at",
            "creator",
            "creator_nickname",
            "invitation_code",
            "admins",
        ]
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        calendar_id = validated_data.pop("calendar_id")
        user = self.context["request"].user

        # Calendar 객체 가져오기
        try:
            calendar = Calendar.objects.get(calendar_id=calendar_id)
        except Calendar.DoesNotExist:
            raise serializers.ValidationError("캘린더를 찾을 수 없습니다.")

        # validated_data에서 user 제거
        validated_data.pop("user", None)

        # 구독 생성
        subscription = Subscription.objects.create(
            user=user, calendar=calendar, **validated_data
        )
        return subscription

    def update(self, instance, validated_data):
        """
        구독 데이터 업데이트 (is_active, is_on_calendar 상태 변경)
        """
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_on_calendar = validated_data.get(
            "is_on_calendar", instance.is_on_calendar
        )
        instance.save()
        return instance


class AdminInvitationSerializer(serializers.Serializer):
    """
    관리자 초대 코드 처리 Serializer
    """

    invitation_code = serializers.CharField(
        max_length=255, help_text="초대 코드", write_only=True
    )
    calendar = CalendarCreateSerializer(read_only=True)

    def validate_invitation_code(self, value):
        """
        초대 코드를 검증하여 캘린더를 확인
        """
        try:
            calendar = Calendar.objects.get(invitation_code=value)
        except Calendar.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 초대 코드입니다.")
        if self.context["request"].user in calendar.admins.all():
            raise serializers.ValidationError("이미 캘린더 관리자로 추가되었습니다.")
        self.calendar = calendar
        return value

    def save(self):
        """
        초대 코드를 사용해 사용자를 캘린더 관리자에 추가
        """
        user = self.context["request"].user  # 요청 사용자
        if not hasattr(self, "calendar"):
            raise serializers.ValidationError("초대 코드가 유효하지 않습니다.")
        self.calendar.admins.add(user)  # 관리자로 추가
        return self.calendar


class AdminCalendarSerializer(serializers.ModelSerializer):
    creator_id = serializers.IntegerField(source="creator.id", read_only=True)
    admin_members = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ["name", "creator_id", "admin_members"]

    def get_admin_members(self, obj):
        return list(obj.admins.values_list("nickname", flat=True))


class CalendarSearchSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ["calendar_id", "name", "creator_nickname", "is_subscribed"]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, calendar=obj).exists()
        return False


class UpdateCalendarActiveSerializer(serializers.Serializer):
    """
    캘린더 활성화 상태 업데이트를 위한 Serializer
    """

    calendar_id = serializers.IntegerField(required=True, help_text="캘린더 ID")
    is_active = serializers.BooleanField(required=True, help_text="활성화 상태")
