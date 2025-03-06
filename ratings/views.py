from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Professor, Module, ModuleInstance, Rating
from .serializers import ProfessorSerializer, ModuleSerializer, ModuleInstanceSerializer, RatingSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Avg
import json

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600' 
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'  
        return response

class ModuleInstanceViewSet(viewsets.ModelViewSet):
    queryset = ModuleInstance.objects.all()
    serializer_class = ModuleInstanceSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'  
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600' 
        return response

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate' 
        return response

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        User.objects.create_user(username=username, email=email, password=password)
        return Response({'status': 'success', 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the token from the request
            token = request.auth
            if token:
                # Delete the token to invalidate it
                token.delete()
            return Response({'status': 'success', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RateProfessorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        professor_id = data.get('professor_id')
        user_name = data.get('user_name')
        module_code = data.get('module_code')
        rating_value = data.get('rating')
        semester = data.get('semester')

        try:
            professor = Professor.objects.get(id=professor_id)
            user = User.objects.get(username=user_name)
            module = Module.objects.get(code=module_code)
            module_instance = ModuleInstance.objects.get(module=module, semester=semester)

            # Check if the professor is associated with the module instance
            if not module_instance.professors.filter(id=professor_id).exists():
                return Response({'status': 'error', 'message': 'Professor is not teaching this module instance'}, status=status.HTTP_400_BAD_REQUEST)

            # Create or update the rating
            rating, created = Rating.objects.update_or_create(
                professor=professor,
                user=user,
                module_instance=module_instance,
                defaults={'rating': rating_value}
            )

            if created:
                message = "Rating added"
            else:
                message = "Rating updated"

            return Response({'status': 'success', 'message': message, 'rating_id': rating.id}, status=status.HTTP_200_OK)
        except Professor.DoesNotExist:
            return Response({'status': 'error', 'message': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ModuleInstance.DoesNotExist:
            return Response({'status': 'error', 'message': 'Module instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'status': 'error', 'message': 'You have already rated this professor for this module instance'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListModulesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            module_instances = ModuleInstance.objects.all()
            result = []

            for instance in module_instances:
                professors = instance.professors.all()  # Assuming a ManyToManyField relationship
                professor_names = ', '.join([f"Professor {prof.name} ({prof.id})" for prof in professors])
                result.append({
                    'code': instance.module.code,
                    'name': instance.module.name,
                    'year': instance.year,
                    'semester': instance.semester,
                    'taught_by': professor_names
                })

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AverageRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        professor_id = data.get('professor_id')
        module_code = data.get('module_code')

        if not professor_id or not module_code:
            return Response({'status': 'error', 'message': 'Professor ID and Module ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            professor = Professor.objects.get(id=professor_id)
            module = Module.objects.get(code=module_code)
        except Professor.DoesNotExist:
            return Response({'status': 'error', 'message': 'Professor not found'}, status=status.HTTP_404_NOT_FOUND)
        except Module.DoesNotExist:
            return Response({'status': 'error', 'message': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter ratings by professor and module
        ratings = Rating.objects.filter(professor=professor, module_instance__module=module)
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg']

        return Response({
            'status': 'success',
            'average_rating': average_rating,
            'module_name': module.name,
            'professor_name': professor.name
        }, status=status.HTTP_200_OK)


class RatingsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            professors = Professor.objects.all()
            result = []

            for professor in professors:
                average_rating = professor.average_rating
                stars = '★' * round(average_rating) if average_rating else 'no ratings'
                result.append(f"The rating of Professor {professor.name} ({professor.id}) is {stars}")

            return Response({'status': 'success', 'ratings': result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)