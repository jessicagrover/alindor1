from django.db import models

class Candidate(models.Model):
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True)
    # Other fields such as candidate name, email, etc.

    def __str__(self):
        return f"Candidate with CV at {self.cv_file.url}"

class JobDescription(models.Model):
    job_file = models.FileField(upload_to='job_descriptions/', blank=True, null=True)
    # Other fields such as job title, department, etc.

    def __str__(self):
        return f"Job description at {self.job_file.url}"

