from rest_framework import viewsets
from .models import Professor, Module, ModuleInstance, Rating
from .serializers import ProfessorSerializer, ModuleSerializer, ModuleInstanceSerializer, RatingSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg
from django.db import IntegrityError
import json

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class ModuleInstanceViewSet(viewsets.ModelViewSet):
    queryset = ModuleInstance.objects.all()
    serializer_class = ModuleInstanceSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

@csrf_exempt
def rate_professor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
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
                return JsonResponse({'status': 'error', 'message': 'Professor is not teaching this module instance'})

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

            return JsonResponse({'status': 'success', 'message': message, 'rating_id': rating.id})
        except Professor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Professor not found'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
        except ModuleInstance.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Module instance not found'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'You have already rated this professor for this module instance'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def list(request):
    try:
        module_instances = ModuleInstance.objects.all()
        result = []

        for instance in module_instances:
            professors = instance.professors.all()  # Assuming a ManyToManyField relationship
            professor_names = ' ,'.join([f" Professor {prof.name} ({prof.id})" for prof in professors])
            result.append({
                'code': instance.module.code,
                'name': instance.module.name,
                'year': instance.year,
                'semester': instance.semester,
                'taught_by': professor_names
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists'})
        
        User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'status': 'success', 'message': 'User registered successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'message': 'Logged in successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def average_rating(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        professor_id = data.get('professor_id')
        module_code = data.get('module_code')

        if not professor_id or not module_code:
            return JsonResponse({'status': 'error', 'message': 'Professor ID and Module ID are required'})

        try:
            professor = Professor.objects.get(id=professor_id)
            module = Module.objects.get(code=module_code)
        except Professor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Professor not found'})
        except Module.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Module not found'})

        return JsonResponse({
            'status': 'success',
            'average_rating': professor.average_rating,
            'module_name': module.name,
            'professor_name': professor.name
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def ratings_list(request):
    try:
        professors = Professor.objects.all()
        result = []

        for professor in professors:
            average_rating = professor.average_rating
            stars = '★' * round(average_rating) if average_rating else 'no ratings'
            result.append(f"The rating of Professor {professor.name} ({professor.id}) is {stars}")

        return JsonResponse({'status': 'success', 'ratings': result}, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)