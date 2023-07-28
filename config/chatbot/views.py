from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decouple import config
import openai

from .models import Conversation
from .serializers import ConversationSerializer

openai.api_key = config('OPENAI_API_KEY')


class ChatbotView(APIView):
    def get(self, request, *args, **kwargs):
        conversations = request.session.get('conversations', [])
        return Response({'conversations': conversations})

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        if prompt:
            # 이전 대화 기록 가져오기
            session_conversations = request.session.get('conversations', [])
            previous_conversations = "\n".join([f"User: {c['prompt']}\nAI: {c['response']}" for c in session_conversations])
            prompt_with_previous = f"{previous_conversations}\nUser: {prompt}\nAI:"

            model_engine = "text-davinci-003"
            completions = openai.Completion.create(
                # OpenAI 모델
                engine=model_engine,
                # 현재 사용자의 입력과 이전 대화 기록을 모두 포함
                prompt=prompt_with_previous,
                # 응답의 최대 길이
                max_tokens=1024,
                # 응답 개수
                n=5,
                # API가 추가 토큰 생성을 중지해야 하는 일련의 시퀀스를 지정하는 선택적 매개변수(지정하지 않을 경우 모델이 정지하기에 가장 좋은 위치를 결정)
                stop=None,
                # 응답의 무작위성 값이 낮을수록 출력에 집중하며, 높을수록 무작위 답변
                temperature=0.5,
            )
            response = completions.choices[0].text.strip()

            conversation = Conversation(prompt=prompt, response=response)
            conversation.save()

            # 대화 기록에 새로운 응답 추가
            session_conversations.append({'prompt': prompt, 'response': response})
            request.session['conversations'] = session_conversations
            request.session.modified = True

        return self.get(request, *args, **kwargs)


class ConversationList(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 필요

    def get_queryset(self):
        # 현재 로그인한 사용자의 대화만 반환
        return Conversation.objects.filter(user=self.request.user)


class ConversationDetail(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 필요

    def get_queryset(self):
        # 현재 로그인한 사용자의 대화만 반환
        return Conversation.objects.filter(user=self.request.user)


class ConversationDelete(DestroyAPIView):
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 필요

    def get_queryset(self):
        # 현재 로그인한 사용자의 대화만 반환
        return Conversation.objects.filter(user=self.request.user)


ChatbotView = ChatbotView.as_view()
ConversationList = ConversationList.as_view()
ConversationDetail = ConversationDetail.as_view()
ConversationDelete = ConversationDelete.as_view()