from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from .serializers import *
from .models import CustomUser

class ExpenseManageView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExpenseManagerSerializer
    queryset = ExpenseBill.objects.all()


class MyExpenseAPIView(APIView):
    def get(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        bill_items = BillItem.objects.filter(holders = user)
        debt_bills = bill_items.exclude(bill__prime_contributer=user)
        you_owe_to = {}
        total_debt = 0
        for bills in debt_bills:
            holders = bills.holders.count()
            temp_debt = (bills.final_amount)//holders
            due_to = bills.bill.prime_contributer.email
            if due_to in you_owe_to:
                you_owe_to[due_to] += temp_debt
            else:
                you_owe_to[due_to] = temp_debt
            total_debt += temp_debt
        
        given_to = bill_items.filter(bill__prime_contributer=user)
        amount_given = 0
        who_owed_you = {}
        for bills in given_to:
            holders = bills.holders.count()
            for owed_user in bills.holders.all():
                if owed_user == user:
                    continue
                amount_given += bills.final_amount//holders
                if owed_user.email in who_owed_you:
                    who_owed_you[owed_user.email] += bills.final_amount//holders
                else:
                    who_owed_you[owed_user.email] = bills.final_amount//holders
        
        return Response(
            {
                "Total Balance": amount_given-total_debt,
                "Total You are Owed": amount_given or 0,
                "Totol You Owe": total_debt or 0,
                "You Owe To":you_owe_to or "No One",
                "Owed To You": who_owed_you or "No One",
            },
             status=status.HTTP_200_OK
            )
    
class ListFreindsExpenseView(APIView):
    def get(self, request, pk):
        friend_id = request.GET.get('friend')
        user = CustomUser.objects.get(id=pk)
        friend = CustomUser.objects.get(id=friend_id)
        bill_items = ExpenseBill.objects.filter(bill_item__holders = friend).distinct()
        expense = []
        for bill in bill_items:
            temp_bill = {}
            temp_bill['id'] = bill.id
            temp_bill['date'] = bill.date.date()
            temp_bill['description'] = bill.description
            temp_bill['Paid By'] = bill.prime_contributer.email
            if bill.prime_contributer != user:
                temp_bill['Total You borrowed'] = bill.get_borrowed_amount(user)
            else:
                temp_bill['Total Owed To You'] = bill.amount_owed_by_friend(friend)
            expense.append(temp_bill)
        return Response({'Expense':expense}, status=status.HTTP_200_OK)


