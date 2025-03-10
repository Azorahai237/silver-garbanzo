from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.core.exceptions import ValidationError

class Professor(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    average_rating = models.FloatField(default=0.0) 
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Module(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    professors = models.ManyToManyField(Professor)  
    year = models.IntegerField()
    semester = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('module', 'year', 'semester'),)  
    
    def __str__(self):
        return f"{self.module.name} ({self.year}, Semester {self.semester})"

class Rating(models.Model):
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('module_instance', 'professor', 'user'),)  

    def __str__(self):
        return f"{self.professor.name}: {self.rating} stars"

    def save(self, *args, **kwargs):
        if not self.module_instance.professors.filter(id=self.professor.id).exists():
            raise ValidationError("Professor is not teaching this module instance")
        super().save(*args, **kwargs)
        self.update_professor_average_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_professor_average_rating()

    def update_professor_average_rating(self):
        ratings = Rating.objects.filter(professor=self.professor)
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        self.professor.average_rating = average_rating
        self.professor.save()
