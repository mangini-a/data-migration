from django.db import models

class QuizData(models.Model):
    # Add fields matching your MySQL structure
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'quiz_data'      # Specify the table name in PostgreSQL
