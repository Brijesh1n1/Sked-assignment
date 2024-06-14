from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.db.models import Sum
from .managers import UserManager


class CustomUser(AbstractBaseUser):
    username = models.CharField(verbose_name="Username", unique=True, max_length=30, null=True, blank=True)
    email = models.EmailField(verbose_name="Email", unique=True, max_length=255)
    is_active = models.BooleanField(verbose_name="Active", default=True)
    is_staff = models.BooleanField(verbose_name="Staff", default=False)
    registered_at = models.DateTimeField(verbose_name="Registered at", auto_now_add=timezone.now)
    is_email_verified = models.BooleanField(default=False)
    # Fields settings
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    objects = UserManager()
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Document(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title", blank=True)
    html_file_name = models.CharField(verbose_name="HTML file name", blank=True, max_length=100)
    doc_file = models.FileField(upload_to='documents/', blank=True)
    child = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class UserSpentTime(models.Model):
    user = models.ForeignKey(CustomUser, null = True, on_delete = models.CASCADE, related_name="usertimespent")
    minutes = models.IntegerField(default=0)
    seconds = models.IntegerField(default=0)
    hours = models.IntegerField(default=0)


class Recognition(models.Model):
    doc_file = models.ImageField(upload_to='recognize/', blank=True)


class ExpenseBill(models.Model):
    tip = models.FloatField(default=0)
    prime_contributer = models.ForeignKey(CustomUser, related_name="contributer",
                                          on_delete=models.CASCADE)
    description = models.CharField(max_length=120, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    total_spends = models.FloatField(blank=True, null=True)

    def get_borrowed_amount(self, user):
        total_debt = 0
        bills = self.bill_item.filter(holders = user)
        for bill in bills:
            holders = bill.holders.count()
            temp_debt = (bill.final_amount)//holders
            total_debt += temp_debt
        return total_debt
    
    def amount_owed_by_friend(self, friend):
        bills = self.bill_item.filter(holders = friend)
        amount_given = 0
        for bill in bills:
            holders = bill.holders.count()            
            amount_given += bill.final_amount//holders
        return amount_given


class BillItem(models.Model):
    bill = models.ForeignKey(ExpenseBill, related_name='bill_item', on_delete=models.CASCADE)
    item = models.CharField(max_length=120, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    holders = models.ManyToManyField(CustomUser, blank=True, related_name="holder")
    tax = models.FloatField(blank=True, null=True)
    final_amount = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        amount = self.price + (self.price*self.tax/100)
        self.final_amount = amount
        return super().save(*args, **kwargs)

